export const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:5001') + '/api'

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Customer {
  id: string
  name: string
  company: string
  plan: string
  status: string
}

export interface Finding {
  agent: string
  finding: string
  confidence: 'high' | 'medium' | 'low'
  data?: Record<string, unknown>
}

export interface Decision {
  decision_point: string
  made_by: string
  choice: string
  reasoning: string
}

export interface Conflict {
  source_a: string
  source_b: string
  description: string
  resolution: string
}

export interface EscalationTicket {
  ticket_id: string
  priority: string
  created_at: string
  reason: string
}

export interface InvestigationResult {
  success: boolean
  session_id?: string
  response?: string
  plan?: string[]
  plan_reasoning?: string
  complexity?: 'low' | 'medium' | 'high'
  escalated?: boolean
  escalation_ticket?: EscalationTicket | null
  conflicts?: Conflict[]
  findings?: Finding[]
  decisions?: Decision[]
  error?: string
}

// ─── API calls ──────────────────────────────────────────────────────────────

export async function getHealth(): Promise<{ status: string; stack: string }> {
  const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(4000) })
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`)
  return res.json()
}

export async function getCustomers(): Promise<Customer[]> {
  const res = await fetch(`${API_BASE}/customers`, { signal: AbortSignal.timeout(6000) })
  if (!res.ok) throw new Error(`Failed to fetch customers: ${res.status}`)
  return res.json()
}

export async function postQuery(
  query: string,
  customerId: string | null,
): Promise<InvestigationResult> {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, customer_id: customerId }),
    signal: AbortSignal.timeout(180000),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error ?? `Request failed: ${res.status}`)
  return data
}
