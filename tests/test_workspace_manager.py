"""
Tests for WorkspaceManager service.
"""

import sys
import pytest
from pathlib import Path
import subprocess

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


class TestWorkspaceManager:
    """Tests for WorkspaceManager service."""
    
    @pytest.fixture
    def wm(self):
        """Get fresh WorkspaceManager instance."""
        from services.workspace_manager import WorkspaceManager
        return WorkspaceManager()
    
    def test_create_and_remove_workspace(self, wm):
        """Should create and remove workspace."""
        task_id = "pytest-test-001"
        
        try:
            # Create
            worktree = wm.create(task_id, "Pytest Test", "cpo")
            
            assert worktree.exists()
            assert (worktree / "META.yml").exists()
            
            # Verify META
            meta = wm.get_meta(task_id)
            assert meta["task_id"] == task_id
            assert meta["status"] == "backlog"
            assert meta["agent"] == "cpo"
            
        finally:
            # Cleanup
            try:
                wm.remove(task_id, force=True)
            except:
                pass
    
    def test_list_workspaces(self, wm):
        """Should list active workspaces."""
        task_id = "pytest-test-002"
        
        try:
            # Create workspace
            wm.create(task_id, "List Test", "tech_lead")
            
            # List should include it
            workspaces = wm.list_workspaces()
            task_ids = [ws["task_id"] for ws in workspaces]
            assert task_id in task_ids
            
        finally:
            try:
                wm.remove(task_id, force=True)
            except:
                pass
    
    def test_update_meta(self, wm):
        """Should update META.yml and commit."""
        task_id = "pytest-test-003"
        
        try:
            wm.create(task_id, "Update Test", "cmo")
            
            # Update status
            wm.update_meta(task_id, {"status": "in_progress", "xp_reward": 100})
            
            # Verify
            meta = wm.get_meta(task_id)
            assert meta["status"] == "in_progress"
            assert meta["xp_reward"] == 100
            
        finally:
            try:
                wm.remove(task_id, force=True)
            except:
                pass
    
    def test_workspace_already_exists(self, wm):
        """Should raise error if workspace exists."""
        from services.workspace_manager import WorkspaceExistsError
        
        task_id = "pytest-test-004"
        
        try:
            wm.create(task_id, "Exists Test", "cpo")
            
            # Try to create again
            with pytest.raises(WorkspaceExistsError):
                wm.create(task_id, "Duplicate", "cpo")
                
        finally:
            try:
                wm.remove(task_id, force=True)
            except:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
