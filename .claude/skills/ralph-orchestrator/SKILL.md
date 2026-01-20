---
name: ralph-orchestrator
description: Self-correcting agent orchestration using Ralph Loop pattern. Handles retries, oscillation detection, and graceful degradation.
allowed-tools: Bash, Read, Write, Edit
---

# Ralph Orchestrator

You are an expert at autonomous agent orchestration using the Ralph Loop pattern.

## When to Activate
- Running multi-step agent pipelines
- Handling agent failures or retries
- Detecting and preventing infinite loops
- Orchestrating RADAR → FACTORY → LAUNCHPAD

## Ralph Loop Pattern

```python
# From agents/ralph_loop.py
for iteration in range(max_iterations):
    result = agent.execute(task)

    if result.status == "COMPLETE":
        return result  # Success!

    # Oscillation detection
    if similarity(result, previous_results) > 0.90:
        return emergency_stop()

    # Sliding window - only keep last error
    context = original_task + last_error_only

    await sleep(2)  # Rate limiting
```

## Key Principles

### 1. Sliding Window Context
- Keep ONLY original task + last error
- Never accumulate all errors (context pollution)
- Reset context on success

### 2. Oscillation Detection
- Track ALL previous outputs
- If output repeats with >90% similarity = STOP
- Use MD5 hashes for quick comparison

### 3. Emergency Stops
- Max 5 iterations per task
- Similarity threshold: 90%
- Timeout: 300 seconds
- Rate limit: 2s between iterations

### 4. Graceful Degradation
- If agent fails → try fallback mock data
- If API down → use cached results
- Always return something useful

## Integration with UZ Factory

### Boss Orchestrator Flow
```
TheBoss.execute(goal)
├── RADAR Phase
│   └── RalphLoop(PainExtractor, max=3)
├── FACTORY Phase
│   ├── RalphLoop(MVPArchitect, max=3)
│   ├── RalphLoop(Coder, max=5)
│   └── RalphLoop(QALead, max=2)
└── LAUNCHPAD Phase
    └── RalphLoop(CMO + Copywriter, max=3)
```

### AutoDiscovery Flow
```
Daily Trigger
├── scan_telegram() → fallback if fails
├── scan_xarid() → fallback if fails
├── For each pain:
│   └── RalphLoop(CPO, max=3)
└── Auto-merge if XP >= 80
```

## Telemetry
Log for each loop:
- `loop_id`: UUID
- `iterations`: Count
- `stopped_reason`: complete|max_iterations|oscillation|emergency
- `total_tokens`: Cost tracking
- `elapsed_seconds`: Performance

## Error Handling Patterns
```python
try:
    result = await agent.execute()
except RateLimitError:
    await exponential_backoff()
except APIError:
    result = get_fallback_data()
except Exception as e:
    log_error(e)
    result = AgentResult(success=False, error=str(e))
```
