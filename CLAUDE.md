# UZ AI FACTORY — Claude Code Configuration

## Project Overview
**UZ AI Factory** — автономная AI-фабрика стартапов для узбекского рынка.

**Архитектура:** 3-фазный pipeline
1. **RADAR** — Сканирование болей (Telegram, YouTube, Xarid.uz, RSS)
2. **FACTORY** — Создание MVP (PRD → Code → Deploy)
3. **LAUNCHPAD** — Запуск (Marketing → Content → Social)

## Tech Stack
- **Backend:** Python 3.11 + FastAPI
- **Frontend:** React 19 + Vite + TypeScript + Tailwind
- **Database:** Supabase PostgreSQL
- **AI Models:** Gemini 2.0 Flash (via Vertex AI)
- **Orchestration:** n8n workflows
- **State:** Zustand (frontend), Git worktrees (tasks)

## Key Directories
```
agents/           # AI agents (Python)
  ├── boss.py           # Meta-orchestrator
  ├── ralph_loop.py     # Self-correcting loop
  ├── pain_extractor.py # 2-stage pain analysis
  ├── scoring_engine.py # 7-criteria scoring
  ├── solution_finder.py # GitHub/n8n/HuggingFace search
  └── auto_discovery.py  # Daily pipeline

services/         # Supporting services
  ├── workspace_manager.py  # Git worktree isolation
  ├── agent_runner.py       # Subprocess execution
  └── supabase_client.py    # Database client

api/              # FastAPI endpoints
  └── server.py           # Main API (500+ lines)

n8n-cloudflare/   # n8n workflows (9 files)
src/              # React frontend
data/             # Scan results, projects
```

## Coding Standards

### Python
- Use type hints: `def func(x: str) -> dict:`
- Docstrings for public functions
- Async where possible (`async def`)
- Error handling with try/except
- Logging via `self.logger`

### TypeScript/React
- Functional components with hooks
- Zustand for state management
- Tailwind for styling
- No inline styles

### Git
- Conventional commits: `feat:`, `fix:`, `refactor:`
- Branch naming: `feat/task-{id}`
- Always include Co-Authored-By

## Agent Pattern
All agents inherit from `BaseAgent`:
```python
class MyAgent(BaseAgent):
    name = "MyAgent"
    model = GEMINI_FLASH_MODEL

    def execute(self, input_data: dict) -> AgentResult:
        # ... logic
        return self.build_result(success=True, data={...})
```

## Ralph Loop Pattern
For fault-tolerant agent execution:
```python
# Max 5 iterations, 90% similarity = stop
result = await ralph_loop(
    agent_func=my_agent.execute,
    task=input_data,
    max_iterations=5
)
```

## n8n Workflow Pattern
```json
{
  "nodes": [
    {"type": "webhook", "path": "/trigger"},
    {"type": "httpRequest", "url": "http://host.docker.internal:8000/api/..."},
    {"type": "telegram", "chatId": "-1002268798360"}
  ]
}
```

## API Endpoints (Key)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/boss/start` | POST | Full lifecycle |
| `/api/radar/analyze` | POST | Pain analysis |
| `/api/factory/run` | POST | MVP creation |
| `/api/board/tasks` | GET/POST | Kanban tasks |
| `/api/health` | GET | System status |

## Environment Variables
Required in `.env`:
```
GOOGLE_API_KEY=...
VERTEX_PROJECT_ID=...
SUPABASE_URL=...
SUPABASE_KEY=...
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
```

## Testing Commands
```bash
# Backend
python api/server.py                    # Start API
python agents/auto_discovery.py --dry-run  # Test discovery

# Frontend
npm run dev                             # Start React
npm run build                           # Production build
```

## Common Tasks

### Create New Agent
1. Create `agents/my_agent.py`
2. Inherit from `BaseAgent`
3. Implement `execute()` method
4. Add to `agents/run_all.py` if needed

### Create New n8n Workflow
1. Create `n8n-cloudflare/my_workflow.json`
2. Follow existing patterns (webhook → API → telegram)
3. Test locally before deploy

### Add New Pain Source
1. Create scanner in `agents/`
2. Add to `auto_discovery.py` `scan_all_sources()`
3. Update config if needed

## Skills Available
- `uz-pain-analyzer` — UZ market analysis
- `uz-mvp-generator` — MVP creation
- `ralph-orchestrator` — Agent orchestration
- `n8n-uz-factory` — n8n workflow creation
- `n8n-skills/*` — 7 n8n skills
- `superpowers/*` — Core dev skills
- `wshobson-agents/*` — 100+ agents

## Do NOT
- Commit `.env` or `credentials.json`
- Push directly to main without review
- Use synchronous code where async is possible
- Hardcode API keys or secrets
- Skip error handling

## Do
- Use existing agent patterns
- Follow Ralph Loop for retries
- Log important actions
- Test with --dry-run first
- Update DEV_LOG.md after changes
