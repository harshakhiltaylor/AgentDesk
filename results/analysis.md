# AgentDesk — System Analysis

## What We Built

AgentDesk is a 5-agent multi-agent customer support intelligence system for AgentDesk SaaS.

### Architecture Summary

```
Customer Query
      │
      ▼
 OrchestratorAgent  ◄──── builds investigation plan via LLM
      │
      ├── AccountAgent    (plan, billing, seats, status)
      ├── FeatureAgent    (availability, docs, limits)
      ├── ContractAgent   (SLA, entitlements, violations)
      └── EscalationAgent (final decision, ticket creation)
            │
            ▼
     SharedContext (shared memory across all agents)
            │
            ▼
     Final Customer Response
```

### Key Design Decisions

**1. LLM-driven Planning (not if-else routing)**
The Orchestrator calls Claude to decide which agents to invoke and in what order.
This allows emergent routing — e.g., a query about "API limits on Pro" triggers
AccountAgent + FeatureAgent + ContractAgent, not just FeatureAgent.

**2. SharedContext as memory backbone**
All agents read from and write to a single SharedContext object per session.
This means FeatureAgent can see AccountAgent's findings before running,
allowing it to tailor its investigation.

**3. Conflict detection is structural, not LLM-only**
When FeatureAgent detects the `api_access` documentation vs. system mismatch,
it writes to `ctx.conflicts` directly. The Orchestrator then reasons about
this conflict in the synthesis step.

**4. Graceful degradation everywhere**
Every tool call is wrapped in `_safe_tool_call()` which returns a fallback
value on failure. The 8% random failure rate simulates real-world DB issues.

**5. EscalationAgent is always last**
It has full context of all prior findings, conflicts, and signals from
ContractAgent. This avoids premature escalation decisions.

---

## Scenario Results Summary

### Scenario 1: Dark Mode Setup
- **Plan invoked**: FeatureAgent → EscalationAgent
- **Complexity**: Low
- **Escalated**: No
- **Key behavior**: Correctly routed to FeatureAgent only; returned step-by-step setup instructions

### Scenario 2: API on Starter Plan
- **Plan invoked**: AccountAgent → FeatureAgent → EscalationAgent
- **Complexity**: Medium
- **Escalated**: No (upgrade suggestion only)
- **Key behavior**: AccountAgent confirmed Starter plan; FeatureAgent confirmed API not available; synthesis recommended Pro upgrade

### Scenario 3: Rate Limit Conflict
- **Plan invoked**: AccountAgent → FeatureAgent → ContractAgent → EscalationAgent
- **Complexity**: High
- **Escalated**: Maybe (if bug confirmed) / No (if doc error)
- **Conflicts Detected**: 1 — marketing docs vs. system data (api_rate_limit)
- **Key behavior**: System correctly flagged doc error. Conflict resolved in favor of system data (1,000/month limit is real). Response explained the discrepancy clearly.

### Scenario 4: SLA Violation
- **Plan invoked**: AccountAgent → ContractAgent → EscalationAgent
- **Complexity**: High
- **Escalated**: YES (P1)
- **Key behavior**: ContractAgent ran SLA compliance check; hours_elapsed >> sla_hours; escalation flagged; P1 ticket created for Customer Success team

### Scenario 5: Seat Overage
- **Plan invoked**: AccountAgent → FeatureAgent → EscalationAgent
- **Complexity**: Medium
- **Escalated**: No (recommended Onboarding specialist optionally)
- **Key behavior**: AccountAgent detected seats_used (15) > seats (10); FeatureAgent explained licensing; synthesis provided upgrade path and setup guidance

---

## What We'd Improve

1. **Parallel agent execution** — AccountAgent and FeatureAgent could run concurrently using asyncio
2. **Vector memory** — Store past customer interactions in a vector DB for context retrieval
3. **Streaming responses** — Stream the final response token-by-token to the UI
4. **Human-in-the-loop** — Add a mechanism for escalated tickets to come back into the system with human feedback
5. **Richer conflict resolution** — Use a dedicated arbitration step with source reliability scoring

## Learnings

- LLM-driven planning is significantly more flexible than rule-based routing but adds ~500ms latency per query
- SharedContext as a plain Python dataclass is simple and testable — no Redis/DB needed for MVP
- The 8% random failure rate revealed several edge cases in the `_safe_tool_call` wrapper that needed fixing
- Conflict detection is best done structurally (in tool layer) rather than only via LLM reasoning
