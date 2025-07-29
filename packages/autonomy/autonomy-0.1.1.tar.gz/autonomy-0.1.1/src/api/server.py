from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ..audit.logger import AuditLogger
from ..audit.undo import UndoManager
from ..core.secret_vault import SecretVault
from ..github.issue_manager import IssueManager
from ..tasks.backlog_doctor import BacklogDoctor
from ..tasks.task_manager import TaskManager

templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)


class UpdateTaskRequest(BaseModel):
    status: Optional[str] = None
    done: bool = False
    notes: Optional[str] = None


def create_app(
    issue_manager: IssueManager,
    audit_logger: Optional[AuditLogger] = None,
    vault: Optional["SecretVault"] = None,
) -> FastAPI:
    """Return a FastAPI app wired with core managers."""

    task_manager = TaskManager.__new__(TaskManager)
    task_manager.issue_manager = issue_manager
    from ..tasks.pinned_items import PinnedItemsStore

    task_manager.pinned_store = PinnedItemsStore()
    from ..tasks.ranking import RankingEngine

    task_manager.ranking = RankingEngine()
    task_manager.project_id = f"{issue_manager.owner}/{issue_manager.repo}"
    backlog_doctor = BacklogDoctor(issue_manager)
    audit_logger = audit_logger or AuditLogger(Path("audit.log"))
    undo_manager = UndoManager(issue_manager, audit_logger)
    vault = vault or SecretVault()

    app = FastAPI(title="Autonomy API", version="1.0")

    # ------------------------------ Tasks ------------------------------
    @app.get("/api/v1/tasks/next")
    def get_next_task(assignee: Optional[str] = None, team: Optional[str] = None):
        issue = task_manager.get_next_task(assignee=assignee, team=team)
        if not issue:
            raise HTTPException(status_code=404, detail="No tasks found")
        return issue

    @app.get("/api/v1/tasks")
    def list_tasks(
        assignee: Optional[str] = None,
        team: Optional[str] = None,
        limit: int = 10,
    ):
        return task_manager.list_tasks(assignee=assignee, team=team, limit=limit)

    @app.post("/api/v1/tasks/{issue_id}/update")
    def update_task(issue_id: int, payload: UpdateTaskRequest):
        success = task_manager.update_task(
            issue_id,
            status=payload.status,
            done=payload.done,
            notes=payload.notes,
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update task")
        return {"success": True}

    # --------------------------- Backlog Doctor ---------------------------
    @app.post("/api/v1/backlog/doctor/run")
    def run_backlog_doctor(
        stale_days: int = 14,
        checklist_limit: int = 10,
    ):
        return backlog_doctor.run(
            stale_days=stale_days,
            checklist_limit=checklist_limit,
        )

    # ------------------------------ Audit ------------------------------
    @app.get("/api/v1/audit/log")
    def get_audit_log():
        return list(audit_logger.iter_logs())

    @app.post("/api/v1/audit/undo/{hash_value}")
    def undo(hash_value: str):
        if undo_manager.undo(hash_value):
            return {"success": True}
        raise HTTPException(status_code=404, detail="Operation not found")

    # ---------------------------- Settings -----------------------------
    @app.get("/settings", response_class=HTMLResponse)
    def settings_page(request: Request):
        values = {
            "openrouter_api_key": vault.get_secret("openrouter_api_key") or "",
            "mem0_url": vault.get_secret("mem0_url") or "",
            "github_token": vault.get_secret("github_token") or "",
            "slack_token": vault.get_secret("slack_token") or "",
        }
        return templates.TemplateResponse(
            "settings.html", {"request": request, "values": values}
        )

    @app.post("/api/v1/settings")
    def update_settings(
        openrouter_api_key: str = Form(""),
        mem0_url: str = Form(""),
        github_token: str = Form(""),
        slack_token: str = Form(""),
    ):
        if openrouter_api_key:
            vault.set_secret("openrouter_api_key", openrouter_api_key)
        if mem0_url:
            vault.set_secret("mem0_url", mem0_url)
        if github_token:
            vault.set_secret("github_token", github_token)
        if slack_token:
            vault.set_secret("slack_token", slack_token)
        return RedirectResponse("/settings", status_code=303)

    return app
