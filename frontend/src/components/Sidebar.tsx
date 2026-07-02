import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Zap, Wifi, WifiOff, Loader, User, FlaskConical, Layers,
  CircleCheck, CircleX, ChevronDown, Terminal, BookOpen,
} from 'lucide-react'
import { Customer, getCustomers, getHealth } from '../lib/api'
import { SCENARIOS, SCENARIO_KEYS } from '../lib/scenarios'

interface SidebarProps {
  selectedCustomer: Customer | null
  onSelectCustomer: (c: Customer | null) => void
  selectedScenario: string | null
  onSelectScenario: (key: string | null, query: string) => void
  activeView: 'console' | 'knowledge'
  onSelectView: (view: 'console' | 'knowledge') => void
}

export default function Sidebar({
  selectedCustomer, onSelectCustomer, selectedScenario, onSelectScenario,
  activeView, onSelectView
}: SidebarProps) {
  const navigate = useNavigate()
  const [customers, setCustomers] = useState<Customer[]>([])
  const [health, setHealth] = useState<'online' | 'offline' | 'checking'>('checking')

  useEffect(() => {
    getHealth().then(() => setHealth('online')).catch(() => setHealth('offline'))
  }, [])

  useEffect(() => {
    getCustomers().then(setCustomers).catch(() => setCustomers([]))
  }, [])

  const isActive = selectedCustomer?.status === 'active'

  return (
    <aside style={{
      width: 264, minWidth: 264, height: '100vh',
      background: 'var(--bg-surface)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex', flexDirection: 'column', overflow: 'hidden',
    }}>

      {/* ── Logo ─────────────────────────────────────────── */}
      <div style={{ padding: '24px 20px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
        {/* Logo row — click → landing page */}
        <div
          onClick={() => navigate('/')}
          style={{
            display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6,
            cursor: 'pointer',
            transition: 'opacity 0.15s',
          }}
          onMouseEnter={e => (e.currentTarget.style.opacity = '0.75')}
          onMouseLeave={e => (e.currentTarget.style.opacity = '1')}
          title="Go to home"
        >
          <div style={{
            width: 32, height: 32,
            background: 'linear-gradient(135deg, #a855f7, #3b82f6)',
            borderRadius: 8,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <Zap size={17} color="#fff" fill="#fff" strokeWidth={2} />
          </div>
          <span style={{
            fontFamily: 'var(--font-display)', fontSize: 18,
            color: 'var(--text-primary)', letterSpacing: '-0.3px',
          }}>
            AgentDesk<sup style={{ fontSize: 9, verticalAlign: 'super' }}>®</sup>
          </span>
        </div>

        {/* Subtitle — click → /app */}
        <p
          onClick={() => navigate('/app')}
          style={{
            fontSize: 11, color: 'var(--text-muted)', marginLeft: 42,
            letterSpacing: '0.02em', cursor: 'pointer',
            transition: 'color 0.15s',
            display: 'flex', alignItems: 'center', gap: 4,
          }}
          onMouseEnter={e => (e.currentTarget.style.color = 'var(--text-secondary)')}
          onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
          title="Go to Investigation Console"
        >
          Investigation Console ↗
        </p>
      </div>

      {/* ── Scrollable body ──────────────────────────────── */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 16px' }}>

        {/* Console Mode */}
        <SideSection label="Console Mode" icon={<Layers size={11} />}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <button
              onClick={() => onSelectView('console')}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '9px 12px', borderRadius: 8, fontSize: 12,
                fontWeight: activeView === 'console' ? 600 : 400,
                background: activeView === 'console' ? 'var(--bg-elevated)' : 'transparent',
                color: activeView === 'console' ? 'var(--text-primary)' : 'var(--text-secondary)',
                border: activeView === 'console' ? '1px solid var(--border-default)' : '1px solid transparent',
                cursor: 'pointer', textAlign: 'left',
                width: '100%', transition: 'all 0.15s',
                fontFamily: 'var(--font-body)',
              }}
            >
              <Terminal size={14} color={activeView === 'console' ? 'var(--accent)' : 'currentColor'} />
              Investigation Console
            </button>

            <button
              onClick={() => onSelectView('knowledge')}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '9px 12px', borderRadius: 8, fontSize: 12,
                fontWeight: activeView === 'knowledge' ? 600 : 400,
                background: activeView === 'knowledge' ? 'var(--bg-elevated)' : 'transparent',
                color: activeView === 'knowledge' ? 'var(--text-primary)' : 'var(--text-secondary)',
                border: activeView === 'knowledge' ? '1px solid var(--border-default)' : '1px solid transparent',
                cursor: 'pointer', textAlign: 'left',
                width: '100%', transition: 'all 0.15s',
                fontFamily: 'var(--font-body)',
              }}
            >
              <BookOpen size={14} color={activeView === 'knowledge' ? 'var(--accent)' : 'currentColor'} />
              Knowledge Base
            </button>
          </div>
        </SideSection>

        <div style={{ margin: '15px 0', borderTop: '1px solid var(--border-subtle)' }} />


        {/* Backend */}
        <SideSection label="Backend" icon={<Wifi size={11} />}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '8px 12px', borderRadius: 10,
            background: health === 'online' ? 'var(--success-soft)' : health === 'offline' ? 'var(--danger-soft)' : 'rgba(255,255,255,0.03)',
            border: `1px solid ${health === 'online' ? 'rgba(52,211,153,0.2)' : health === 'offline' ? 'rgba(248,113,113,0.2)' : 'var(--border-subtle)'}`,
          }}>
            {health === 'checking' && <Loader size={13} color="var(--text-muted)" style={{ animation: 'spin 1s linear infinite' }} />}
            {health === 'online'   && <CircleCheck size={14} color="var(--success)" strokeWidth={2.5} />}
            {health === 'offline'  && <CircleX     size={14} color="var(--danger)"  strokeWidth={2.5} />}
            {health === 'online'   && <Wifi   size={13} color="var(--success)" />}
            {health === 'offline'  && <WifiOff size={13} color="var(--danger)"  />}
            <span style={{
              fontSize: 12, fontWeight: 500,
              color: health === 'online' ? 'var(--success)' : health === 'offline' ? 'var(--danger)' : 'var(--text-secondary)',
            }}>
              {health === 'online' ? 'Backend online' : health === 'offline' ? 'Backend offline' : 'Connecting…'}
            </span>
          </div>
          {health === 'offline' && (
            <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8, lineHeight: 1.5 }}>
              Run: <code style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)', padding: '1px 6px', borderRadius: 4, fontSize: 11 }}>python app.py</code>
            </p>
          )}
        </SideSection>

        {/* Customer */}
        <SideSection label="Customer" icon={<User size={11} />}>
          <StyledSelect
            value={selectedCustomer?.id ?? ''}
            onChange={val => onSelectCustomer(customers.find(c => c.id === val) ?? null)}
            options={[
              { value: '', label: '— Anonymous —' },
              ...customers.map(c => ({
                value: c.id,
                label: `${c.status === 'active' ? '●' : '○'} ${c.name} · ${c.plan.toUpperCase()}`,
              })),
            ]}
          />
          {selectedCustomer && (
            <div style={{
              marginTop: 10, padding: '10px 12px', borderRadius: 10,
              background: isActive ? 'rgba(52,211,153,0.06)' : 'rgba(248,113,113,0.06)',
              border: `1px solid ${isActive ? 'rgba(52,211,153,0.18)' : 'rgba(248,113,113,0.18)'}`,
            }}>
              {[
                ['ID', selectedCustomer.id],
                ['Company', selectedCustomer.company],
                ['Plan', selectedCustomer.plan.toUpperCase()],
                ['Status', selectedCustomer.status.toUpperCase()],
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: 11 }}>
                  <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                  <span style={{
                    color: k === 'Status' ? (isActive ? 'var(--success)' : 'var(--danger)') : 'var(--text-secondary)',
                    fontWeight: k === 'Status' ? 600 : 400,
                  }}>{v}</span>
                </div>
              ))}
            </div>
          )}
        </SideSection>

        {/* Scenarios */}
        <SideSection label="Test Scenarios" icon={<FlaskConical size={11} />}>
          <StyledSelect
            value={selectedScenario ?? ''}
            onChange={val => {
              if (val && SCENARIOS[val]) onSelectScenario(val, SCENARIOS[val].query)
              else onSelectScenario(null, '')
            }}
            options={[
              { value: '', label: '— Custom query —' },
              ...SCENARIO_KEYS.map(k => ({ value: k, label: k })),
            ]}
          />
          {selectedScenario && SCENARIOS[selectedScenario] && (
            <div style={{
              marginTop: 8, padding: '8px 10px',
              background: 'rgba(59,130,246,0.06)',
              border: '1px solid rgba(59,130,246,0.14)',
              borderRadius: 8,
              fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5,
              display: 'flex', gap: 6, alignItems: 'flex-start',
            }}>
              <span style={{ color: 'var(--accent)', marginTop: 1, flexShrink: 0 }}>ℹ</span>
              {SCENARIOS[selectedScenario].hint}
            </div>
          )}
        </SideSection>

        {/* Tech Stack */}
        <SideSection label="Stack" icon={<Layers size={11} />}>
          <div style={{
            borderRadius: 10, background: 'var(--bg-elevated)',
            border: '1px solid var(--border-subtle)', overflow: 'hidden',
          }}>
            {[
              ['Orchestration', 'LangGraph'],
              ['LLM', 'LLaMA-3.3-70B'],
              ['Provider', 'Groq'],
              ['Observability', 'Langfuse'],
              ['Backend', 'Flask'],
            ].map(([k, v], i, arr) => (
              <div key={k} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '8px 12px', fontSize: 11,
                borderBottom: i < arr.length - 1 ? '1px solid var(--border-subtle)' : 'none',
              }}>
                <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                <span style={{
                  color: 'var(--text-secondary)', fontWeight: 500,
                  background: 'var(--bg-surface)', padding: '2px 8px',
                  borderRadius: 4, fontSize: 10, letterSpacing: '0.02em',
                }}>{v}</span>
              </div>
            ))}
          </div>
        </SideSection>
      </div>
    </aside>
  )
}

