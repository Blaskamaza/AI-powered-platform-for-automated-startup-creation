"""
CPO Agent — Директор по продукту UZ AI Factory
Отвечает за превращение "идеи" в "продукт". Пишет PRD (Product Requirements Document).
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from google import genai
from google.genai import types

from config import (
    GOOGLE_API_KEY, GEMINI_PRO_MODEL, BASE_DIR
)
from utils.uz_finance import calculate_unit_economics

# Настройка Gemini
client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

class CPO:
    """
    AI Agent, который действует как Senior Product Manager.
    Принимает Raw Idea -> Выдает PRD (User Stories, Features, Monetization).
    """
    
    def __init__(self):
        self.model_name = GEMINI_PRO_MODEL
        self.client = client
        self.system_prompt = """
        You are a visionary Chief Product Officer (CPO) for a startup factory in Uzbekistan.
        Your goal is to take a vague business idea and turn it into a concrete Product Requirements Document (PRD).
        
        Principles:
        1. **User First:** Focus on the problem and the user, not just features.
        2. **MVP Mindset:** Define what is critical for V1 vs what can wait.
        3. **Monetization:** The product must make money. Define how.
        4. **Local Context:** Adapt features for the Uzbekistan market (Telegram, P2P transfers, trust issues).
        """

    def create_prd(self, idea: str, context: str = "") -> Dict:
        """
        Генерирует PRD (Product Requirements Document).
        """
        print(f"🧠 CPO: Analyzing idea '{idea}'...")
        
        prompt = f"""
        {self.system_prompt}
        
        IDEA: {idea}
        
        MARKET CONTEXT:
        {context}
        
        TASK:
        Create a comprehensive PRD.
        
        1. **Problem Statement:** What pain are we solving?
        2. **Target Audience:** Who are the users? (Personas)
        3. **User Stories:** "As a [user], I want to [action], so that [benefit]."
        4. **Core Features (MVP):** List the absolute must-haves.
        5. **Monetization Strategy:** How do we make money? (Subscription, Commission, Ads).
        6. **Success Metrics:** Key KPIs (e.g., DAU, Retention).
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "project_name": "Short Catchy Name",
            "problem": "...",
            "audience": ["Student", "Landlord"],
            "user_stories": [
                "As a student, I want to filter by price...",
                "As a landlord, I want to hide my phone number..."
            ],
            "features": {{
                "mvp": ["Search", "Chat", "Payment"],
                "future": ["AI Matching", "Map View"]
            }},
            "monetization": "Freemium model...",
            "metrics": ["1000 users in month 1", "5% conversion"],
            "financial_estimates": {
                "estimated_price_uzs": 100000,
                "estimated_cost_uzs": 50000,
                "estimated_sales_per_month": 100
            }
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="OFF"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT", 
                            threshold="OFF"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="OFF"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="OFF"
                        ),
                    ]
                )
            )
            
            # Cleaning JSON
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            
            # Save artifact
            self._save_prd(data)
            
            return data
            
        except Exception as e:
            print(f"❌ CPO Error: {e}")
            return {"error": str(e)}

    def _save_prd(self, data: Dict):
        """Сохраняет PRD в Markdown"""
        project_name = data.get("project_name", "Unknown Project")
        folder_name = project_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        path = BASE_DIR / "data" / "projects" / folder_name
        path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        with open(path / "prd.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Save Markdown
        with open(path / "prd.md", "w", encoding="utf-8") as f:
            f.write(f"# 🧠 Product Requirements Document (PRD): {project_name}\n\n")
            
            f.write(f"## 🚩 Problem Statement\n{data.get('problem')}\n\n")
            
            f.write("## 👥 Target Audience\n")
            for persona in data.get("audience", []):
                f.write(f"- {persona}\n")
            f.write("\n")
            
            f.write("## 📖 User Stories\n")
            for story in data.get("user_stories", []):
                f.write(f"- {story}\n")
            f.write("\n")
            
            f.write("## 🛠 Core Features (MVP)\n")
            for feature in data.get("features", {}).get("mvp", []):
                f.write(f"- [ ] {feature}\n")
            f.write("\n")
            
            f.write("## 🔮 Future Features\n")
            for feature in data.get("features", {}).get("future", []):
                f.write(f"- {feature}\n")
            f.write("\n")
            
            f.write(f"## 💰 Monetization\n{data.get('monetization')}\n\n")
            
            f.write("## 📈 Success Metrics\n")
            for metric in data.get("metrics", []):
                f.write(f"- {metric}\n")
            
            # Financial Analysis
            estimates = data.get("financial_estimates", {})
            if estimates:
                price = estimates.get("estimated_price_uzs", 0)
                cost = estimates.get("estimated_cost_uzs", 0)
                sales = estimates.get("estimated_sales_per_month", 0)
                
                if price > 0:
                    economics = calculate_unit_economics(price, cost, sales)
                    f.write("\n## 🧮 Unit Economics (Uzbekistan Tax Model)\n")
                    f.write(f"**Verdict:** {economics['verdict']}\n\n")
                    f.write(f"| Metric | Value (UZS) |\n|---|---|\n")
                    f.write(f"| Revenue | {economics['revenue']:,.0f} |\n")
                    f.write(f"| Taxes | {economics['taxes']:,.0f} |\n")
                    f.write(f"| Net Profit | {economics['net_profit']:,.0f} |\n")
                    f.write(f"| Margin | {economics['margin_percent']}% |\n")
                
        print(f"✅ PRD saved to {path}/prd.md")

    def refine_prd(self, original_prd: Dict, qa_feedback: Dict) -> Dict:
        """
        Refine PRD based on QA Lead feedback.
        Called when QA rejects or gives warnings.
        """
        print(f"🔄 CPO: Refining PRD based on QA feedback...")
        
        prompt = f"""
        {self.system_prompt}
        
        ORIGINAL PRD:
        {json.dumps(original_prd, indent=2, ensure_ascii=False)}
        
        QA FEEDBACK:
        Status: {qa_feedback.get('status', 'UNKNOWN')}
        Score: {qa_feedback.get('score', 0)}/100
        Issues: {json.dumps(qa_feedback.get('issues', []), indent=2, ensure_ascii=False)}
        Recommendations: {json.dumps(qa_feedback.get('recommendations', []), indent=2, ensure_ascii=False)}
        
        TASK:
        Refine the PRD to address all QA feedback issues.
        Fix the critical issues and implement the recommendations.
        
        OUTPUT FORMAT: Same JSON structure as the original PRD.
        """
        
        try:
            if not self.client:
                return {"error": "No API key configured"}
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="OFF"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="OFF"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="OFF"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="OFF"
                        ),
                    ]
                )
            )
            
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            
            # Save refined artifact
            self._save_prd(data)
            
            print(f"✅ CPO: PRD refined successfully")
            return data
            
        except Exception as e:
            print(f"❌ CPO Refine Error: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    import os
    import sys
    
    # Check if running via AgentRunner (V2)
    task_id = os.environ.get("AGENT_TASK_ID")
    
    if task_id:
        try:
            print(f"🚀 Starting CPOv2 for Task: {task_id}")
            from agents.v2.cpo_v2 import CPOv2
            from services.workspace_manager import WorkspaceManager
            
            # Load metadata to get the idea
            wm = WorkspaceManager()
            meta = wm.get_meta(task_id)
            idea = meta.get("title", "Unknown Idea")
            context = "Uzbekistan Market" # Default context or from meta if we add it
            
            # Execute V2 Agent
            agent = CPOv2(task_id=task_id)
            
            # Mock Mode for testing pipeline without API key
            if os.environ.get("MOCK_MODE"):
                print("⚠️ MOCK MODE: Simulating CPOv2 execution")
                # Create dummy PRD
                prd = {
                    "project_name": "Mock Project",
                    "problem": "Mock Problem",
                    "features": {"mvp": ["Feature A", "Feature B"]},
                    "status": "MOCK_SUCCESS"
                }
                agent._save_to_worktree(prd)
                result = agent.build_result(True, prd)
            else:
                result = agent.execute({"idea": idea, "context": context})
            
            if result.success:
                print("✅ CPOv2 Execution Complete")
                sys.exit(0)
            else:
                print(f"❌ CPOv2 Failed: {result.error}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Fatal Error in CPOv2 Runner: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
    else:
        # Legacy V1 Test run
        print("⚠️ Running in Legacy V1 Mode")
        agent = CPO()
        agent.create_prd(
            idea="A marketplace for renting wedding dresses in Tashkent.",
            context="Weddings are huge in Uzbekistan, but dresses are expensive to buy."
        )
