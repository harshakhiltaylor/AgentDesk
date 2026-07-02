import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft, MessageSquare, Send, Loader2, Bot,
  Info, AlertCircle, Zap, Tag, X,
} from 'lucide-react'
import Sidebar from '../components/Sidebar'
import InvestigationProgress from '../components/InvestigationProgress'
import ResultsPanel from '../components/ResultsPanel'
import KnowledgeBasePanel from '../components/KnowledgeBasePanel'
import { Customer, InvestigationResult, postQuery } from '../lib/api'

export default function DashboardPage() {
  const navigate = useNavigate()

  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [activeView, setActiveView] = useState<'console' | 'knowledge'>('console')
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [result, setResult] = useState<InvestigationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [charCount, setCharCount] = useState(0)

  const stepTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const startTimeRef = useRef<number>(0)

  const handleSelectScenario = (key: string | null, q: string) => {
    setSelectedScenario(key)
    setQuery(q)
    setCharCount(q.length)
    setResult(null)
    setError(null)
  }

  const handleInvestigate = async () => {
    if (!query.trim() || isLoading) return
    setIsLoading(true)
    setStep(0)
    setResult(null)
    setError(null)
    startTimeRef.current = Date.now()
    stepTimerRef.current = setInterval(() => setStep(s => s + 1), 1900)

    try {
      const res = await postQuery(query, selectedCustomer?.id ?? null)
      setResult(res)
      if (!res.success) setError(res.error ?? 'Investigation failed')
      setElapsed(Math.round((Date.now() - startTimeRef.current) / 100) / 10)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Connection error — is the Flask backend running?')
    } finally {
      if (stepTimerRef.current) clearInterval(stepTimerRef.current)
      setIsLoading(false)
    }
  }

  useEffect(() => () => { if (stepTimerRef.current) clearInterval(stepTimerRef.current) }, [])

  const canInvestigate = !isLoading && query.trim().length > 0
  const canClear = !isLoading && (query.trim().length > 0 || !!result || !!error)

  const handleClear = () => {
    setQuery('')
    setCharCount(0)
    setResult(null)
    setError(null)
    setSelectedScenario(null)
    setStep(0)
  }

  const handleAskQuestion = (q: string) => {
    setQuery(q)
    setCharCount(q.length)
    setResult(null)
    setError(null)
    setSelectedScenario(null)
    setActiveView('console')
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg-base)' }}>
      <Sidebar
        selectedCustomer={selectedCustomer}
        onSelectCustomer={setSelectedCustomer}
        selectedScenario={selectedScenario}
        onSelectScenario={handleSelectScenario}
        activeView={activeView}
        onSelectView={setActiveView}
      />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

        {/* ── Top bar ─────────────────────────────────────── */}
        <header style={{
          height: 60, display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', padding: '0 32px',
          borderBottom: '1px solid var(--border-subtle)',
          background: 'var(--bg-surface)', flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <h1
              onClick={() => navigate('/app')}
              style={{
                fontFamily: 'var(--font-display)', fontSize: 20,
                fontWeight: 400, color: 'var(--text-primary)', letterSpacing: '-0.3px',
                cursor: 'pointer', transition: 'opacity 0.15s',
              }}
              onMouseEnter={e => (e.currentTarget.style.opacity = '0.75')}
              onMouseLeave={e => (e.currentTarget.style.opacity = '1')}
              title="Investigation Console"
            >
              Investigation Console
            </h1>
            <div style={{ width: 1, height: 18, background: 'var(--border-subtle)' }} />
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              LangGraph · Groq LLaMA-3.3-70B · Langfuse
            </span>
          </div>

          <button
            onClick={() => navigate('/')}
            style={{
              display: 'flex', alignItems: 'center', gap: 7,
              padding: '7px 16px', borderRadius: 8, fontSize: 12,
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-muted)', cursor: 'pointer',
              transition: 'all 0.2s', fontFamily: 'var(--font-body)',
            }}
            onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-primary)'; e.currentTarget.style.borderColor = 'var(--border-default)' }}
            onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.borderColor = 'var(--border-subtle)' }}
          >
            <ArrowLeft size={13} strokeWidth={2} />
            Home
          </button>
        </header>

        {/* ── Scrollable content ───────────────────────────── */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '28px 32px', display: 'flex', flexDirection: 'column', gap: 20 }}>

          {activeView === 'knowledge' ? (
            <KnowledgeBasePanel onAskQuestion={handleAskQuestion} />
          ) : (
            <>
              {/* ── Query Panel ─────────────────────────────────── */}
              <div style={{
                borderRadius: 20, background: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)', padding: '24px 24px 20px',
              }}>
                {/* Label row */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <MessageSquare size={14} color="var(--text-secondary)" strokeWidth={2} />
                    <span style={{
                      fontSize: 11, fontWeight: 600, letterSpacing: '0.1em',
                      textTransform: 'uppercase', color: 'var(--text-secondary)',
                    }}>Customer Query</span>
                  </div>
                  {selectedCustomer && (
                    <div style={{
                      display: 'flex', alignItems: 'center', gap: 6,
                      padding: '4px 10px', borderRadius: 999,
                      background: selectedCustomer.status === 'active' ? 'var(--success-soft)' : 'var(--danger-soft)',
                      border: `1px solid ${selectedCustomer.status === 'active' ? 'rgba(52,211,153,0.2)' : 'rgba(248,113,113,0.2)'}`,
                      fontSize: 11, color: selectedCustomer.status === 'active' ? 'var(--success)' : 'var(--danger)',
                    }}>
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor' }} />
                      {selectedCustomer.name} · {selectedCustomer.plan.toUpperCase()}
                    </div>
                  )}
                </div>

                {/* Textarea */}
                <div style={{ position: 'relative' }}>
                  <textarea
                    value={query}
                    onChange={e => { setQuery(e.target.value); setCharCount(e.target.value.length) }}
                    onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && canInvestigate) handleInvestigate() }}
                    placeholder="Type a support query here, or pick a preset scenario from the sidebar…"
                    style={{
                      width: '100%', height: 120, resize: 'none',
                      borderRadius: 12, padding: '14px 16px',
                      background: 'var(--bg-elevated)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-primary)',
                      fontSize: 14, lineHeight: 1.65,
                      fontFamily: 'var(--font-body)',
                      outline: 'none', transition: 'border-color 0.2s, box-shadow 0.2s',
                    }}
                    onFocus={e => {
                      e.currentTarget.style.borderColor = 'rgba(59,130,246,0.45)'
                      e.currentTarget.style.boxShadow = '0 0 0 3px rgba(59,130,246,0.08)'
                    }}
                    onBlur={e => {
                      e.currentTarget.style.borderColor = 'var(--border-subtle)'
                      e.currentTarget.style.boxShadow = 'none'
                    }}
                  />
                  {charCount > 0 && (
                    <span style={{
                      position: 'absolute', bottom: 10, right: 14,
                      fontSize: 10, color: 'var(--text-muted)',
                    }}>{charCount}</span>
                  )}
                </div>

                {/* Action row */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>

                    {/* Clear button — leftmost */}
                    {canClear && (
                      <button
                        onClick={handleClear}
                        style={{
                          display: 'flex', alignItems: 'center', gap: 7,
                          padding: '10px 18px', borderRadius: 10, fontSize: 13, fontWeight: 500,
                          background: 'var(--bg-elevated)',
                          color: 'var(--text-secondary)',
                          border: '1px solid var(--border-subtle)',
                          cursor: 'pointer', transition: 'all 0.2s',
                          fontFamily: 'var(--font-body)',
                        }}
                        onMouseEnter={e => {
                          e.currentTarget.style.borderColor = 'var(--border-default)'
                          e.currentTarget.style.color = 'var(--text-primary)'
                        }}
                        onMouseLeave={e => {
                          e.currentTarget.style.borderColor = 'var(--border-subtle)'
                          e.currentTarget.style.color = 'var(--text-secondary)'
                        }}
                        title="Clear query and results"
                      >
                        Clear
                      </button>
                    )}
                    <button
                      onClick={handleInvestigate}
                      disabled={!canInvestigate}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 8,
                        padding: '10px 22px', borderRadius: 10, fontSize: 13, fontWeight: 600,
                        background: canInvestigate ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)' : 'var(--bg-elevated)',
                        color: canInvestigate ? '#fff' : 'var(--text-muted)',
                        border: 'none',
                        cursor: canInvestigate ? 'pointer' : 'not-allowed',
                        transition: 'all 0.2s',
                        boxShadow: canInvestigate ? '0 4px 16px rgba(59,130,246,0.35)' : 'none',
                        fontFamily: 'var(--font-body)',
                      }}
                      onMouseEnter={e => canInvestigate && (e.currentTarget.style.transform = 'translateY(-1px)')}
                      onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}
                    >
                      {isLoading
                        ? <><Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> Investigating…</>
                        : <><Send size={14} strokeWidth={2} /> Investigate</>
                      }
                    </button>
                    {canInvestigate && !isLoading && (
                      <span style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Zap size={10} /> ⌘↵ to run
                      </span>
                    )}
                  </div>

                  {!selectedCustomer && (
                    <div
                      className="with-tooltip"
                      style={{
                        display: 'flex', alignItems: 'center', gap: 6,
                        padding: '6px 10px', borderRadius: 8,
                        background: 'rgba(251,191,36,0.06)',
                        border: '1px solid rgba(251,191,36,0.18)',
                        fontSize: 11, color: 'var(--warning)', cursor: 'default',
                      }}
                    >
                      <Info size={12} strokeWidth={2} />
                      No customer
                      <span className="tooltip-text">
                        Select a customer in the sidebar for full account, billing & contract investigation
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* ── Progress ─────────────────────────────────────── */}
              <InvestigationProgress isLoading={isLoading} step={step} />

              {/* ── Error ───────────────────────────────────────── */}
              {error && !isLoading && (
                <div style={{
                  borderRadius: 16, padding: '18px 20px',
                  background: 'var(--danger-soft)',
                  border: '1px solid rgba(248,113,113,0.2)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <AlertCircle size={15} color="var(--danger)" strokeWidth={2} />
                    <p style={{ fontWeight: 600, color: 'var(--danger)', fontSize: 14 }}>Error</p>
                  </div>
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{error}</p>
                  <p style={{ marginTop: 8, fontSize: 12, color: 'var(--text-muted)' }}>
                    Make sure the Flask backend is running:{' '}
                    <code style={{ background: 'var(--bg-elevated)', padding: '1px 6px', borderRadius: 4 }}>python app.py</code>
                  </p>
                </div>
              )}

              {/* ── Results ─────────────────────────────────────── */}
              {result && result.success && !isLoading && (
                <ResultsPanel data={result} elapsed={elapsed} />
              )}

              {/* ── Empty state ─────────────────────────────────── */}
              {!result && !isLoading && !error && (
                <div style={{
                  flex: 1, display: 'flex', flexDirection: 'column',
                  alignItems: 'center', justifyContent: 'center',
                  minHeight: 320, textAlign: 'center', gap: 16,
                }}>
                  <div style={{
                    width: 72, height: 72, borderRadius: 20,
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Zap size={34} color="var(--accent)" fill="var(--accent-soft)" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p style={{ fontFamily: 'var(--font-display)', fontSize: 22, color: 'var(--text-primary)', marginBottom: 8 }}>
                      Ready to investigate
                    </p>
                    <p style={{ fontSize: 14, color: 'var(--text-muted)', maxWidth: 380, lineHeight: 1.65 }}>
                      Select a scenario from the sidebar or type a custom query above, then click Investigate.
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: 8, marginTop: 4, flexWrap: 'wrap', justifyContent: 'center' }}>
                    {['Account disputes', 'SLA violations', 'API conflicts', 'Seat overages'].map(tag => (
                      <span key={tag} className="agent-badge" style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11 }}>
                        <Tag size={10} strokeWidth={2} />
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          <div style={{ height: 20 }} />
        </div>

        {/* ── Footer ──────────────────────────────────────── */}
        <footer style={{
          height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center',
          borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-surface)', flexShrink: 0,
        }}>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
            AgentDesk &nbsp;·&nbsp; LangGraph + Groq (LLaMA-3.3-70B) + Langfuse + Flask
          </p>
        </footer>
      </div>
    </div>
  )
}
