from datetime import datetime, timedelta, timezone

from src.tasks.pinned_items import PinnedItemsStore
from src.tasks.task_manager import TaskManager


class DummyIssueManager:
    def __init__(self, issues):
        self._issues = issues
        self.updated = None
        self.state_update = None
        self.comment = None

    def list_issues(self, state="open"):
        return self._issues

    def update_issue_labels(self, issue_number, add_labels=None, remove_labels=None):
        self.updated = (issue_number, add_labels, remove_labels)
        return True

    def update_issue_state(self, issue_number, state):
        self.state_update = (issue_number, state)
        return True

    def add_comment(self, issue_number, comment):
        self.comment = (issue_number, comment)
        return True


def _make_issue(num, prio, days=0):
    return {
        "number": num,
        "title": f"Issue {num}",
        "labels": [{"name": prio}],
        "created_at": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),
    }


def test_get_next_task(monkeypatch, tmp_path):
    issues = [_make_issue(1, "priority-low", 5), _make_issue(2, "priority-high", 1)]
    dummy = DummyIssueManager(issues)
    tm = TaskManager.__new__(TaskManager)
    tm.issue_manager = dummy
    tm.pinned_store = PinnedItemsStore(config_dir=tmp_path)
    tm.project_id = "o/r"
    from src.tasks.ranking import RankingEngine

    tm.ranking = RankingEngine()
    issue = tm.get_next_task()
    assert issue["number"] == 2


def test_get_next_task_explain(monkeypatch, tmp_path):
    issues = [_make_issue(1, "priority-low", 0)]
    dummy = DummyIssueManager(issues)
    tm = TaskManager.__new__(TaskManager)
    tm.issue_manager = dummy
    tm.pinned_store = PinnedItemsStore(config_dir=tmp_path)
    tm.project_id = "o/r"
    from src.tasks.ranking import RankingEngine

    tm.ranking = RankingEngine()
    issue, breakdown = tm.get_next_task(explain=True)
    assert issue["number"] == 1
    assert breakdown["priority"] == 1
    assert "age_penalty" in breakdown


def test_update_task(monkeypatch):
    dummy = DummyIssueManager([])
    tm = TaskManager.__new__(TaskManager)
    tm.issue_manager = dummy
    from src.tasks.ranking import RankingEngine

    tm.ranking = RankingEngine()
    assert tm.update_task(3, status="in-progress", done=True, notes="done")
    assert dummy.updated == (3, ["in-progress"], None)
    assert dummy.state_update == (3, "closed")
    assert dummy.comment == (3, "done")


def test_get_next_task_none(monkeypatch, tmp_path):
    issues = [
        {"number": 1, "state": "closed", "labels": []},
        {"number": 2, "labels": ["blocked"]},
    ]
    dummy = DummyIssueManager(issues)
    tm = TaskManager.__new__(TaskManager)
    tm.issue_manager = dummy
    tm.pinned_store = PinnedItemsStore(config_dir=tmp_path)
    tm.project_id = "o/r"
    from src.tasks.ranking import RankingEngine

    tm.ranking = RankingEngine()
    assert tm.get_next_task() is None


def test_list_tasks(monkeypatch, tmp_path):
    issues = [
        _make_issue(1, "priority-medium", 1),
        _make_issue(2, "priority-high", 5),
    ]
    dummy = DummyIssueManager(issues)
    tm = TaskManager.__new__(TaskManager)
    tm.issue_manager = dummy
    tm.pinned_store = PinnedItemsStore(config_dir=tmp_path)
    tm.project_id = "o/r"
    from src.tasks.ranking import RankingEngine

    tm.ranking = RankingEngine()
    tasks = tm.list_tasks()
    assert [t["number"] for t in tasks] == [2, 1]


def test_update_task_rollover(monkeypatch):
    dummy = DummyIssueManager([])
    tm = TaskManager.__new__(TaskManager)
    tm.issue_manager = dummy
    from src.tasks.ranking import RankingEngine

    tm.ranking = RankingEngine()
    called = {}

    def roll(num):
        called["issue"] = num
        return True

    tm.rollover_subtasks = roll
    tm.update_task(4, done=True)
    assert called["issue"] == 4


def test_pinned_items_skipped(tmp_path):
    issues = [_make_issue(1, "priority-high", 0)]
    dummy = DummyIssueManager(issues)
    store = PinnedItemsStore(config_dir=tmp_path)
    store.pin_item("o/r", "1")
    tm = TaskManager.__new__(TaskManager)
    tm.issue_manager = dummy
    tm.pinned_store = store
    tm.project_id = "o/r"
    from src.tasks.ranking import RankingEngine

    tm.ranking = RankingEngine()
    assert tm.get_next_task() is None
