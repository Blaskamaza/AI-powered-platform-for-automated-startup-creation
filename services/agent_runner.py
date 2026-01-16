"""
AgentRunner — Execute agents as isolated subprocesses.

Runs agents in their own process with:
- Isolated environment via worktree
- Logs written to agent.log
- PID tracking for monitoring
"""

import subprocess
import os
import sys
import signal
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger("AgentRunner")


class AgentRunner:
    """
    Runs agents as subprocesses in isolated worktrees.
    
    Usage:
        runner = AgentRunner("task-123", "cpo")
        pid = runner.start()
        print(runner.get_logs())
        runner.stop()
    """
    
    def __init__(self, task_id: str, agent_name: str):
        """
        Initialize runner for specific task and agent.
        
        Args:
            task_id: Task identifier (e.g., "delivery-456")
            agent_name: Agent module name (e.g., "cpo", "tech_lead")
        """
        self.task_id = task_id
        self.agent_name = agent_name
        self.worktree = Path(f"worktrees/feat-{task_id}")
        self.log_file = self.worktree / "agent.log"
        self.pid_file = self.worktree / "agent.pid"
        self.process: Optional[subprocess.Popen] = None
    
    def start(self, extra_env: Optional[Dict[str, str]] = None) -> int:
        """
        Start agent in background process.
        
        Args:
            extra_env: Additional environment variables
            
        Returns:
            Process ID
        """
        if not self.worktree.exists():
            raise AgentRunnerError(f"Worktree not found: {self.worktree}")
        
        # Check if already running
        if self.is_running():
            raise AgentRunnerError(f"Agent already running with PID {self.get_pid()}")
        
        # Build environment
        env = os.environ.copy()
        env.update({
            "AGENT_TASK_ID": self.task_id,
            "AGENT_NAME": self.agent_name,
            "PYTHONPATH": str(Path.cwd()),  # Project root
            "PYTHONUNBUFFERED": "1",  # Disable output buffering
        })
        if extra_env:
            env.update(extra_env)
        
        # Get Python executable
        python_exe = sys.executable
        
        # Build command
        # Try to run agent as module: python -m agents.{agent_name}
        cmd = [python_exe, "-m", f"agents.{self.agent_name}"]
        
        logger.info(f"🚀 Starting agent: {' '.join(cmd)}")
        logger.info(f"📂 Working directory: {self.worktree}")
        
        # Open log file
        log_handle = open(self.log_file, "w", encoding="utf-8")
        
        # Write header
        log_handle.write(f"=== Agent: {self.agent_name} | Task: {self.task_id} ===\n")
        log_handle.write(f"=== Started: {datetime.now().isoformat()} ===\n")
        log_handle.write("-" * 50 + "\n")
        log_handle.flush()
        
        # Start process
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.worktree),
                env=env,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                # Windows doesn't support preexec_fn
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
            )
            
            # Save PID
            self.pid_file.write_text(str(self.process.pid))
            
            logger.info(f"✅ Agent started with PID: {self.process.pid}")
            return self.process.pid
            
        except FileNotFoundError:
            log_handle.close()
            raise AgentRunnerError(f"Agent module not found: agents.{self.agent_name}")
        except Exception as e:
            log_handle.close()
            raise AgentRunnerError(f"Failed to start agent: {e}")
    
    def stop(self, timeout: float = 5.0) -> bool:
        """
        Stop running agent.
        
        Args:
            timeout: Seconds to wait before force kill
            
        Returns:
            True if stopped cleanly, False if force killed
        """
        pid = self.get_pid()
        if not pid:
            logger.warning("No agent running")
            return True
        
        try:
            # Try graceful termination
            if os.name == 'nt':
                # Windows
                subprocess.run(["taskkill", "/PID", str(pid)], capture_output=True)
            else:
                # Unix
                os.kill(pid, signal.SIGTERM)
            
            # Wait for process to exit
            start = time.time()
            while time.time() - start < timeout:
                if not self._process_exists(pid):
                    self._cleanup()
                    logger.info(f"✅ Agent stopped gracefully (PID: {pid})")
                    return True
                time.sleep(0.1)
            
            # Force kill
            if os.name == 'nt':
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
            else:
                os.kill(pid, signal.SIGKILL)
            
            self._cleanup()
            logger.warning(f"⚠️ Agent force killed (PID: {pid})")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error stopping agent: {e}")
            self._cleanup()
            return False
    
    def is_running(self) -> bool:
        """Check if agent is currently running."""
        pid = self.get_pid()
        if not pid:
            return False
        return self._process_exists(pid)
    
    def get_pid(self) -> Optional[int]:
        """Get PID of running agent."""
        if self.pid_file.exists():
            try:
                return int(self.pid_file.read_text().strip())
            except ValueError:
                return None
        return None
    
    def get_logs(self, tail: int = 50) -> str:
        """
        Get recent log lines.
        
        Args:
            tail: Number of lines to return
            
        Returns:
            Log content
        """
        if not self.log_file.exists():
            return "No logs yet"
        
        try:
            with open(self.log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            return "".join(lines[-tail:])
        except Exception as e:
            return f"Error reading logs: {e}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "task_id": self.task_id,
            "agent": self.agent_name,
            "running": self.is_running(),
            "pid": self.get_pid(),
            "worktree": str(self.worktree),
            "log_file": str(self.log_file),
        }
    
    def wait(self, timeout: Optional[float] = None) -> int:
        """
        Wait for agent to complete.
        
        Args:
            timeout: Max seconds to wait (None = forever)
            
        Returns:
            Exit code
        """
        if self.process:
            try:
                return self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                return -1
        return -1
    
    # === Private Methods ===
    
    def _process_exists(self, pid: int) -> bool:
        """Check if process with PID exists."""
        try:
            if os.name == 'nt':
                # Windows
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True, text=True
                )
                return str(pid) in result.stdout
            else:
                # Unix
                os.kill(pid, 0)
                return True
        except (OSError, ProcessLookupError):
            return False
    
    def _cleanup(self):
        """Clean up PID file."""
        if self.pid_file.exists():
            self.pid_file.unlink()


