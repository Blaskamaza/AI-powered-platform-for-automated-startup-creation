"""
WorkspaceManager — Git Worktree-based agent isolation.

Creates isolated workspaces for each task using Git worktrees.
Each workspace has its own branch, META.yml (source of truth), and .env copy.

No Docker, no complex orchestration — just Git.
"""

import subprocess
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Try to import yaml, fallback to simple implementation
try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger("WorkspaceManager")


class WorkspaceManager:
    """
    Git Worktree-based workspace manager.
    
    Usage:
        wm = WorkspaceManager()
        worktree = wm.create("task-123", "MVP доставка", "cpo")
        # Work happens in worktree...
        wm.remove("task-123")
    """
    
    BASE_WORKTREE = Path("./worktrees")
    ENV_TEMPLATE = Path(".env")
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize WorkspaceManager.
        
        Args:
            base_path: Override base worktree directory (default: ./worktrees)
        """
        if base_path:
            self.BASE_WORKTREE = Path(base_path)
        
        # Ensure worktrees directory exists
        self.BASE_WORKTREE.mkdir(parents=True, exist_ok=True)
    
    def create(self, task_id: str, title: str, agent: str, skill: Optional[str] = None) -> Path:
        """
        Create isolated workspace for a task.
        
        Creates:
        1. Git branch from main
        2. Git worktree in ./worktrees/feat/{task_id}
        3. Copy of .env (not symlink for isolation)
        4. META.yml with task metadata
        5. Initial commit
        
        Args:
            task_id: Unique task identifier (e.g., "delivery-456")
            title: Human-readable task title
            agent: Agent name (e.g., "cpo", "tech_lead")
            skill: Optional skill to activate (e.g., "prd-standard-uz")
            
        Returns:
            Path to created worktree
        """
        branch = f"feat/{task_id}"
        worktree = self.BASE_WORKTREE / branch.replace("/", "-")  # Windows-safe path
        
        if worktree.exists():
            raise WorkspaceExistsError(f"Workspace already exists: {worktree}")
        
        try:
            # 1. Create branch from main (or master)
            main_branch = self._get_main_branch()
            self._run_git(["branch", branch, main_branch])
            logger.info(f"📦 Created branch: {branch}")
            
            # 2. Create worktree
            self._run_git(["worktree", "add", str(worktree), branch])
            logger.info(f"📂 Created worktree: {worktree}")
            
            # 3. Copy .env (not symlink for true isolation)
            if self.ENV_TEMPLATE.exists():
                shutil.copy(self.ENV_TEMPLATE, worktree / ".env")
                logger.debug(f"📋 Copied .env to worktree")
            
            # 4. Create META.yml — single source of truth
            meta = {
                "task_id": task_id,
                "title": title,
                "agent": agent,
                "status": "backlog",
                "skill": skill,
                "xp_reward": 0,
                "parent_commit": self._get_current_commit(),
                "created_at": self._now_iso(),
                "updated_at": self._now_iso(),
            }
            self._write_yaml(worktree / "META.yml", meta)
            logger.info(f"📝 Created META.yml")
            
            # 5. Commit META.yml
            self._run_git_in_worktree(worktree, ["add", "META.yml"])
            self._run_git_in_worktree(worktree, ["commit", "-m", f"init: {title}"])
            logger.info(f"✅ Initial commit in {branch}")
            
            return worktree
            
        except subprocess.CalledProcessError as e:
            # Cleanup on failure
            self._cleanup_failed_workspace(task_id, worktree)
            raise WorkspaceCreationError(f"Failed to create workspace: {e}") from e
    
    def remove(self, task_id: str, force: bool = False) -> None:
        """
        Remove workspace completely.
        
        Args:
            task_id: Task identifier
            force: Force remove even if uncommitted changes
        """
        branch = f"feat/{task_id}"
        worktree = self.BASE_WORKTREE / branch.replace("/", "-")
        
        try:
            # Remove worktree
            cmd = ["worktree", "remove", str(worktree)]
            if force:
                cmd.insert(2, "--force")
            self._run_git(cmd)
            logger.info(f"📂 Removed worktree: {worktree}")
            
            # Delete branch
            self._run_git(["branch", "-D", branch])
            logger.info(f"🗑️ Deleted branch: {branch}")
            
        except subprocess.CalledProcessError as e:
            raise WorkspaceRemovalError(f"Failed to remove workspace: {e}") from e
    
    def get_meta(self, task_id: str) -> Dict[str, Any]:
        """
        Read META.yml from workspace.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Parsed META.yml as dict
        """
        branch = f"feat/{task_id}"
        worktree = self.BASE_WORKTREE / branch.replace("/", "-")
        meta_path = worktree / "META.yml"
        
        if not meta_path.exists():
            raise WorkspaceNotFoundError(f"META.yml not found in {worktree}")
        
        return self._read_yaml(meta_path)
    
    def update_meta(self, task_id: str, updates: Dict[str, Any], commit: bool = True) -> None:
        """
        Update META.yml and optionally commit.
        
        Args:
            task_id: Task identifier
            updates: Fields to update
            commit: Whether to commit the change
        """
        branch = f"feat/{task_id}"
        worktree = self.BASE_WORKTREE / branch.replace("/", "-")
        meta_path = worktree / "META.yml"
        
        # Read current
        meta = self._read_yaml(meta_path)
        
        # Update
        meta.update(updates)
        meta["updated_at"] = self._now_iso()
        
        # Write
        self._write_yaml(meta_path, meta)
        
        # Commit
        if commit:
            self._run_git_in_worktree(worktree, ["add", "META.yml"])
            msg = f"update: {', '.join(updates.keys())}"
            self._run_git_in_worktree(worktree, ["commit", "-m", msg])
            logger.info(f"📝 Updated META.yml: {updates}")
    
    def list_workspaces(self) -> list:
        """
        List all active workspaces.
        
        Returns:
            List of dicts with workspace info
        """
        result = []
        
        try:
            output = subprocess.check_output(
                ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/feat/*"],
                stderr=subprocess.DEVNULL,
                encoding="utf-8",
                errors="replace"
            ).strip()
            
            if not output:
                return []
            
            for branch in output.splitlines():
                try:
                    # Try to get META.yml from branch
                    meta_yaml = subprocess.check_output(
                        ["git", "show", f"{branch}:META.yml"],
                        stderr=subprocess.DEVNULL,
                        encoding="utf-8",
                        errors="replace"
                    )
                    
                    meta = self._parse_yaml(meta_yaml)
                    meta["branch"] = branch
                    result.append(meta)
                except subprocess.CalledProcessError:
                    # Branch without META.yml — skip
                    continue
                    
        except subprocess.CalledProcessError:
            pass
        
        return result
    
    # === Private Methods ===
    
    def _run_git(self, args: list) -> str:
        """Run git command in main repo."""
        result = subprocess.run(
            ["git"] + args,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def _run_git_in_worktree(self, worktree: Path, args: list) -> str:
        """Run git command in specific worktree."""
        result = subprocess.run(
            ["git", "-C", str(worktree)] + args,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def _get_main_branch(self) -> str:
        """Get name of main branch (main or master)."""
        try:
            self._run_git(["rev-parse", "--verify", "main"])
            return "main"
        except subprocess.CalledProcessError:
            return "master"
    
    def _get_current_commit(self) -> str:
        """Get current HEAD commit hash."""
        return self._run_git(["rev-parse", "HEAD"])
    
    def _now_iso(self) -> str:
        """Get current UTC time in ISO format."""
        return datetime.utcnow().isoformat()
    
    def _write_yaml(self, path: Path, data: dict) -> None:
        """Write dict to YAML file."""
        if yaml:
            path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))
        else:
            # Simple fallback without pyyaml
            lines = []
            for key, value in data.items():
                if value is None:
                    lines.append(f"{key}: null")
                elif isinstance(value, str):
                    lines.append(f'{key}: "{value}"')
                else:
                    lines.append(f"{key}: {value}")
            path.write_text("\n".join(lines))
    
    def _read_yaml(self, path: Path) -> dict:
        """Read YAML file to dict."""
        content = path.read_text()
        return self._parse_yaml(content)
    
    def _parse_yaml(self, content: str) -> dict:
        """Parse YAML string to dict."""
        if yaml:
            return yaml.safe_load(content)
        else:
            # Simple fallback parser
            result = {}
            for line in content.strip().splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    value = value.strip().strip('"')
                    if value == "null":
                        value = None
                    elif value.isdigit():
                        value = int(value)
                    result[key.strip()] = value
            return result
    
    def _cleanup_failed_workspace(self, task_id: str, worktree: Path) -> None:
        """Cleanup after failed workspace creation."""
        branch = f"feat/{task_id}"
        try:
            if worktree.exists():
                subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], 
                             capture_output=True)
            subprocess.run(["git", "branch", "-D", branch], capture_output=True)
        except:
            pass


# === Exceptions ===

class WorkspaceError(Exception):
    """Base exception for workspace operations."""
    pass

class WorkspaceExistsError(WorkspaceError):
    """Workspace already exists."""
    pass

class WorkspaceNotFoundError(WorkspaceError):
    """Workspace not found."""
    pass

class WorkspaceCreationError(WorkspaceError):
    """Failed to create workspace."""
    pass

class WorkspaceRemovalError(WorkspaceError):
    """Failed to remove workspace."""
    pass


# === CLI ===

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python workspace_manager.py create <task_id> <title> <agent>")
        print("  python workspace_manager.py remove <task_id>")
        print("  python workspace_manager.py list")
        sys.exit(1)
    
    wm = WorkspaceManager()
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 5:
            print("Usage: python workspace_manager.py create <task_id> <title> <agent>")
            sys.exit(1)
        task_id, title, agent = sys.argv[2], sys.argv[3], sys.argv[4]
        try:
            worktree = wm.create(task_id, title, agent)
            print(f"✅ Created: {worktree}")
        except WorkspaceError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Usage: python workspace_manager.py remove <task_id>")
            sys.exit(1)
        task_id = sys.argv[2]
        try:
            wm.remove(task_id)
            print(f"✅ Removed workspace for: {task_id}")
        except WorkspaceError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif command == "list":
        workspaces = wm.list_workspaces()
        if not workspaces:
            print("No active workspaces")
        else:
            for ws in workspaces:
                print(f"  • {ws.get('task_id')}: {ws.get('title')} [{ws.get('status')}]")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
