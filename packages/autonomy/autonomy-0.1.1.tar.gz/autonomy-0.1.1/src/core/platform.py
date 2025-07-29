from __future__ import annotations

import os
from collections import OrderedDict
from typing import Any, Type

import requests
from langchain_community.embeddings import FakeEmbeddings
from mem0.client.main import MemoryClient as RemoteMemoryClient
from mem0.memory.main import Memory

from ..llm.openrouter import ModelSelector, OpenRouterClient
from ..tools.github import GitHubTools
from ..tools.slack import SlackTools
from .workflow import BaseWorkflow


class Mem0Client:  # pragma: no cover - uses real Mem0 backend
    """Repository-scoped memory backed by mem0."""

    def __init__(
        self, max_entries: int = 50, config: dict[str, Any] | None = None
    ) -> None:
        self.max_entries = max_entries
        self.store: dict[str, OrderedDict[str, str]] = {}
        self._id_map: dict[tuple[str, str], str] = {}
        default_config = {
            "embedder": {
                "provider": "langchain",
                "config": {"model": FakeEmbeddings(size=10)},
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "mem0",
                    "embedding_model_dims": 10,
                    "path": ":memory:",
                },
            },
            "llm": {"provider": "openai", "config": {"api_key": "sk-fake"}},
        }
        if os.getenv("MEM0_API_KEY"):
            self.backend = RemoteMemoryClient()
        else:
            self.backend = Memory.from_config(config or default_config)

    def _get_repo_store(self, repo: str) -> OrderedDict[str, str]:
        if repo not in self.store:
            self.store[repo] = OrderedDict()
        return self.store[repo]

    def search(self, query: str, filter_metadata: dict | None = None) -> str:
        """Return stored value filtered by repository."""
        repo = filter_metadata.get("repository") if filter_metadata else "default"
        mem_id = self._id_map.get((repo, query))
        if mem_id:
            try:
                result = self.backend.get(mem_id)
                return result.get("memory", "") if result else ""
            except Exception:
                pass
        return self.store.get(repo, {}).get(query, "")

    def add(self, data: dict[str, str]) -> bool:
        """Add data to repository-specific store with cleanup."""
        repository = data.pop("repository", "default")
        repo_store = self._get_repo_store(repository)
        for key, value in data.items():
            if len(repo_store) >= self.max_entries:
                old_key, _ = repo_store.popitem(last=False)
                old_id = self._id_map.pop((repository, old_key), None)
                if old_id:
                    try:
                        self.backend.delete(old_id)
                    except Exception:
                        pass
            res = self.backend.add(
                value,
                run_id=repository,
                metadata={"repository": repository, "key": key},
                infer=False,
            )
            mem_id = (
                res.get("results", [{}])[0].get("id") if isinstance(res, dict) else None
            )
            if mem_id:
                self._id_map[(repository, key)] = mem_id
            repo_store[key] = value
        return True


class CachedMem0Client:
    """Lazily initialize ``Mem0Client`` and cache search results."""

    def __init__(self) -> None:
        self._client: Mem0Client | None = None
        self._cache: dict[tuple[str, str], str] = {}

    @property
    def client(self) -> Mem0Client:
        if self._client is None:
            self._client = Mem0Client()
        return self._client

    @property
    def store(self) -> dict[str, OrderedDict[str, str]]:
        return self.client.store

    def search(self, query: str, filter_metadata: dict | None = None) -> str:
        repo = filter_metadata.get("repository") if filter_metadata else "default"
        key = (repo, query)
        if key in self._cache:
            return self._cache[key]
        result = self.client.search(query, filter_metadata)
        if result:
            self._cache[key] = result
        return result

    def add(self, data: dict[str, str]) -> bool:
        self._cache.clear()
        return self.client.add(data)


class AutonomyPlatform:
    """Shared foundation for all workflows."""

    _shared_session: requests.Session | None = None

    @classmethod
    def get_session(cls) -> requests.Session:
        """Return a shared requests session."""
        if cls._shared_session is None:
            cls._shared_session = requests.Session()
        return cls._shared_session

    def __init__(
        self,
        api_key: str | None = None,
        model_selector: ModelSelector | None = None,
        github_token: str | None = None,
        owner: str | None = None,
        repo: str | None = None,
        slack_token: str | None = None,
    ):
        self.memory = CachedMem0Client()
        self.llm = OpenRouterClient(api_key=api_key)
        self.model_selector = model_selector or ModelSelector()
        if github_token and owner and repo:
            from ..github.issue_manager import IssueManager

            manager = IssueManager(
                github_token,
                owner,
                repo,
                session=self.get_session(),
            )
            self.github = GitHubTools(manager)
        else:
            from ..github.issue_manager import IssueManager

            self.github = GitHubTools(
                IssueManager("", "", "", session=self.get_session())
            )

        if slack_token:
            from ..slack.bot import SlackBot

            self.slack = SlackTools(SlackBot(slack_token))
        else:
            from ..slack.bot import SlackBot

            self.slack = SlackTools(SlackBot(""))

    def create_workflow(self, workflow_class: Type[BaseWorkflow]) -> BaseWorkflow:
        kwargs = {
            "memory": self.memory,
            "llm": self.llm,
            "github": self.github,
            "slack": self.slack,
        }
        if "model_selector" in workflow_class.__init__.__code__.co_varnames:
            kwargs["model_selector"] = self.model_selector
        return workflow_class(**kwargs)
