---
description: Scan Uzbekistan market for pains using all available sources
---

# Scan Pains Command

Run the UZ AI Factory pain discovery pipeline.

## Steps

1. **Check Available Sources**
   - Verify Telegram scanner is configured
   - Check Xarid.uz accessibility
   - Verify Perplexity API key

2. **Execute Scan**
   ```bash
   cd agents && python auto_discovery.py --dry-run
   ```

3. **Analyze Results**
   - Load data from `data/fresh/`
   - Run pain_extractor.py for scoring
   - Display top 10 pains with scores

4. **Output Format**
   For each pain found:
   - Pain description
   - Category (Education/Work/Finance/etc)
   - Score (0-100)
   - Source (Telegram/Xarid/RSS)
   - Business idea suggestion

$ARGUMENTS will be used as filter (e.g., "IT" to filter IT-related pains)