# === Exceptions ===

class AgentRunnerError(Exception):
    """Agent runner error."""
    pass


# === API Endpoints ===

def create_agent_api_router():
    """Create FastAPI router for agent control."""
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
    
    router = APIRouter(prefix="/api/agent", tags=["agent"])
    
    class RunRequest(BaseModel):
        task_id: str
        agent: str
    
    @router.post("/run")
    def start_agent(request: RunRequest):
        """Start an agent for a task."""
        runner = AgentRunner(request.task_id, request.agent)
        try:
            pid = runner.start()
            return {"status": "started", "pid": pid, "task_id": request.task_id}
        except AgentRunnerError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post("/stop/{task_id}")
    def stop_agent(task_id: str, agent: str = "unknown"):
        """Stop a running agent."""
        runner = AgentRunner(task_id, agent)
        stopped = runner.stop()
        return {"status": "stopped" if stopped else "killed", "task_id": task_id}
    
    @router.get("/status/{task_id}")
    def get_agent_status(task_id: str, agent: str = "unknown"):
        """Get agent status."""
        runner = AgentRunner(task_id, agent)
        return runner.get_status()
    
    @router.get("/logs/{task_id}")
    def get_agent_logs(task_id: str, agent: str = "unknown", tail: int = 50):
        """Get agent logs."""
        runner = AgentRunner(task_id, agent)
        return {"logs": runner.get_logs(tail)}
    
    return router


# === CLI ===

if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    parser = argparse.ArgumentParser(description="Agent Runner CLI")
    parser.add_argument("command", choices=["start", "stop", "status", "logs"])
    parser.add_argument("task_id", help="Task ID")
    parser.add_argument("--agent", "-a", default="cpo", help="Agent name")
    parser.add_argument("--tail", "-n", type=int, default=50, help="Lines for logs")
    
    args = parser.parse_args()
    runner = AgentRunner(args.task_id, args.agent)
    
    if args.command == "start":
        try:
            pid = runner.start()
            print(f"✅ Agent started with PID: {pid}")
        except AgentRunnerError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "stop":
        runner.stop()
        print(f"✅ Agent stopped")
    
    elif args.command == "status":
        status = runner.get_status()
        print(f"Task:    {status['task_id']}")
        print(f"Agent:   {status['agent']}")
        print(f"Running: {status['running']}")
        print(f"PID:     {status['pid']}")
    
    elif args.command == "logs":
        print(runner.get_logs(args.tail))
