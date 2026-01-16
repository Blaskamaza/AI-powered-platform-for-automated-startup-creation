"""
CPO V2 — Uses Skills System for PRD generation.

Key differences from V1:
- Uses generate_with_skills() instead of hardcoded prompts
- Works with WorkspaceManager for isolated output
- Writes artifacts to worktree, not global data/
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from agents.base import BaseAgent, AgentResult


class CPOv2(BaseAgent):
    """
    Chief Product Officer V2 — Agentic Skills Pattern.
    
    Usage:
        cpo = CPOv2()
        cpo.task_id = "delivery-app-001"  # Links to worktree
        result = cpo.execute({"idea": "Food delivery for Uzbekistan"})
    """
    
    name = "CPOv2"
    model = "gemini-2.0-flash"
    temperature = 0.7
    
    # V2 uses skills, not hardcoded prompts
    skills_enabled = True
    
    def __init__(self, task_id: Optional[str] = None):
        super().__init__()
        self.task_id = task_id
        self._worktree: Optional[Path] = None
    
    @property
    def worktree(self) -> Optional[Path]:
        """Get worktree path for this task."""
        if self._worktree:
            return self._worktree
        if self.task_id:
            path = Path(f"worktrees/feat-{self.task_id}")
            if path.exists():
                return path
        return None
    
    @worktree.setter
    def worktree(self, path: Path):
        self._worktree = path
    
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Generate PRD using Skills system.
        
        Args:
            input_data: {"idea": str, "context": str (optional)}
            
        Returns:
            AgentResult with PRD data
        """
        idea = input_data.get("idea", "")
        context = input_data.get("context", "Uzbekistan Market")
        
        if not idea:
            return self.build_result(False, {}, "No idea provided")
        
        self.logger.info(f"🧠 CPOv2: Generating PRD for '{idea}'...")
        
        # Build prompt that triggers skill discovery
        prompt = f"""
You are the Chief Product Officer analyzing a new product idea.

IDEA: {idea}
CONTEXT: {context}

Your task:
1. First, check if there's a PRD standard skill available for this market
2. If found, use that skill to structure your PRD
3. Generate a comprehensive PRD with:
   - Problem Statement
   - Target Users
   - Core Features (prioritized)
   - User Stories
   - Success Metrics
   - Monetization Strategy
   - MVP Scope

Output format: JSON with all sections.
"""
        
        try:
            # V2: Uses agentic skill discovery
            response = self.generate_with_skills(
                prompt=prompt,
                system_prompt="You are an expert Product Manager. Use available skills when relevant.",
                max_skill_calls=2,
                auto_cleanup=True
            )
            
            # Parse JSON from response
            prd = self._extract_json(response)
            
            # Track which skills were used
            skills_used = [skill.name for skill in self._active_skills] if self._active_skills else []
            
            # Save to worktree if available
            if self.worktree:
                self._save_to_worktree(prd)
            
            return self.build_result(True, {
                "prd": prd,
                "skills_used": skills_used,
                "raw_response": response
            })
            
        except Exception as e:
            self.logger.error(f"❌ CPOv2 failed: {e}")
            return self.build_result(False, {}, str(e))
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from LLM response."""
        import re
        
        # Try to find JSON block
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find raw JSON
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        
        # Fallback: return as-is
        return {"raw_content": text}
    
    def _save_to_worktree(self, prd: Dict) -> None:
        """Save PRD to worktree."""
        if not self.worktree:
            return
        
        # Save JSON
        json_path = self.worktree / "prd.json"
        json_path.write_text(json.dumps(prd, indent=2, ensure_ascii=False), encoding="utf-8")
        self.logger.info(f"📝 Saved: {json_path}")
        
        # Save Markdown
        md_path = self.worktree / "prd.md"
        md_content = self._prd_to_markdown(prd)
        md_path.write_text(md_content, encoding="utf-8")
        self.logger.info(f"📝 Saved: {md_path}")
    
    def _prd_to_markdown(self, prd: Dict) -> str:
        """Convert PRD dict to Markdown."""
        lines = ["# Product Requirements Document\n"]
        
        for key, value in prd.items():
            title = key.replace("_", " ").title()
            lines.append(f"## {title}\n")
            
            if isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    lines.append(f"**{k}**: {v}")
            else:
                lines.append(str(value))
            
            lines.append("")
        
        return "\n".join(lines)


# For testing
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    cpo = CPOv2()
    result = cpo.execute({"idea": "Food delivery app for Tashkent", "context": "Uzbekistan"})
    
    print(f"Success: {result.success}")
    print(f"Skills used: {result.data.get('skills_used', [])}")
