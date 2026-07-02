export interface Scenario {
  query: string
  cid: string
  hint: string
}

export const SCENARIOS: Record<string, Scenario> = {
  '1 — Dark Mode Setup (Starter)': {
    query: 'How do I enable dark mode in my account?',
    cid: 'CUST-001',
    hint: 'Simple · 1 agent · No escalation',
  },
  '2 — API Access on Starter Plan': {
    query: "I'm on the Starter plan but I need API access for my automation workflow. What are my options?",
    cid: 'CUST-001',
    hint: 'Medium · Account + Feature agents',
  },
  '3 — Pro Plan API Rate Limit Conflict': {
    query:
      'Your documentation says the Pro plan includes unlimited API calls, but I\'m getting rate limit errors after 1000 calls/month. My account shows Pro. Is this a bug or am I misunderstanding something?',
    cid: 'CUST-002',
    hint: 'High · Conflict detection · 3+ agents',
  },
  '4 — SLA Violation — Escalate Now': {
    query:
      'I have been waiting 10 days for a response on a critical production issue. My company has a contract with a 24-hour SLA guarantee. This is costing us $500 per day in lost revenue. Please verify the SLA was violated and escalate immediately.',
    cid: 'CUST-003',
    hint: 'High · P1 escalation · Contract agent',
  },
  '5 — Seat Mismatch After Migration': {
    query:
      'Our company just migrated from a competitor platform. We have 15 users but the plan shows only 10 seats. Can you help me understand the licensing model and set up all our users?',
    cid: 'CUST-004',
    hint: 'Medium · Seat overage · Onboarding',
  },
}

export const SCENARIO_KEYS = Object.keys(SCENARIOS)
