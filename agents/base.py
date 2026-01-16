"""
BaseAgent — Unified base class for all AI agents.

Provides:
- Unified interface for Vertex AI / Gemini
- Automatic error handling and retry
- Logging and cost tracking
- Common prompting patterns
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from agents.exceptions import (
    RateLimitError,
    TimeoutError,
    AIClientError
)

# Import unified Vertex client
try:
    from agents.vertex_client import get_vertex_client, VertexClient
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)


@dataclass
class AgentResult:
    """Standardized result from any agent."""
    success: bool
    data: Dict[str, Any]
    agent_name: str
    execution_time: float
    tokens_used: int = 0
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Base class for all AI agents in UZ AI Factory.
    
    Usage:
        class MyAgent(BaseAgent):
            name = "MyAgent"
            
            def execute(self, input_data: Dict) -> AgentResult:
                response = self.generate(prompt)
                return self.build_result(True, {"output": response})
    """
    
    name: str = "BaseAgent"
    model: str = "gemini-1.5-flash"  # Default model
    temperature: float = 0.7
    max_tokens: int = 8192
    
    # Skills configuration
    skills_enabled: bool = True  # Can be disabled per-agent
    skill_ttl_seconds: int = 300  # 5 minutes default TTL for loaded skills
    
    def __init__(self):
        self.logger = logging.getLogger(self.name)
        self.client: Optional[VertexClient] = None
        self.total_tokens = 0
        
        # Conversation history for multi-turn interactions
        self._conversation_history: List[Dict[str, str]] = []
        
        # Skills state
        self._skill_manager = None  # Lazy init
        self._skills_index: Optional[List[dict]] = None
        self._active_skills: Dict[str, datetime] = {}  # skill_name -> activation_time
        self._skill_contents: Dict[str, str] = {}  # skill_name -> content
        self._skill_message_ids: List[int] = []  # Track which history messages contain skill content
        
        self._init_client()
    
    def _init_client(self):
        """Initialize Vertex AI client."""
        if VERTEX_AVAILABLE:
            self.client = get_vertex_client()
            self.logger.info(f"✅ {self.name} initialized with Vertex AI")
        else:
            self.logger.warning(f"⚠️ {self.name} running without AI client")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((RateLimitError, TimeoutError, AIClientError)),
        before_sleep=before_sleep_log(logging.getLogger("BaseAgent"), logging.WARNING)
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_output: bool = False,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate content using Vertex AI.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            json_output: Request JSON response
            temperature: Override default temperature
        
        Returns:
            Generated text
        """
        if not self.client:
            self.logger.error("No AI client available")
            return '{"error": "No AI client"}'
        
        start_time = datetime.now()
        
        try:
            response = self.client.generate(
                prompt=prompt,
                model=self.model,
                system_prompt=system_prompt,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
                json_output=json_output,
            )
        except Exception as e:
            # Map exceptions to our custom types for retry logic
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str:
                raise RateLimitError(retry_after=60) from e
            elif "503" in error_str or "timeout" in error_str:
                raise TimeoutError() from e
            else:
                raise AIClientError(str(e)) from e
        
        elapsed = (datetime.now() - start_time).total_seconds()
        self.logger.debug(f"Generated in {elapsed:.2f}s")
        
        return response
    
    def build_result(
        self,
        success: bool,
        data: Dict[str, Any],
        error: Optional[str] = None,
        execution_time: float = 0.0,
    ) -> AgentResult:
        """Build standardized result."""
        return AgentResult(
            success=success,
            data=data,
            agent_name=self.name,
            execution_time=execution_time,
            tokens_used=self.total_tokens,
            error=error,
        )
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute agent's main task.
        Must be implemented by subclasses.
        """
        pass
    
    # === Skills Methods ===
    
    def _get_skill_manager(self):
        """Lazy init SkillManager to avoid circular imports."""
        if self._skill_manager is None:
            try:
                from services.skill_manager import SkillManager
                self._skill_manager = SkillManager()
            except ImportError:
                self.logger.warning("⚠️ SkillManager not available")
                return None
        return self._skill_manager
    
    def use_skill(self, skill_name: str) -> str:
        """
        Activates a specific skill by loading its detailed instructions into memory.
        
        This method is designed to work as a Vertex AI Function Calling tool.
        The model autonomously decides when to call this based on the task.
        
        Args:
            skill_name: The exact ID of the skill (e.g., 'uz-procurement-analyzer')
            
        Returns:
            A string with the skill's detailed instructions, or helpful error if not found.
        """
        if not self.skills_enabled:
            return "Skills are disabled for this agent."
        
        manager = self._get_skill_manager()
        if not manager:
            return "SkillManager not available."
        
        try:
            content = manager.get_skill_content(skill_name)
            
            # Track activation for TTL-based garbage collection
            self._active_skills[skill_name] = datetime.now()
            self._skill_contents[skill_name] = content
            
            self.logger.info(f"📚 Activated skill: {skill_name}")
            return f"SYSTEM: Skill '{skill_name}' loaded successfully.\nINSTRUCTIONS:\n{content}"
            
        except Exception as e:
            # Provide helpful error with available skills (so model can self-correct)
            available = [s.name for s in manager.get_index()]
            self.logger.warning(f"⚠️ Skill not found: {skill_name}. Available: {available}")
            return f"Skill '{skill_name}' not found. Available skills are: {', '.join(available)}. Please try again with a valid skill name."
    
    def clear_active_skills(self, purge_history: bool = False) -> None:
        """
        Clear all active skills to free up context window.
        Call this after finishing a major task.
        
        Args:
            purge_history: If True, also remove skill content from conversation history
                          to prevent context pollution in long-running sessions.
        """
        count = len(self._active_skills)
        
        if purge_history and self._skill_message_ids:
            # Remove or redact skill content from conversation history
            for msg_id in sorted(self._skill_message_ids, reverse=True):
                if 0 <= msg_id < len(self._conversation_history):
                    # Replace with placeholder to maintain conversation flow
                    self._conversation_history[msg_id] = {
                        "role": self._conversation_history[msg_id].get("role", "assistant"),
                        "content": "[SKILL CONTENT REMOVED TO SAVE CONTEXT]"
                    }
            self._skill_message_ids.clear()
            self.logger.debug(f"🧹 Purged skill content from conversation history")
        
        self._active_skills.clear()
        self._skill_contents.clear()
        
        if count > 0:
            self.logger.info(f"🧹 Cleared {count} active skills (purge_history={purge_history})")
    
    def garbage_collect_skills(self) -> int:
        """
        Remove skills that have exceeded their TTL.
        
        Returns:
            Number of skills removed.
        """
        now = datetime.now()
        expired = []
        
        for skill_name, activated_at in self._active_skills.items():
            if now > activated_at + timedelta(seconds=self.skill_ttl_seconds):
                expired.append(skill_name)
        
        for skill_name in expired:
            del self._active_skills[skill_name]
            del self._skill_contents[skill_name]
            self.logger.debug(f"🗑️ GC: Removed expired skill '{skill_name}'")
        
        return len(expired)
    
    def _emit_xp_event(self, skill_name: str, xp_amount: int = 10) -> None:
        """
        Emit XP event after successful skill execution.
        
        XP is awarded based on skill complexity and success.
        This method can be overridden to integrate with game systems.
        
        Args:
            skill_name: Name of the skill that was used
            xp_amount: Base XP amount (can be modified based on skill metadata)
        """
        try:
            # Calculate XP based on skill metadata if available
            manager = self._get_skill_manager()
            if manager:
                skills = manager.get_index()
                for skill in skills:
                    if skill.name == skill_name:
                        # Could add xp_reward to skill metadata in the future
                        break
            
            self.logger.info(f"🎮 XP Event: +{xp_amount} XP from skill '{skill_name}'")
            
            # TODO: Integrate with actual XP system (e.g., write to META.yml)
            # For now, just log the event
            
        except Exception as e:
            self.logger.debug(f"XP emit failed (non-critical): {e}")
    
    def get_skills_for_prompt(self) -> str:
        """
        Get formatted list of available skills for inclusion in system prompt.
        
        This is the Discovery Phase - agents see skill names and descriptions
        but not full content (saves tokens). Agent should call use_skill()
        to load detailed instructions.
        
        Returns:
            Formatted string listing available skills, or empty string if disabled.
        """
        if not self.skills_enabled:
            return ""
        
        manager = self._get_skill_manager()
        if not manager:
            return ""
        
        try:
            if self._skills_index is None:
                self._skills_index = [s.to_dict() for s in manager.get_index()]
            
            if not self._skills_index:
                return ""
            
            lines = ["\nAVAILABLE SKILLS:"]
            for skill in self._skills_index:
                lines.append(f"- **{skill['name']}**: {skill['description']}")
                if skill.get('triggers'):
                    lines.append(f"  Triggers: {', '.join(skill['triggers'][:3])}")
            
            lines.append("\nTo load a skill's detailed instructions, use the use_skill(skill_name) function.")
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"❌ Error getting skills for prompt: {e}")
            return ""
    
    def get_skill_tool_schema(self) -> dict:
        """
        Get the schema for use_skill as a Vertex AI Function Calling tool.
        
        Returns:
            Tool schema dict compatible with Vertex AI.
        """
        return {
            "name": "use_skill",
            "description": "Activates a specific skill by loading its detailed instructions. Call this when you need specialized knowledge from the AVAILABLE SKILLS list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "The exact ID of the skill (e.g., 'uz-procurement-analyzer', 'prd-standard-uz')"
                    }
                },
                "required": ["skill_name"]
            }
        }
    
    def generate_with_skills(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_skill_calls: int = 3,
        auto_cleanup: bool = True,
    ) -> str:
        """
        Generate response with autonomous skill selection.
        
        The model decides which skills to use based on the task.
        This is the TRUE AGENTIC pattern - no hardcoded skill calls.
        
        Flow:
        1. Model sees available skills in system prompt
        2. Model generates response or requests a skill via function call
        3. If skill requested: load it, add to context, continue generation
        4. Repeat until model produces final response (no more function calls)
        
        Args:
            prompt: The user's task/request
            system_prompt: Optional additional system instructions
            max_skill_calls: Maximum number of skills the model can load (prevents loops)
            auto_cleanup: If True, clear skills and purge history after completion
            
        Returns:
            Final generated text after all skill interactions
        """
        if not self.client:
            return '{"error": "No AI client available"}'
        
        # Build system instruction with available skills
        skills_info = self.get_skills_for_prompt()
        full_system = f"""{system_prompt or ''}

{skills_info}

If the task requires specialized knowledge from the skills above, call use_skill(skill_name) to load the instructions before proceeding.
"""
        
        # Initialize conversation
        self._conversation_history = [{"role": "user", "content": prompt}]
        skill_calls_made = 0
        
        while skill_calls_made < max_skill_calls:
            # Generate with current context
            full_prompt = self._build_conversation_prompt()
            response = self.generate(
                prompt=full_prompt,
                system_prompt=full_system,
            )
            
            # Check if model is requesting a skill (simple pattern matching)
            # In production, use actual Vertex Function Calling API
            skill_request = self._detect_skill_request(response)
            
            if skill_request:
                # Model wants to load a skill
                skill_name = skill_request
                self.logger.info(f"🤖 Model requested skill: {skill_name}")
                
                skill_content = self.use_skill(skill_name)
                
                # Add to conversation
                self._conversation_history.append({
                    "role": "assistant",
                    "content": f"I need to load the '{skill_name}' skill for this task."
                })
                skill_msg_id = len(self._conversation_history)
                self._conversation_history.append({
                    "role": "user",
                    "content": f"SYSTEM: {skill_content}"
                })
                self._skill_message_ids.append(skill_msg_id)
                
                skill_calls_made += 1
            else:
                # Model produced final response
                self._conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                if auto_cleanup:
                    self.clear_active_skills(purge_history=True)
                
                return response
        
        # Max skill calls reached, force final response
        self.logger.warning(f"⚠️ Max skill calls ({max_skill_calls}) reached")
        if auto_cleanup:
            self.clear_active_skills(purge_history=True)
        
        return self._conversation_history[-1].get("content", "")
    
    def _build_conversation_prompt(self) -> str:
        """Build prompt from conversation history."""
        parts = []
        for msg in self._conversation_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                parts.append(f"User: {content}")
            else:
                parts.append(f"Assistant: {content}")
        return "\n\n".join(parts)
    
    def _detect_skill_request(self, response: str) -> Optional[str]:
        """
        Detect if the model is requesting a skill.
        
        This is a simple implementation. In production, use Vertex AI
        native Function Calling which returns structured function_call objects.
        
        Returns:
            skill_name if detected, None otherwise
        """
        import re
        
        # Pattern: use_skill("skill-name") or use_skill('skill-name')
        pattern = r'use_skill\s*\(\s*["\']([a-z0-9-]+)["\']\s*\)'
        match = re.search(pattern, response.lower())
        
        if match:
            return match.group(1)
        
        # Also check for explicit request patterns
        patterns = [
            r'I need to load the ["\']?([a-z0-9-]+)["\']? skill',
            r'loading skill:? ["\']?([a-z0-9-]+)["\']?',
            r'activating ["\']?([a-z0-9-]+)["\']? skill',
        ]
        for p in patterns:
            match = re.search(p, response.lower())
            if match:
                return match.group(1)
        
        return None
    
    def reset_conversation(self) -> None:
        """Clear conversation history for a fresh start."""
        self._conversation_history.clear()
        self._skill_message_ids.clear()
        self.logger.debug("🔄 Conversation history reset")
    
    def __repr__(self) -> str:
        skills_info = f", skills={len(self._active_skills)}" if self._active_skills else ""
        history_info = f", turns={len(self._conversation_history)}" if self._conversation_history else ""
        return f"<{self.name} model={self.model}{skills_info}{history_info}>"


