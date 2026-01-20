---
description: Run the full RADAR → FACTORY → LAUNCHPAD pipeline
---

# Run Boss Command

Execute the complete UZ Factory lifecycle.

## Steps

1. **RADAR Phase** (Discovery)
   - Scan all pain sources
   - Score and rank pains
   - Select top opportunity

2. **FACTORY Phase** (Creation)
   - Generate PRD from selected pain
   - Create MVP code
   - Setup deployment

3. **LAUNCHPAD Phase** (Growth)
   - Generate marketing strategy
   - Create social media content
   - Schedule publications

## Arguments
$ARGUMENTS can specify:
- `--dry-run` - Don't create actual files
- `--skip-radar` - Use existing pain
- `--pain "description"` - Start with specific pain

## Output
- Complete project in `data/projects/`
- Marketing materials
- n8n workflow for automation
- Deployment instructions

## Logs
All actions logged to:
- Console output
- `logs/journal.md`
- Telegram notifications (if configured)
