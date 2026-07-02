import { useState } from 'react'
import {
  BookOpen, Search, Copy, Check, Terminal, ExternalLink,
  Shield, Key, HelpCircle, HardDrive, ListCollapse,
} from 'lucide-react'

interface KnowledgeBasePanelProps {
  onAskQuestion: (query: string) => void
}

export default function KnowledgeBasePanel({ onAskQuestion }: KnowledgeBasePanelProps) {
  const [search, setSearch] = useState('')
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const KNOWLEDGE_SECTIONS = [
    {
      id: 'features',
      title: '1. Feature Availability Matrix',
      desc: 'Platform features enabled across Starter, Pro, and Enterprise subscription tiers.',
      content: (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <table style={{
            width: '100%', borderCollapse: 'collapse', fontSize: 12,
            background: 'var(--bg-elevated)', borderRadius: 8, overflow: 'hidden',
          }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--text-primary)' }}>Feature Key</th>
                <th style={{ padding: '10px 12px', textAlign: 'center', color: 'var(--text-primary)' }}>Starter</th>
                <th style={{ padding: '10px 12px', textAlign: 'center', color: 'var(--text-primary)' }}>Pro</th>
                <th style={{ padding: '10px 12px', textAlign: 'center', color: 'var(--text-primary)' }}>Enterprise</th>
              </tr>
            </thead>
            <tbody>
              {[
                { key: 'basic_dashboard', starter: '✓', pro: '✓', ent: '✓' },
                { key: 'dark_mode', starter: '✓', pro: '✓', ent: '✓' },
                { key: 'email_support', starter: '✓', pro: '✓', ent: '✓' },
                { key: 'api_access', starter: '✗', pro: '✓', ent: '✓' },
                { key: 'advanced_analytics', starter: '✗', pro: '✓', ent: '✓' },
                { key: 'webhooks', starter: '✗', pro: '✓', ent: '✓' },
                { key: 'priority_support', starter: '✗', pro: '✓', ent: '✓' },
                { key: 'sso', starter: '✗', starterColor: 'var(--text-muted)', pro: '✗', proColor: 'var(--text-muted)', ent: '✓' },
                { key: 'custom_roles', starter: '✗', pro: '✗', ent: '✓' },
                { key: 'dedicated_support', starter: '✗', pro: '✗', ent: '✓' },
              ].map(row => (
                <tr key={row.key} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '8px 12px', fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{row.key}</td>
                  <td style={{ padding: '8px 12px', textAlign: 'center', color: row.starter === '✓' ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>{row.starter}</td>
                  <td style={{ padding: '8px 12px', textAlign: 'center', color: row.pro === '✓' ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>{row.pro}</td>
                  <td style={{ padding: '8px 12px', textAlign: 'center', color: row.ent === '✓' ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>{row.ent}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 4 }}>
            <AskButton
              text="Ask about feature mismatch"
              query="I have Starter plan. Why is API Access showing active for me?"
              onAsk={onAskQuestion}
            />
            <AskButton
              text="Ask about Pro seats limit"
              query="What is the seat limit on Pro plan?"
              onAsk={onAskQuestion}
            />
          </div>
        </div>
      )
    },
    {
      id: 'apilimit',
      title: '2. API Rate Limit Discrepancy Policy',
      desc: 'Resolving discrepancies between promotional material and database schemas.',
      content: (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{
            padding: '14px', borderRadius: 12, background: 'rgba(251,191,36,0.05)',
            borderLeft: '4px solid var(--warning)', border: '1px solid rgba(251,191,36,0.18)',
            fontSize: 13, lineHeight: 1.6, color: 'var(--text-secondary)',
          }}>
            <p style={{ fontWeight: 600, color: 'var(--warning)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Shield size={14} /> Marketing vs. Database Schema conflict
            </p>
            <ul style={{ paddingLeft: 18, listStyleType: 'disc', display: 'flex', flexDirection: 'column', gap: 6 }}>
              <li><strong>Marketing material</strong> incorrectly claims that the <strong style={{ color: 'var(--text-primary)' }}>Pro plan</strong> includes <em>unlimited</em> API access.</li>
              <li><strong>Database Schema & Contracts</strong> define a hard limit of <strong style={{ color: 'var(--text-primary)' }}>1,000 calls/month</strong> for the Pro plan.</li>
              <li><strong>Enterprise tier</strong> is the only tier with true unlimited API access.</li>
              <li><strong>Resolution Strategy:</strong> Acknowledge the documentation discrepancy, confirm the database limit of 1000, and offer upgrading to Enterprise.</li>
            </ul>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <AskButton
              text="Ask about Pro rate limits"
              query="Documentation says Pro includes unlimited API calls but I get rate limit errors after 1000 calls. Why?"
              onAsk={onAskQuestion}
            />
          </div>
        </div>
      )
    },
    {
      id: 'sla',
      title: '3. Contract SLA & Penalties',
      desc: 'Operational service level agreement rules by customer contract.',
      content: (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <table style={{
            width: '100%', borderCollapse: 'collapse', fontSize: 12,
            background: 'var(--bg-elevated)', borderRadius: 8, overflow: 'hidden',
          }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--text-primary)' }}>Contract ID</th>
                <th style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--text-primary)' }}>Tier</th>
                <th style={{ padding: '10px 12px', textAlign: 'center', color: 'var(--text-primary)' }}>SLA Hours</th>
                <th style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--text-primary)' }}>Special Penalties</th>
              </tr>
            </thead>
            <tbody>
              {[
                { id: 'CONTRACT-001', plan: 'starter', sla: '72 hrs', terms: 'None' },
                { id: 'CONTRACT-002', plan: 'pro', sla: '24 hrs', terms: 'Standard support SLA' },
                { id: 'CONTRACT-003', plan: 'enterprise', sla: '4 hrs', terms: '10% MRR credit penalty per day of breach' },
                { id: 'CONTRACT-004', plan: 'starter', sla: '72 hrs', terms: 'None' },
                { id: 'CONTRACT-005', plan: 'pro', sla: '24 hrs', terms: 'Account suspended (billing failure)' },
              ].map(row => (
                <tr key={row.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '8px 12px', fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{row.id}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>{row.plan.toUpperCase()}</td>
                  <td style={{ padding: '8px 12px', textAlign: 'center', color: 'var(--text-secondary)' }}>{row.sla}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>{row.terms}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ display: 'flex', gap: 8 }}>
            <AskButton
              text="Ask about SLA breach penalty"
              query="I have an enterprise SLA contract with a 4-hour guarantee. We waited 10 days for response. What credits do we get?"
              onAsk={onAskQuestion}
            />
          </div>
        </div>
      )
    },
    {
      id: 'onboarding',
      title: '4. Seat Overages & Licensing',
      desc: 'Database thresholds for licensing seat capacities.',
      content: (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            <p>Each contract sets a strict maximum of user seats allocated. If the seats used exceed the allocated seats, the account is flagged for seat overage:</p>
            <ul style={{ paddingLeft: 18, listStyleType: 'disc', marginTop: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
              <li><strong>Starter Seats limit:</strong> 10 seats</li>
              <li><strong>Pro Seats limit:</strong> 50 seats</li>
              <li><strong>Enterprise Seats limit:</strong> Unlimited</li>
              <li><strong>David Lee (CUST-004)</strong> has 10 seats allocated but 15 used (SaaS seat mismatch conflict).</li>
            </ul>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <AskButton
              text="Ask about seat mismatch"
              query="Our seat capacity shows 10 but we have 15 users. How can we fix this seat migration mismatch?"
              onAsk={onAskQuestion}
            />
          </div>
        </div>
      )
    }
  ]

  const filteredSections = KNOWLEDGE_SECTIONS.filter(s =>
    s.title.toLowerCase().includes(search.toLowerCase()) ||
    s.desc.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div style={{ display: 'flex', gap: 24, height: '100%', overflow: 'hidden' }} className="animate-fade-in">
      {/* ── Left Navigation Links ───────────────────────── */}
      <div style={{
        width: 200, flexShrink: 0, display: 'flex', flexDirection: 'column',
        gap: 12, borderRight: '1px solid var(--border-subtle)', paddingRight: 20,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
          <ListCollapse size={14} color="var(--text-muted)" />
          <span style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            Sections
          </span>
        </div>
        {KNOWLEDGE_SECTIONS.map(s => (
          <a
            key={s.id}
            href={`#kb-${s.id}`}
            style={{
              fontSize: 12, color: 'var(--text-secondary)', textDecoration: 'none',
              padding: '6px 10px', borderRadius: 6, transition: 'all 0.15s',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background = 'var(--bg-surface)'
              e.currentTarget.style.color = 'var(--text-primary)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.color = 'var(--text-secondary)'
            }}
          >
            {s.title.split('.')[1].trim()}
          </a>
        ))}
      </div>

      {/* ── Right Content Area ──────────────────────────── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 20, overflow: 'hidden' }}>
        
        {/* Search */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          background: 'var(--bg-surface)', padding: '10px 14px',
          borderRadius: 12, border: '1px solid var(--border-subtle)',
          flexShrink: 0,
        }}>
          <Search size={15} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search the knowledge base documentation…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              background: 'transparent', border: 'none', color: 'var(--text-primary)',
              fontSize: 13, width: '100%', outline: 'none', fontFamily: 'var(--font-body)',
            }}
          />
        </div>

        {/* Scrollable text container */}
        <div style={{
          flex: 1, overflowY: 'auto', paddingRight: 10,
          display: 'flex', flexDirection: 'column', gap: 32,
        }}>
          {filteredSections.length > 0 ? (
            filteredSections.map(s => (
              <section
                key={s.id}
                id={`kb-${s.id}`}
                style={{
                  scrollMarginTop: 20,
                  display: 'flex', flexDirection: 'column', gap: 10,
                  borderBottom: '1px solid var(--border-subtle)',
                  paddingBottom: 24,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
                  <div>
                    <h3 style={{
                      fontFamily: 'var(--font-display)', fontSize: 18,
                      color: 'var(--text-primary)', fontWeight: 400,
                    }}>{s.title}</h3>
                    <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{s.desc}</p>
                  </div>
                  <button
                    onClick={() => handleCopy(s.id, s.title)}
                    style={{
                      background: 'none', border: 'none', color: 'var(--text-muted)',
                      cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4,
                      fontSize: 11, padding: 4,
                    }}
                    title="Copy section name"
                  >
                    {copiedId === s.id ? <Check size={12} color="var(--success)" /> : <Copy size={12} />}
                    {copiedId === s.id ? 'Copied' : 'Copy'}
                  </button>
                </div>
                <div style={{ marginTop: 6 }}>
                  {s.content}
                </div>
              </section>
            ))
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 40, paddingBottom: 40, color: 'var(--text-muted)', gap: 12 }}>
              <HelpCircle size={32} />
              <p style={{ fontSize: 13 }}>No matching documentation found.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─── Sub-component Ask Button ──────────────────────────────────── */

interface AskButtonProps {
  text: string
  query: string
  onAsk: (q: string) => void
}

function AskButton({ text, query, onAsk }: AskButtonProps) {
  return (
    <button
      onClick={() => onAsk(query)}
      style={{
        display: 'flex', alignItems: 'center', gap: 6,
        padding: '6px 12px', borderRadius: 8, fontSize: 11,
        background: 'rgba(59,130,246,0.08)',
        border: '1px solid rgba(59,130,246,0.18)',
        color: 'var(--accent)', cursor: 'pointer',
        transition: 'all 0.15s',
        fontFamily: 'var(--font-body)',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.background = 'rgba(59,130,246,0.15)'
        e.currentTarget.style.color = '#fff'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background = 'rgba(59,130,246,0.08)'
        e.currentTarget.style.color = 'var(--accent)'
      }}
    >
      <Terminal size={11} strokeWidth={2} />
      {text}
    </button>
  )
}
