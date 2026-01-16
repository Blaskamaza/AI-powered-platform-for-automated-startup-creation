"""
CPO Agent — Chief Product Officer (V2)

This module re-exports CPOv2 as CPO for backwards compatibility.
V1 code has been moved to legacy/v1 branch.

The CPO agent is now powered by the Skills system and writes to Git worktrees.
"""

# Re-export CPOv2 as CPO for backwards compatibility
from agents.v2.cpo_v2 import CPOv2 as CPO

__all__ = ["CPO"]


# === Entry point for AgentRunner ===
if __name__ == "__main__":
    import os
    import sys
    
    task_id = os.environ.get("AGENT_TASK_ID")
    
    if task_id:
        print(f"🚀 Starting CPO (V2) for Task: {task_id}")
        from services.workspace_manager import WorkspaceManager
        
        # Load metadata to get the idea
        wm = WorkspaceManager()
        meta = wm.get_meta(task_id)
        idea = meta.get("title", "Unknown Idea")
        context = "Uzbekistan Market"
        
        # Execute
        agent = CPO(task_id=task_id)
        result = agent.execute({"idea": idea, "context": context})
        
        if result.success:
            print("✅ CPO Execution Complete")
            sys.exit(0)
        else:
            print(f"❌ CPO Failed: {result.error}")
            sys.exit(1)
    else:
        # Interactive test
        print("⚠️ No AGENT_TASK_ID set. Running in test mode.")
        agent = CPO()
        result = agent.execute({"idea": "Test MVP", "context": "Uzbekistan"})
        print(f"Success: {result.success}")
