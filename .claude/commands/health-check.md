---
description: Check health of all UZ Factory components
---

# Health Check Command

Verify all system components are working.

## Checks

### 1. API Server
```bash
curl http://localhost:8000/api/health
```

### 2. Configuration
- [ ] GOOGLE_API_KEY set
- [ ] SUPABASE_URL set
- [ ] TELEGRAM_API_ID set

### 3. Agents
- [ ] pain_extractor.py imports OK
- [ ] scoring_engine.py imports OK
- [ ] solution_finder.py imports OK

### 4. n8n Workflows
- [ ] All JSON files valid
- [ ] Telegram credentials configured

### 5. Frontend
- [ ] npm dependencies installed
- [ ] Vite dev server starts

### 6. Database
- [ ] Supabase connection OK
- [ ] Tables exist

## Output
Summary table showing:
| Component | Status | Details |
|-----------|--------|---------|
| API | OK/FAIL | ... |
| Agents | OK/FAIL | ... |
| Database | OK/FAIL | ... |
