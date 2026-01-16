"""
Kanban Board API — REST endpoints for task management.

Reads state from Git (branches + META.yml), not from JSON.
Uses WorkspaceManager for mutations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import subprocess

router = APIRouter(prefix="/api/board", tags=["board"])


# === Models ===

class TaskCreate(BaseModel):
    """Request body for creating a task."""
    id: str
    title: str
    agent: str
    skill: Optional[str] = None


class TaskUpdate(BaseModel):
    """Request body for updating task status."""
    status: str


class TaskResponse(BaseModel):
    """Task response model."""
    task_id: str
    title: str
    agent: str
    status: str
    skill: Optional[str] = None
    xp_reward: int = 0
    branch: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# === Endpoints ===

@router.get("/tasks", response_model=List[TaskResponse])
def list_tasks():
    """
    List all active tasks.
    
    Reads from Git branches with META.yml.
    No database — Git is the source of truth.
    """
    from services.workspace_manager import WorkspaceManager
    
    wm = WorkspaceManager()
    workspaces = wm.list_workspaces()
    
    return [
        TaskResponse(
            task_id=ws.get("task_id", ""),
            title=ws.get("title", ""),
            agent=ws.get("agent", ""),
            status=ws.get("status", "backlog"),
            skill=ws.get("skill"),
            xp_reward=ws.get("xp_reward", 0),
            branch=ws.get("branch"),
            created_at=ws.get("created_at"),
            updated_at=ws.get("updated_at"),
        )
        for ws in workspaces
    ]


@router.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate):
    """
    Create a new task.
    
    Creates:
    1. Git branch feat/{task.id}
    2. Git worktree in ./worktrees/
    3. META.yml with initial state
    """
    from services.workspace_manager import WorkspaceManager, WorkspaceExistsError
    
    wm = WorkspaceManager()
    
    try:
        worktree = wm.create(task.id, task.title, task.agent, task.skill)
        meta = wm.get_meta(task.id)
        
        return TaskResponse(
            task_id=meta.get("task_id", task.id),
            title=meta.get("title", task.title),
            agent=meta.get("agent", task.agent),
            status=meta.get("status", "backlog"),
            skill=meta.get("skill"),
            xp_reward=meta.get("xp_reward", 0),
            branch=f"feat/{task.id}",
            created_at=meta.get("created_at"),
            updated_at=meta.get("updated_at"),
        )
        
    except WorkspaceExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str):
    """Get single task by ID."""
    from services.workspace_manager import WorkspaceManager, WorkspaceNotFoundError
    
    wm = WorkspaceManager()
    
    try:
        meta = wm.get_meta(task_id)
        
        return TaskResponse(
            task_id=meta.get("task_id", task_id),
            title=meta.get("title", ""),
            agent=meta.get("agent", ""),
            status=meta.get("status", "backlog"),
            skill=meta.get("skill"),
            xp_reward=meta.get("xp_reward", 0),
            branch=f"feat/{task_id}",
            created_at=meta.get("created_at"),
            updated_at=meta.get("updated_at"),
        )
        
    except WorkspaceNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task_status(task_id: str, update: TaskUpdate):
    """
    Update task status (backlog → in_progress → review → done).
    
    Changes META.yml and commits the change.
    """
    from services.workspace_manager import WorkspaceManager, WorkspaceNotFoundError
    
    valid_statuses = ["backlog", "in_progress", "review", "done", "blocked"]
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid: {valid_statuses}"
        )
    
    wm = WorkspaceManager()
    
    try:
        wm.update_meta(task_id, {"status": update.status})
        meta = wm.get_meta(task_id)
        
        return TaskResponse(
            task_id=meta.get("task_id", task_id),
            title=meta.get("title", ""),
            agent=meta.get("agent", ""),
            status=meta.get("status", update.status),
            skill=meta.get("skill"),
            xp_reward=meta.get("xp_reward", 0),
            branch=f"feat/{task_id}",
            created_at=meta.get("created_at"),
            updated_at=meta.get("updated_at"),
        )
        
    except WorkspaceNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, force: bool = False):
    """
    Delete task (removes worktree and branch).
    
    Use force=true if there are uncommitted changes.
    """
    from services.workspace_manager import WorkspaceManager, WorkspaceNotFoundError
    
    wm = WorkspaceManager()
    
    try:
        wm.remove(task_id, force=force)
        return {"message": f"Task {task_id} deleted", "task_id": task_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/columns")
def get_columns():
    """Get Kanban column definitions."""
    return {
        "columns": [
            {"id": "backlog", "title": "📥 Backlog", "color": "#6b7280"},
            {"id": "in_progress", "title": "🔄 In Progress", "color": "#3b82f6"},
            {"id": "review", "title": "👀 Review", "color": "#f59e0b"},
            {"id": "done", "title": "✅ Done", "color": "#10b981"},
            {"id": "blocked", "title": "🚫 Blocked", "color": "#ef4444"},
        ]
    }


@router.get("/stats")
def get_board_stats():
    """Get board statistics."""
    from services.workspace_manager import WorkspaceManager
    
    wm = WorkspaceManager()
    workspaces = wm.list_workspaces()
    
    stats = {
        "total": len(workspaces),
        "by_status": {},
        "by_agent": {},
        "total_xp": 0,
    }
    
    for ws in workspaces:
        status = ws.get("status", "backlog")
        agent = ws.get("agent", "unknown")
        xp = ws.get("xp_reward", 0)
        
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        stats["by_agent"][agent] = stats["by_agent"].get(agent, 0) + 1
        stats["total_xp"] += xp if isinstance(xp, int) else 0
    
    return stats
