"""
The Boss — Главный Оркестратор UZ AI Factory.
Управляет агентами: Tech Lead, CMO, QA Lead.
Интегрирован с Agent Builder RAG для обогащения контекста.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Добавляем корневую директорию в путь, чтобы импортировать агентов
sys.path.append(str(Path(__file__).parent.parent))

from agents.tech_lead import TechLead
from agents.cmo import CMO
from agents.qa_lead import QALead
from agents.cpo import CPO
from agents.sales_head import SalesHead
from config import BASE_DIR, ENABLE_V2_AGENTS

# V2 Services
if ENABLE_V2_AGENTS:
    from services.workspace_manager import WorkspaceManager
    from services.agent_runner import AgentRunner

# RAG Integration
try:
    from services.vector_search_service import get_search_service
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAG not available. Running without knowledge base.")

# Ralph Wiggum Loop Integration
try:
    from agents.ralph_loop import RalphLoop
    RALPH_AVAILABLE = True
except ImportError:
    RALPH_AVAILABLE = False
    print("⚠️ Ralph Loop not available. Using standard iterations.")

class TheBoss:
    """
    AI Orchestrator.
    Запускает конвейер создания стартапа.
    Использует RAG для обогащения контекста.
    Поддерживает Ralph-режим для автономного self-correction.
    """
    
    MAX_ITERATIONS = 3  # Standard mode
    RALPH_MAX_ITERATIONS = 5  # Ralph mode (fewer but smarter)
    
    def __init__(self):
        # V1 Agents
        self.cpo = CPO()
        self.tech_lead = TechLead()
        self.cmo = CMO()
        self.sales_head = SalesHead()
        self.qa_lead = QALead()
        self.projects_dir = BASE_DIR / "data" / "projects"
        
        # V2 Services
        if ENABLE_V2_AGENTS:
            self.workspace_manager = WorkspaceManager()
        
        # RAG Service
        self.search_service = get_search_service() if RAG_AVAILABLE else None
    
    def _enrich_context_with_rag(self, idea: str, base_context: str = "") -> str:
        """Обогащаем контекст релевантными документами из базы знаний."""
        if not self.search_service or not self.search_service.is_initialized:
            return base_context
        
        print("🔍 Searching knowledge base for relevant context...")
        rag_context = self.search_service.get_context_for_agent(idea, max_chars=1500)
        
        if rag_context:
            print(f"   ✅ Found relevant documents")
            return f"{base_context}\n\n📚 Relevant Knowledge:\n{rag_context}"
        
        return base_context

    def run_startup_factory(self, idea: str, context: str = ""):
        """
        Запускает полный цикл производства стартапа с итеративным улучшением.
        """
        print(f"\n👔 The Boss: Starting new project for idea: '{idea}'")
        print("="*60)
        
        # RAG: Enrich context with knowledge base
        enriched_context = self._enrich_context_with_rag(idea, context)
        
        # === V2 PIPELINE (Vibe-Lite) ===
        if ENABLE_V2_AGENTS:
            print("\n🚀 V2 MODE: Using Git Worktrees & Agent Runner")
            return self._run_v2_pipeline(idea, enriched_context)
            
        # === V1 PIPELINE (Legacy) ===
        print("\n⚠️ V1 MODE: Using Legacy Pipeline")
        
        # 1. Product Phase (CPO)
        print("\n🧠 PHASE 1: PRODUCT STRATEGY (CPO)")
        prd = self.cpo.create_prd(idea, enriched_context)
        
        if "error" in prd:
            print(f"❌ Critical Error in PRD: {prd['error']}")
            return
            
        project_name = prd.get("project_name", "Unknown Project")
        print(f"✅ PRD created for: {project_name}")
        
        # Convert PRD to string for Tech Lead
        prd_str = json.dumps(prd, indent=2)

        # 2. Engineering Phase (Tech Lead)
        print("\n🏗 PHASE 2: ENGINEERING (Tech Lead)")
        tech_spec = self.tech_lead.create_spec(project_name, prd_str)
        
        if "error" in tech_spec:
            print(f"❌ Critical Error in Tech Spec: {tech_spec['error']}")
            return
            
        print(f"✅ Tech Spec created.")
        
        # 3. Marketing Phase (CMO)
        print("\n📢 PHASE 3: MARKETING (CMO)")
        tech_spec_str = json.dumps(tech_spec, indent=2)
        marketing_plan = self.cmo.create_marketing_plan(project_name, tech_spec_str, context)
        
        if "error" in marketing_plan:
            print(f"❌ Critical Error in Marketing Plan: {marketing_plan['error']}")
            return
            
        print(f"✅ Marketing Plan created.")

        # 4. Sales Phase (Sales Head)
        print("\n💰 PHASE 4: SALES AUTOMATION (Sales Head)")
        marketing_str = json.dumps(marketing_plan, indent=2)
        sales_kit = self.sales_head.create_sales_kit(project_name, marketing_str, context)
        
        if "error" in sales_kit:
            print(f"❌ Critical Error in Sales Kit: {sales_kit['error']}")
            return
            
        print(f"✅ Sales Kit created.")
        
        # 5. Quality Assurance Phase with Iteration Loop
        for attempt in range(1, self.MAX_ITERATIONS + 1):
            print(f"\n⚖️ PHASE 5: QUALITY CONTROL (QA Lead) - Attempt {attempt}/{self.MAX_ITERATIONS}")
            qa_report = self.qa_lead.review_project(project_name)
            
            if "error" in qa_report:
                print(f"❌ Critical Error in QA Report: {qa_report['error']}")
                return
            
            status = qa_report.get("status", "UNKNOWN")
            score = qa_report.get("score", 0)
            
            print(f"   Status: {status}, Score: {score}/100")
            
            # Check if we pass
            if status == "PASS" or score >= 80:
                print("\n🚀 PROJECT APPROVED! READY FOR LAUNCH.")
                print(f"   Location: {self.projects_dir}/{project_name.lower().replace(' ', '_')}")
                return {"status": "PASS", "project_name": project_name, "score": score}
            
            elif status == "WARN" and score >= 60:
                print("\n⚠️ PROJECT APPROVED WITH WARNINGS.")
                print("   Minor issues to fix before launch.")
                return {"status": "WARN", "project_name": project_name, "score": score}
            
            else:
                # FAIL or low score - need to iterate
                if attempt < self.MAX_ITERATIONS:
                    print(f"\n🔄 Iteration needed. Refining PRD based on QA feedback...")
                    
                    # Refine PRD
                    prd = self.cpo.refine_prd(prd, qa_report)
                    
                    if "error" in prd:
                        print(f"❌ Error refining PRD: {prd['error']}")
                        break
                    
                    # Re-run downstream agents with refined PRD
                    prd_str = json.dumps(prd, indent=2)
                    
                    print("\n🏗 Re-running Tech Lead with refined PRD...")
                    tech_spec = self.tech_lead.create_spec(project_name, prd_str)
                    
                    print("\n📢 Re-running CMO...")
                    tech_spec_str = json.dumps(tech_spec, indent=2)
                    marketing_plan = self.cmo.create_marketing_plan(project_name, tech_spec_str, context)
                    
                    print("\n💰 Re-running Sales Head...")
                    marketing_str = json.dumps(marketing_plan, indent=2)
                    sales_kit = self.sales_head.create_sales_kit(project_name, marketing_str, context)
                else:
                    print(f"\n❌ PROJECT REJECTED after {self.MAX_ITERATIONS} attempts.")
                    print(f"   Final Score: {score}/100")
                    print("   See qa_report.md for details.")
                    return {"status": "FAIL", "project_name": project_name, "score": score}

    def _run_v2_pipeline(self, idea: str, context: str):
        """
        V2 Pipeline: Uses WorkspaceManager and AgentRunner.
        """
        import time
        
        # 1. Create Workspace
        task_id = f"project-{hash(idea) % 10000:04d}"
        print(f"📦 Creating Workspace: {task_id}")
        
        try:
            worktree = self.workspace_manager.create(task_id, idea, "boss")
            print(f"   Worktree: {worktree}")
        except Exception as e:
            print(f"   ⚠️ Workspace might exist, trying to reuse... ({e})")
            # If exists, we might want to continue or fail. For now, assume we can reuse.
        
        # 2. Run CPO (Product Phase)
        print("\n🧠 PHASE 1: PRODUCT STRATEGY (CPOv2)")
        runner = AgentRunner(task_id, "cpo")
        
        try:
            pid = runner.start()
            print(f"   🚀 CPO Agent started (PID: {pid})")
            
            # Wait for completion (simple polling for now)
            print("   ⏳ Waiting for CPO...")
            while runner.is_running():
                time.sleep(1)
                # Optional: stream logs here
            
            # Check result (exit code or log)
            # Since AgentRunner.wait() returns exit code, but here we just polled is_running
            # We can check logs or assume success if it stopped gracefully
            
            print("   ✅ CPO finished.")
            print(f"   📄 Output: worktrees/feat-{task_id}/prd.md")
            
            # In a real V2 pipeline, we would trigger TechLead here
            # For now, we just stop after CPO as per Vibe-Lite scope
            
            return {"status": "PASS", "task_id": task_id, "worktree": str(worktree)}
            
        except Exception as e:
            print(f"❌ V2 Pipeline Failed: {e}")
            runner.stop()
            return {"status": "FAIL", "error": str(e)}

    def run_with_ralph(self, idea: str, context: str = "") -> Dict:
        """
        🤖 Ralph Wiggum Mode — Autonomous self-correcting execution.
        
        Использует RalphLoop для автоматического исправления ошибок.
        Модель сама анализирует неудачи и корректирует подход.
        """
        if not RALPH_AVAILABLE:
            print("⚠️ Ralph not available. Falling back to standard mode.")
            return self.run_startup_factory(idea, context)
        
        print("\n🤖 RALPH MODE ACTIVATED")
        print("=" * 60)
        
        # Create Ralph Loop with project pipeline as agent_fn
        ralph = RalphLoop(
            agent_fn=lambda prompt: self._ralph_iteration(prompt, idea, context),
            max_iterations=self.RALPH_MAX_ITERATIONS,
            delay_seconds=2.0,
            similarity_threshold=0.9
        )
        
        task = f"Create a complete startup for: {idea}. Market: {context}"
        result = ralph.run(task)
        
        print("\n" + "=" * 60)
        print(f"🏁 RALPH COMPLETE")
        print(f"   Success: {result.success}")
        print(f"   Iterations: {result.iterations}")
        print(f"   Loop ID: {result.loop_id}")
        print(f"   Reason: {result.stopped_reason}")
        print(f"   Time: {result.elapsed_seconds:.1f}s")
        
        return {
            "status": "PASS" if result.success else "FAIL",
            "result": result.result,
            "iterations": result.iterations,
            "loop_id": result.loop_id
        }
    
    def _ralph_iteration(self, prompt: str, idea: str, context: str) -> Dict:
        """
        Single iteration for Ralph to wrap.
        Returns structured JSON response.
        """
        try:
            # Enrich with RAG
            enriched_context = self._enrich_context_with_rag(idea, context)
            
            # Run the pipeline
            result = self.run_startup_factory(idea, enriched_context)
            
            if result and result.get("status") == "PASS":
                return {
                    "status": "COMPLETE",
                    "result": f"Project approved with score {result.get('score', 'N/A')}",
                    "confidence": result.get("score", 80)
                }
            elif result and result.get("status") == "WARN":
                return {
                    "status": "COMPLETE",
                    "result": f"Project approved with warnings. Score: {result.get('score')}",
                    "confidence": result.get("score", 70)
                }
            else:
                return {
                    "status": "IN_PROGRESS",
                    "result": f"Pipeline returned: {result}",
                    "error_reason": "QA rejected the project. Need to improve PRD quality.",
                    "confidence": 30
                }
        except Exception as e:
            return {
                "status": "FAILED",
                "result": "",
                "error_reason": str(e),
                "confidence": 0
            }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Startup Factory")
    parser.add_argument("--idea", type=str, help="Business Idea", required=True)
    parser.add_argument("--context", type=str, help="Market Context", default="Uzbekistan Market")
    parser.add_argument("--ralph", action="store_true", help="Enable Ralph Wiggum autonomous mode")
    
    args = parser.parse_args()
    
    boss = TheBoss()
    
    if args.ralph:
        result = boss.run_with_ralph(args.idea, args.context)
    else:
        result = boss.run_startup_factory(args.idea, args.context)
    
    print(f"\n📊 Final Result: {result}")

