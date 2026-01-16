"""
Test V2 Pipeline — Verifies that TheBoss uses AgentRunner and WorkspaceManager.
"""

import sys
import os
from pathlib import Path

# Add project root
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from agents.boss import TheBoss
from config import ENABLE_V2_AGENTS

def main():
    print(f"🔧 Config ENABLE_V2_AGENTS: {ENABLE_V2_AGENTS}")
    
    if not ENABLE_V2_AGENTS:
        print("❌ V2 is disabled in config.py. Please enable it first.")
        sys.exit(1)
    
    # Enable Mock Mode for testing
    os.environ["MOCK_MODE"] = "true"
    
    boss = TheBoss()
    
    idea = "AI-powered To-Do List for Students"
    context = "Uzbekistan Market"
    
    print(f"\n🧪 Testing V2 Pipeline with idea: '{idea}'")
    result = boss.run_startup_factory(idea, context)
    
    print("\n📊 Result:")
    print(result)
    
    if result and result.get("status") == "PASS" and "worktree" in result:
        print("\n✅ V2 Pipeline Test Passed!")
        print(f"   Worktree: {result['worktree']}")
    else:
        print("\n❌ V2 Pipeline Test Failed")

if __name__ == "__main__":
    main()
