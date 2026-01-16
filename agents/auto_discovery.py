"""
Auto-Discovery Pipeline — Automatically discovers new pains and creates tasks.

This is the future of UZ AI Factory:
- Scans Telegram channels for pains
- Checks Xarid.uz for procurement opportunities
- Creates tasks automatically
- Runs CPO agent
- Auto-merges if XP > threshold

Usage:
    # Manual run
    python agents/auto_discovery.py --dry-run
    
    # Cron (daily at 9 AM, Mon-Fri)
    0 9 * * 1-5 cd /home/uz/uz-ai-factory && python agents/auto_discovery.py
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.workspace_manager import WorkspaceManager
from services.agent_runner import AgentRunner
from config import V2_MAX_PARALLEL_TASKS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("AutoDiscovery")


class AutoDiscovery:
    """
    Autonomous pain discovery and task creation.
    """
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.workspace_manager = WorkspaceManager()
        self.max_tasks_per_day = 5
        self.xp_threshold_for_merge = 80
        self.processed_file = Path("data/processed_pains.json")
    
    def run_daily(self):
        """Main daily pipeline."""
        logger.info("=" * 60)
        logger.info("🔍 AUTO-DISCOVERY PIPELINE STARTED")
        logger.info("=" * 60)
        
        # 1. Scan for pains
        pains = self.scan_all_sources()
        logger.info(f"Found {len(pains)} pains")
        
        # 2. Filter already processed
        new_pains = [p for p in pains if not self.already_processed(p)]
        logger.info(f"New pains: {len(new_pains)}")
        
        if not new_pains:
            logger.info("No new pains to process")
            return
        
        # 3. Limit to max per day
        to_process = new_pains[:self.max_tasks_per_day]
        logger.info(f"Processing {len(to_process)} pains today")
        
        # 4. Create tasks and run agents
        created = []
        for pain in to_process:
            task_id = self.create_task_from_pain(pain)
            if task_id:
                created.append(task_id)
                self.mark_as_processed(pain)
        
        logger.info(f"Created {len(created)} tasks")
        
        # 5. Wait for completion and auto-merge
        for task_id in created:
            self.wait_and_evaluate(task_id)
        
        logger.info("=" * 60)
        logger.info("🏁 AUTO-DISCOVERY PIPELINE COMPLETED")
        logger.info("=" * 60)
    
    def scan_all_sources(self) -> List[Dict]:
        """Scan all sources for pains."""
        pains = []
        
        # Telegram (mock for now)
        pains.extend(self.scan_telegram())
        
        # Xarid.uz (mock for now)
        pains.extend(self.scan_xarid())
        
        # Local DEV_LOG pains
        pains.extend(self.scan_dev_log())
        
        return pains
    
    def scan_telegram(self) -> List[Dict]:
        """
        Scan Telegram channels for pains.
        TODO: Integrate with tg_scanner.py
        """
        logger.info("📱 Scanning Telegram channels...")
        
        # Mock data — in production, use tg_scanner
        return [
            {"source": "telegram", "text": "Нужна автоматизация для фермеров Ферганы", "channel": "uzb_business"},
            {"source": "telegram", "text": "Проблема с учётом товаров на складах", "channel": "logistics_uz"},
        ]
    
    def scan_xarid(self) -> List[Dict]:
        """
        Scan Xarid.uz for procurement opportunities.
        TODO: Integrate with xarid_scanner.py
        """
        logger.info("📋 Scanning Xarid.uz...")
        
        # Mock data — in production, use xarid_scanner
        return [
            {"source": "xarid", "text": "Тендер на систему мониторинга теплиц", "tender_id": "XT-2026-001"},
        ]
    
    def scan_dev_log(self) -> List[Dict]:
        """Scan DEV_LOG for documented pains."""
        logger.info("📓 Scanning DEV_LOG...")
        
        dev_log_path = Path("DEV_LOG.md")
        if not dev_log_path.exists():
            return []
        
        pains = []
        try:
            content = dev_log_path.read_text(encoding="utf-8")
            # Extract pains section (simple parsing)
            if "## Боли" in content or "## Pains" in content:
                lines = content.split("\n")
                in_pains = False
                for line in lines:
                    if "## Боли" in line or "## Pains" in line:
                        in_pains = True
                        continue
                    if in_pains and line.startswith("##"):
                        break
                    if in_pains and line.strip().startswith("- "):
                        pain_text = line.strip()[2:]
                        pains.append({"source": "dev_log", "text": pain_text})
        except Exception as e:
            logger.warning(f"Error scanning DEV_LOG: {e}")
        
        return pains
    
    def already_processed(self, pain: Dict) -> bool:
        """Check if pain was already processed."""
        pain_hash = self.get_pain_hash(pain)
        
        if not self.processed_file.exists():
            return False
        
        try:
            processed = json.loads(self.processed_file.read_text())
            return pain_hash in processed.get("hashes", [])
        except:
            return False
    
    def mark_as_processed(self, pain: Dict):
        """Mark pain as processed."""
        if self.dry_run:
            return
        
        pain_hash = self.get_pain_hash(pain)
        
        self.processed_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.processed_file.exists():
            processed = json.loads(self.processed_file.read_text())
        else:
            processed = {"hashes": [], "history": []}
        
        processed["hashes"].append(pain_hash)
        processed["history"].append({
            "hash": pain_hash,
            "pain": pain,
            "date": datetime.now().isoformat()
        })
        
        self.processed_file.write_text(json.dumps(processed, indent=2, ensure_ascii=False))
    
    def get_pain_hash(self, pain: Dict) -> str:
        """Generate unique hash for pain."""
        text = pain.get("text", "")
        return hashlib.md5(text.encode()).hexdigest()[:12]
    
    def create_task_from_pain(self, pain: Dict) -> Optional[str]:
        """Create a task from discovered pain."""
        pain_text = pain.get("text", "Unknown pain")
        source = pain.get("source", "unknown")
        
        # Generate task ID
        pain_hash = self.get_pain_hash(pain)
        task_id = f"auto-{pain_hash}"
        
        logger.info(f"\n📦 Creating task: {task_id}")
        logger.info(f"   Source: {source}")
        logger.info(f"   Pain: {pain_text[:50]}...")
        
        if self.dry_run:
            logger.info("   [DRY RUN] Would create task")
            return task_id
        
        try:
            worktree = self.workspace_manager.create(task_id, pain_text, "cpo")
            logger.info(f"   ✅ Created: {worktree}")
            
            # Start agent
            runner = AgentRunner(task_id, "cpo")
            runner.start()
            logger.info(f"   🚀 Agent started")
            
            return task_id
            
        except Exception as e:
            logger.error(f"   ❌ Failed: {e}")
            return None
    
    def wait_and_evaluate(self, task_id: str, timeout: int = 300):
        """Wait for task completion and evaluate for auto-merge."""
        logger.info(f"\n⏳ Waiting for {task_id}...")
        
        if self.dry_run:
            logger.info("   [DRY RUN] Would wait and evaluate")
            return
        
        runner = AgentRunner(task_id, "cpo")
        success = runner.wait_for_completion(timeout=timeout)
        
        if not success:
            logger.warning(f"   ❌ Task failed or timed out")
            return
        
        # Check XP
        meta = self.workspace_manager.get_meta(task_id)
        xp = meta.get("xp_reward", 0) or 0
        
        logger.info(f"   ✅ Completed with XP: {xp}")
        
        if xp >= self.xp_threshold_for_merge:
            logger.info(f"   🎉 XP >= {self.xp_threshold_for_merge}, auto-merging!")
            # TODO: Call tools/review.py --auto-merge
            # For now, just log
            self.workspace_manager.update_meta(task_id, {"status": "approved"})
        else:
            logger.info(f"   📋 XP < {self.xp_threshold_for_merge}, needs manual review")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-Discovery Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Don't create tasks")
    
    args = parser.parse_args()
    
    discovery = AutoDiscovery(dry_run=args.dry_run)
    discovery.run_daily()
