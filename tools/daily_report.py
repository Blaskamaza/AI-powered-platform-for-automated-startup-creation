"""
Daily Report — Generate daily metrics report.

Run via cron:
    0 23 * * * python tools/daily_report.py >> /var/log/factory_daily.log

Creates a summary of tasks processed in the last 24 hours.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.workspace_manager import WorkspaceManager


def generate_daily_report(output_file: str = None):
    """Generate daily metrics report."""
    wm = WorkspaceManager()
    workspaces = wm.list_workspaces()
    
    now = datetime.now()
    yesterday = now - timedelta(hours=24)
    
    # Filter to last 24 hours
    recent = []
    for ws in workspaces:
        meta = ws.get("meta", {})
        created_str = meta.get("created_at")
        if created_str:
            try:
                created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                if created.replace(tzinfo=None) > yesterday:
                    recent.append(ws)
            except:
                pass
    
    # Count by status
    completed = sum(1 for w in recent if w.get("meta", {}).get("status") == "completed")
    failed = sum(1 for w in recent if w.get("meta", {}).get("status") == "failed")
    running = sum(1 for w in recent if w.get("meta", {}).get("status") == "running")
    backlog = sum(1 for w in recent if w.get("meta", {}).get("status") == "backlog")
    
    # XP
    total_xp = sum(w.get("meta", {}).get("xp_reward", 0) or 0 for w in recent)
    
    # Durations
    durations = []
    for ws in recent:
        meta = ws.get("meta", {})
        created = meta.get("created_at")
        updated = meta.get("updated_at")
        if created and updated and meta.get("status") == "completed":
            try:
                start = datetime.fromisoformat(created.replace("Z", "+00:00"))
                end = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                durations.append((end - start).total_seconds())
            except:
                pass
    
    avg_duration = sum(durations) / len(durations) if durations else 0
    success_rate = (completed / len(recent) * 100) if recent else 0
    
    report = {
        "date": now.strftime("%Y-%m-%d"),
        "period": "24h",
        "tasks": {
            "total": len(recent),
            "completed": completed,
            "failed": failed,
            "running": running,
            "backlog": backlog
        },
        "metrics": {
            "success_rate": f"{success_rate:.1f}%",
            "avg_duration_seconds": round(avg_duration, 1),
            "avg_duration_minutes": round(avg_duration / 60, 1),
            "total_xp": total_xp
        }
    }
    
    # Output
    output = f"""
================================================================================
📊 DAILY REPORT — {now.strftime("%Y-%m-%d %H:%M")}
================================================================================

Tasks (last 24h):
  Total:     {len(recent)}
  Completed: {completed}
  Failed:    {failed}
  Running:   {running}
  Backlog:   {backlog}

Metrics:
  Success Rate: {success_rate:.1f}%
  Avg Duration: {avg_duration:.0f}s ({avg_duration/60:.1f}m)
  Total XP:     {total_xp}

================================================================================
"""
    
    print(output)
    print("JSON:")
    print(json.dumps(report, indent=2))
    
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(output)
            f.write(json.dumps(report) + "\n")
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Report")
    parser.add_argument("--output", "-o", help="Append to file")
    
    args = parser.parse_args()
    generate_daily_report(args.output)
