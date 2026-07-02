import { useState } from 'react'
import {
  Clock, Bot, BarChart2, AlertTriangle, CheckCircle2, AlertOctagon,
  GitFork, MessageSquare, Ticket, Target, Search, ChevronDown,
  ChevronRight, FileJson, CheckCheck,
} from 'lucide-react'
import { InvestigationResult, Finding, Decision, Conflict } from '../lib/api'

interface ResultsPanelProps {
  data: InvestigationResult
  elapsed: number
}

export default function ResultsPanel({ data, elapsed }: ResultsPanelProps) {
  const [activeTab, setActiveTab] = useState<'findings' | 'decisions' | 'conflicts' | 'raw'>('findings')

  const plan       = data.plan ?? []
  const complexity = data.complexity ?? 'medium'
  const escalated  = data.escalated ?? false
  const conflicts  = data.conflicts ?? []
  const findings   = data.findings ?? []
  const decisions  = data.decisions ?? []
  const ticket     = data.escalation_ticket
  const agentsRun  = plan.filter(a => a !== 'EscalationAgent').length + 1

  const cxColor = { low: 'var(--success)', medium: 'var(--warning)', high: 'var(--danger)' }[complexity] ?? 'var(--warning)'
  const cxBg    = { low: 'var(--success-soft)', medium: 'var(--warning-soft)', high: 'var(--danger-soft)' }[complexity] ?? 'var(--warning-soft)'

  const METRICS = [
    { label: 'Duration',   value: `${elapsed}s`,                          Icon: Clock,         color: undefined,          bg: undefined },
    { label: 'Agents',     value: agentsRun,                              Icon: Bot,           color: undefined,          bg: undefined },
    { label: 'Complexity', value: complexity.charAt(0).toUpperCase() + complexity.slice(1), Icon: BarChart2, color: cxColor, bg: cxBg },
    { label: 'Conflicts',  value: conflicts.length,                       Icon: AlertTriangle, color: conflicts.length > 0 ? 'var(--warning)' : undefined, bg: conflicts.length > 0 ? 'var(--warning-soft)' : undefined },
    { label: 'Escalated',  value: escalated ? 'YES' : 'NO',               Icon: escalated ? AlertOctagon : CheckCircle2, color: escalated ? 'var(--danger)' : 'var(--success)', bg: escalated ? 'var(--danger-soft)' : 'var(--success-soft)' },
  ]

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* ── Metrics ──────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 }}>
        {METRICS.map(({ label, value, Icon, color, bg }) => (
          <div key={label} style={{
            borderRadius: 14,
            background: bg ?? 'var(--bg-surface)',
            border: `1px solid ${bg ? 'transparent' : 'var(--border-subtle)'}`,
            padding: '14px 16px',
            display: 'flex', flexDirection: 'column', gap: 8,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Icon size={13} color={color ?? 'var(--text-muted)'} strokeWidth={2} />
              <span style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase' }}>
                {label}
              </span>
            </div>
            <span style={{
              fontSize: 22, fontWeight: 700, lineHeight: 1,
              color: color ?? 'var(--text-primary)',
              fontFamily: 'var(--font-display)',
            }}>
              {value}
            </span>
          </div>
        ))}
      </div>

      {/* ── Investigation Plan ───────────────────────────── */}
      <div style={{
        borderRadius: 16, background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)', padding: '18px 20px',
      }}>
        <SectionLabel Icon={GitFork} text="Investigation Plan" />
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginTop: 12 }}>
          {plan.map((agent, i) => (
            <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {i > 0 && <ChevronRight size={14} color="var(--text-muted)" />}
              <span className="agent-badge">{agent}</span>
            </span>
          ))}
        </div>
        {data.plan_reasoning && (
          <p style={{ marginTop: 10, fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>
            <strong style={{ color: 'var(--text-secondary)' }}>Reasoning:</strong>{' '}{data.plan_reasoning}
          </p>
        )}
      </div>

      {/* ── Support Response ─────────────────────────────── */}
      <div style={{
        borderRadius: 16,
        background: 'rgba(59,130,246,0.05)',
        border: '1px solid rgba(59,130,246,0.18)',
        borderLeft: '4px solid var(--accent)',
        padding: '20px 22px',
      }}>
        <SectionLabel Icon={MessageSquare} text="Support Response" color="rgba(99,179,237,0.85)" />
        <p className="response-text" style={{ marginTop: 12, fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.85 }}>
          {data.response ?? 'No response generated.'}
        </p>
      </div>

      {/* ── Escalation Ticket ────────────────────────────── */}
      {escalated && ticket && (
        <div style={{
          borderRadius: 16, background: 'var(--danger-soft)',
          border: '1px solid rgba(248,113,113,0.25)', padding: '18px 20px',
        }}>
          <SectionLabel Icon={Ticket} text="Escalation Ticket Created" color="var(--danger)" />
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginTop: 10 }}>
            {[
              ['Ticket ID', ticket.ticket_id],
              ['Priority', ticket.priority],
              ['Created', String(ticket.created_at).slice(0, 19)],
            ].map(([k, v]) => (
              <div key={k} style={{ fontSize: 12 }}>
                <span style={{ color: 'var(--text-muted)' }}>{k}: </span>
                <code style={{ color: 'var(--danger)', background: 'rgba(248,113,113,0.1)', padding: '1px 6px', borderRadius: 4 }}>{v}</code>
              </div>
            ))}
          </div>
          <p style={{ marginTop: 10, fontSize: 13, color: 'var(--text-primary)' }}>
            <strong style={{ color: 'var(--text-secondary)' }}>Reason:</strong>{' '}{ticket.reason}
          </p>
        </div>
      )}

      {/* ── Detail Tabs ──────────────────────────────────── */}
      <div style={{
        borderRadius: 16, background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)', overflow: 'hidden',
      }}>
        <div style={{
          display: 'flex', borderBottom: '1px solid var(--border-subtle)',
          background: 'var(--bg-elevated)', overflowX: 'auto',
        }}>
          {([
            ['findings',  Search,      `Findings (${findings.length})`],
            ['decisions', Target,      `Decisions (${decisions.length})`],
            ['conflicts', AlertTriangle, `Conflicts (${conflicts.length})`],
            ['raw',       FileJson,    'Raw JSON'],
          ] as const).map(([key, Icon, label]) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`tab-btn ${activeTab === key ? 'active' : ''}`}
              style={{
                color: activeTab === key ? 'var(--text-primary)' : 'var(--text-muted)',
                display: 'flex', alignItems: 'center', gap: 6,
              }}
            >
              <Icon size={13} strokeWidth={2} />
              {label}
            </button>
          ))}
        </div>

        <div style={{ padding: '20px' }}>
          {activeTab === 'findings'  && <FindingsTab findings={findings} />}
          {activeTab === 'decisions' && <DecisionsTab decisions={decisions} />}
          {activeTab === 'conflicts' && <ConflictsTab conflicts={conflicts} />}
          {activeTab === 'raw' && (
            <pre style={{ fontSize: 11, overflowX: 'auto', maxHeight: 400, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {JSON.stringify(data, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─── Tabs ───────────────────────────────────────────────────────── */

function FindingsTab({ findings }: { findings: Finding[] }) {
  const [expanded, setExpanded] = useState<number | null>(null)
  if (!findings.length) return <Empty text="No agent findings recorded for this session." />

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {findings.map((f, i) => {
        const conf        = f.confidence
        const borderColor = { high: 'var(--success)', medium: 'var(--warning)', low: 'var(--danger)' }[conf] ?? 'var(--success)'
        const bgColor     = { high: 'var(--success-soft)', medium: 'var(--warning-soft)', low: 'var(--danger-soft)' }[conf] ?? 'var(--success-soft)'
        const ConfIcon    = { high: CheckCircle2, medium: AlertTriangle, low: AlertOctagon }[conf] ?? CheckCircle2
        return (
          <div key={i} style={{
            borderRadius: 12, padding: '14px 16px',
            background: bgColor,
            borderLeft: `3px solid ${borderColor}`,
            border: `1px solid ${borderColor}22`,
            borderLeftWidth: 3,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
              <ConfIcon size={14} color={borderColor} strokeWidth={2.5} />
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{f.agent}</span>
              <span style={{
                fontSize: 10, padding: '2px 8px', borderRadius: 99,
                background: 'rgba(255,255,255,0.05)',
                color: 'var(--text-muted)',
                border: '1px solid var(--border-subtle)',
              }}>{conf} confidence</span>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{f.finding}</p>
            {f.data && (
              <div style={{ marginTop: 10 }}>
                <button
                  onClick={() => setExpanded(expanded === i ? null : i)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 4,
                    fontSize: 11, color: 'var(--accent)',
                    background: 'none', border: 'none', cursor: 'pointer', padding: 0,
                  }}
                >
                  {expanded === i ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                  {expanded === i ? 'Hide raw data' : 'Show raw tool data'}
                </button>
                {expanded === i && (
                  <pre style={{
                    marginTop: 8, fontSize: 11, padding: '12px',
                    background: 'var(--bg-base)', borderRadius: 8,
                    color: 'var(--text-muted)', overflowX: 'auto', maxHeight: 200,
                    border: '1px solid var(--border-subtle)',
                  }}>
                    {JSON.stringify(f.data, null, 2)}
                  </pre>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function DecisionsTab({ decisions }: { decisions: Decision[] }) {
  if (!decisions.length) return <Empty text="No decisions recorded for this session." />
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {decisions.map((d, i) => (
        <div key={i} style={{
          borderRadius: 12, padding: '14px 16px',
          background: 'var(--success-soft)',
          borderLeft: '3px solid var(--success)',
          border: '1px solid rgba(52,211,153,0.15)',
          borderLeftWidth: 3,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
            <Target size={14} color="var(--success)" strokeWidth={2} />
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{d.decision_point}</span>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>by {d.made_by}</span>
          </div>
          <p style={{ fontSize: 12, marginBottom: 6 }}>
            <span style={{ color: 'var(--text-muted)' }}>Choice: </span>
            <code style={{ color: 'var(--accent)', background: 'var(--accent-soft)', padding: '1px 6px', borderRadius: 4, fontSize: 11 }}>
              {d.choice}
            </code>
          </p>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{d.reasoning}</p>
        </div>
      ))}
    </div>
  )
}

function ConflictsTab({ conflicts }: { conflicts: Conflict[] }) {
  if (!conflicts.length) return (
    <div style={{
      padding: '16px 20px', borderRadius: 12,
      background: 'var(--success-soft)',
      border: '1px solid rgba(52,211,153,0.2)',
      fontSize: 13, color: 'var(--success)',
      display: 'flex', alignItems: 'center', gap: 10,
    }}>
      <CheckCheck size={16} strokeWidth={2.5} />
      No data conflicts detected in this investigation.
    </div>
  )
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {conflicts.map((c, i) => (
        <div key={i} style={{
          borderRadius: 12, padding: '14px 16px',
          background: 'var(--warning-soft)',
          borderLeft: '3px solid var(--warning)',
          border: '1px solid rgba(251,191,36,0.15)',
          borderLeftWidth: 3,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <AlertTriangle size={14} color="var(--warning)" strokeWidth={2} />
            <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--warning)' }}>Conflict Detected & Resolved</p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 12 }}>
            {[['Source A', c.source_a], ['Source B', c.source_b], ['Issue', c.description], ['Resolution', c.resolution]].map(([k, v]) => (
              <div key={k}>
                <span style={{ color: 'var(--text-muted)' }}>{k}: </span>
                <span style={{ color: k === 'Resolution' ? 'var(--text-primary)' : 'var(--text-secondary)' }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function Empty({ text }: { text: string }) {
  return <p style={{ textAlign: 'center', padding: '24px 0', fontSize: 13, color: 'var(--text-muted)' }}>{text}</p>
}

function SectionLabel({ Icon, text, color }: { Icon: React.ElementType; text: string; color?: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <Icon size={14} color={color ?? 'var(--text-muted)'} strokeWidth={2} />
      <span style={{
        fontSize: 11, fontWeight: 600, letterSpacing: '0.08em',
        textTransform: 'uppercase', color: color ?? 'var(--text-muted)',
      }}>{text}</span>
    </div>
  )
}