/* ─── Sub-components ─────────────────────────────────────────────── */

function SideSection({ label, icon, children }: { label: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 8 }}>
        <span style={{ color: 'var(--text-muted)', display: 'flex' }}>{icon}</span>
        <p style={{
          fontSize: 10, fontWeight: 600, letterSpacing: '0.12em',
          textTransform: 'uppercase', color: 'var(--text-muted)',
        }}>{label}</p>
      </div>
      {children}
    </div>
  )
}

function StyledSelect({ value, onChange, options }: {
  value: string
  onChange: (v: string) => void
  options: { value: string; label: string }[]
}) {
  return (
    <div style={{ position: 'relative' }}>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          width: '100%', padding: '9px 36px 9px 12px',
          borderRadius: 10, fontSize: 12,
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-subtle)',
          color: value ? 'var(--text-primary)' : 'var(--text-muted)',
          cursor: 'pointer', appearance: 'none',
          outline: 'none', transition: 'border-color 0.2s',
          fontFamily: 'var(--font-body)',
        }}
        onFocus={e => (e.currentTarget.style.borderColor = 'rgba(59,130,246,0.5)')}
        onBlur={e => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}
      >
        {options.map(o => (
          <option key={o.value} value={o.value} style={{ background: '#0a1f35', color: '#f0f4ff' }}>
            {o.label}
          </option>
        ))}
      </select>
      <div style={{
        position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)',
        pointerEvents: 'none', color: 'var(--text-muted)', display: 'flex',
      }}>
        <ChevronDown size={14} />
      </div>
    </div>
  )
}
