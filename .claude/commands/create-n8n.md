---
description: Create n8n workflow using UZ Factory patterns
---

# Create n8n Workflow Command

Generate a new n8n workflow following project patterns.

## Input
$ARGUMENTS should describe the workflow, e.g.:
`/create-n8n Daily Telegram channel scanner with Supabase storage`

## Workflow Patterns Available

1. **Webhook → API → Telegram**
   - Trigger: HTTP webhook
   - Action: Call FastAPI endpoint
   - Notify: Telegram message

2. **Schedule → Scan → Store**
   - Trigger: Cron schedule
   - Action: Run scanner
   - Store: Supabase insert

3. **Telegram → Process → Respond**
   - Trigger: Telegram message
   - Action: AI processing
   - Respond: Reply to user

## Output
- JSON workflow file in `n8n-cloudflare/`
- Connection to existing API endpoints
- Telegram notifications configured
- Error handling included

## Reference Workflows
- pain_scanner.json (scheduled scan)
- social_publisher.json (multi-trigger)
- feedback_collector.json (Telegram trigger)
