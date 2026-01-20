---
description: Create MVP from a pain or idea using UZ Factory pipeline
---

# Create MVP Command

Generate a complete MVP using the FACTORY phase.

## Input
$ARGUMENTS should be the pain/idea description, e.g.:
`/create-mvp Telegram bot for learning English in Uzbekistan`

## Steps

1. **Generate PRD**
   - Use mvp_architect.py pattern
   - Create structured JSON + markdown PRD
   - Save to `data/projects/{project_name}/`

2. **Create Code**
   - Generate FastAPI backend
   - Create Telegram bot if applicable
   - Add database models
   - Generate requirements.txt

3. **Setup Deployment**
   - Create Dockerfile
   - Create docker-compose.yml
   - Add environment template

4. **Output**
   - Project folder path
   - Key files created
   - Next steps for deployment

## Tech Stack Defaults
- Backend: FastAPI + Python 3.11
- Database: Supabase PostgreSQL
- Bot: python-telegram-bot
- Frontend: React + Vite (if needed)
