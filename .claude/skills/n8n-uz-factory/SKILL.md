---
name: n8n-uz-factory
description: Creates n8n workflows following UZ AI Factory patterns. Includes templates for pain scanning, MVP generation, and social publishing.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# n8n UZ Factory

You are an expert at creating n8n workflows for UZ AI Factory automation.

## When to Activate
- Creating new n8n workflows
- Modifying existing workflows in `n8n-cloudflare/`
- Connecting n8n to FastAPI backend
- Setting up Telegram notifications

## Existing Workflows Reference
```
n8n-cloudflare/
├── master_orchestrator.json    # Weekly Boss trigger
├── pain_scanner.json           # Daily pain discovery
├── mvp_generator.json          # MVP creation pipeline
├── content_engine.json         # Marketing content
├── social_publisher.json       # Multi-platform posting
├── feedback_collector.json     # Telegram feedback
├── deep_research_agent.json    # Multi-source research
├── groq_research_agent.json    # Cost-optimized research
└── qualifizer_router_v2.json   # Intent routing
```

## Workflow Patterns

### Pattern 1: Webhook → API → Telegram
```json
{
  "nodes": [
    {"type": "webhook", "path": "/trigger"},
    {"type": "httpRequest", "url": "http://host.docker.internal:8000/api/..."},
    {"type": "telegram", "chatId": "-1002268798360"}
  ]
}
```

### Pattern 2: Schedule → Scan → Store
```json
{
  "nodes": [
    {"type": "scheduleTrigger", "cron": "0 9 * * *"},
    {"type": "httpRequest", "url": ".../api/radar/analyze"},
    {"type": "supabase", "operation": "upsert"}
  ]
}
```

### Pattern 3: AI Agent Flow
```json
{
  "nodes": [
    {"type": "webhook"},
    {"type": "openAi", "model": "gpt-4"},  // or Gemini via HTTP
    {"type": "code", "language": "javascript"},
    {"type": "telegram"}
  ]
}
```

## Standard Configuration

### API Base URL
- Docker: `http://host.docker.internal:8000`
- Local: `http://localhost:8000`

### Telegram Bot
- Chat ID: `-1002268798360` (admin notifications)
- Credentials: `telegramApi` (ID: 1)

### Error Handling
Always include:
```json
{
  "type": "errorTrigger",
  "position": [x, y]
},
{
  "type": "telegram",
  "text": "Error in {{$workflow.name}}: {{$json.error.message}}"
}
```

## API Endpoints for n8n

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/boss/start` | POST | Full lifecycle |
| `/api/radar/analyze` | POST | Pain analysis |
| `/api/factory/run` | POST | MVP creation |
| `/api/launchpad/campaign` | POST | Marketing |
| `/api/health` | GET | Health check |

## Workflow Naming Convention
```
{domain}_{action}.json
Examples:
- pain_scanner.json
- mvp_generator.json
- social_publisher.json
- feedback_collector.json
```

## Node Connection Pattern
```json
"connections": {
  "NodeA": {
    "main": [[{"node": "NodeB", "type": "main", "index": 0}]]
  }
}
```

## Testing Workflows
1. Use n8n test webhooks
2. Check `api/server.py` endpoint exists
3. Verify Telegram credentials
4. Test with dry-run first