class PromptMixin:
    """
    Mixin for common prompting patterns.
    """
    
    @staticmethod
    def format_context(context: str, max_length: int = 2000) -> str:
        """Truncate context if too long."""
        if len(context) > max_length:
            return context[:max_length] + "\n...[truncated]"
        return context
    
    @staticmethod
    def json_instruction() -> str:
        """Standard JSON output instruction."""
        return """
Respond ONLY with valid JSON. No markdown, no explanations.
Do not wrap in ```json``` blocks.
"""
    
    @staticmethod
    def uzbekistan_context() -> str:
        """Standard Uzbekistan market context."""
        return """
Context: Uzbekistan market (35M population)
- Currency: UZS (1 USD ≈ 12,500 UZS)
- Average salary: 3-5M UZS/month
- Key cities: Tashkent, Samarkand, Bukhara
- Languages: Uzbek, Russian
- Growing sectors: IT, Agriculture, E-commerce, EdTech
"""


# === EXAMPLE USAGE ===

if __name__ == "__main__":
    # Demo agent
    class DemoAgent(BaseAgent, PromptMixin):
        name = "DemoAgent"
        model = "gemini-1.5-flash"
        
        def execute(self, input_data: Dict[str, Any]) -> AgentResult:
            prompt = f"""
{self.uzbekistan_context()}

Task: {input_data.get('task', 'Analyze market')}

{self.json_instruction()}
"""
            response = self.generate(prompt, json_output=True)
            return self.build_result(True, {"response": response})
    
    agent = DemoAgent()
    print(agent)
    result = agent.execute({"task": "Find top 3 business ideas"})
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")
