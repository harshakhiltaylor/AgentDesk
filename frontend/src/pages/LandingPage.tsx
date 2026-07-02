import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Brain, Zap, SearchCode, BarChart3, ArrowUpRight,
  User, Database, GitFork, Cpu, AlertTriangle,
  Mail, CheckCircle2, ChevronRight,
} from 'lucide-react'

const VIDEO_URL =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260314_131748_f2ca2a28-fed7-44c8-b9a9-bd9acdd5ec31.mp4'

export default function LandingPage() {
  const navigate = useNavigate()

  // Contact Form State
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleScroll = (id: string) => {
    const el = document.getElementById(id)
    if (el) {
      el.scrollMarginTop = 80 // offset for navbar
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (name && email && message) {
      setSubmitted(true)
      setName('')
      setEmail('')
      setMessage('')
      setTimeout(() => setSubmitted(false), 5000)
    }
  }

  return (
    <div style={{
      position: 'relative',
      minHeight: '100vh',
      background: '#071828',
    }}>

      {/* ── Background Video (Fixed Position for parallax) ── */}
      <video
        autoPlay loop muted playsInline
        style={{
          position: 'fixed', inset: 0,
          width: '100%', height: '100%',
          objectFit: 'cover', zIndex: 0,
        }}
      >
        <source src={VIDEO_URL} type="video/mp4" />
      </video>

      {/* ── Gradient scrim for text legibility ─────────── */}
      <div style={{
        position: 'fixed', inset: 0, zIndex: 1,
        background: 'linear-gradient(to bottom, rgba(5,8,16,0.5) 0%, rgba(5,8,16,0.3) 50%, rgba(5,8,16,0.85) 100%)',
        pointerEvents: 'none',
      }} />

      {/* ── All content ─────────────────────────────────── */}
      <div style={{ position: 'relative', zIndex: 10, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>

        {/* ── Fixed/Floating Nav ───────────────────────── */}
        <nav style={{
          position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
          padding: '16px 48px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: '#071828',
          borderBottom: '1px solid var(--border-subtle)',
        }}>
          {/* Logo — click → scroll to top */}
          <span
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 26, color: '#f0f4ff',
              letterSpacing: '-0.5px', fontWeight: 400,
              cursor: 'pointer', transition: 'opacity 0.15s',
            }}
            onMouseEnter={e => (e.currentTarget.style.opacity = '0.75')}
            onMouseLeave={e => (e.currentTarget.style.opacity = '1')}
            title="AgentDesk Home"
          >
            AgentDesk<sup style={{ fontSize: 11, verticalAlign: 'super', marginLeft: 1 }}>®</sup>
          </span>

          {/* Links */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 36 }}>
            {[
              { name: 'Home', id: 'home' },
              { name: 'About', id: 'about' },
              { name: 'Architecture', id: 'architecture' },
              { name: 'Research', id: 'research' },
              { name: 'Reach Us', id: 'reach-us' }
            ].map(({ name, id }) => (
              <span key={name} style={{
                fontSize: 14, cursor: 'pointer',
                color: 'rgba(240,244,255,0.6)',
                transition: 'color 0.2s',
                fontWeight: 500,
              }}
                onClick={() => handleScroll(id)}
                onMouseEnter={e => (e.currentTarget.style.color = '#f0f4ff')}
                onMouseLeave={e => (e.currentTarget.style.color = 'rgba(240,244,255,0.6)')}
              >{name}</span>
            ))}
          </div>

          {/* CTA */}
          <button
            onClick={() => navigate('/app')}
            className="liquid-glass"
            style={{
              padding: '10px 24px', borderRadius: 999,
              fontSize: 13, color: '#f0f4ff', cursor: 'pointer',
              transition: 'transform 0.2s, opacity 0.2s',
              fontFamily: 'var(--font-body)',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.04)'; e.currentTarget.style.opacity = '0.9' }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.opacity = '1' }}
          >
            Launch App <ArrowUpRight size={13} style={{ display: 'inline', verticalAlign: 'middle' }} />
          </button>
        </nav>

        {/* ── Home (Hero) Section ────────────────────────── */}
        <section id="home" style={{
          minHeight: '100vh',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          textAlign: 'center',
          padding: '150px 48px 60px',
          gap: 0,
        }}>
          {/* Eyebrow */}
          <p
            className="animate-fade-rise"
            style={{
              fontSize: 11, letterSpacing: '0.2em', textTransform: 'uppercase',
              color: 'rgba(240,244,255,0.45)', marginBottom: 32,
            }}
          >
            LangGraph &nbsp;·&nbsp; LLaMA-3 &nbsp;·&nbsp; Langfuse
          </p>

          {/* H1 */}
          <h1
            className="animate-fade-rise"
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(2.6rem, 6.5vw, 5.5rem)',
              lineHeight: 1.02,
              letterSpacing: '-0.04em',
              fontWeight: 400,
              color: '#f0f4ff',
              maxWidth: 900,
              width: '100%',
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
            }}
          >
            Where{' '}
            <em className="not-italic" style={{ color: 'rgba(240,244,255,0.42)' }}>agents resolve</em>{' '}
            what{' '}
            <em className="not-italic" style={{ color: 'rgba(240,244,255,0.42)' }}>humans can't.</em>
          </h1>

          {/* Subtext */}
          <p
            className="animate-fade-rise-delay"
            style={{
              maxWidth: 520,
              marginTop: 28,
              fontSize: 16,
              lineHeight: 1.75,
              color: 'rgba(240,244,255,0.55)',
            }}
          >
            A production-grade multi-agent intelligence system. The Orchestrator thinks.
            Specialists investigate. Conflicts get resolved. You get answers.
          </p>

          {/* CTA */}
          <button
            onClick={() => navigate('/app')}
            className="liquid-glass animate-fade-rise-delay-2"
            style={{
              marginTop: 44,
              padding: '16px 52px',
              borderRadius: 999,
              fontSize: 15, color: '#f0f4ff',
              cursor: 'pointer',
              fontFamily: 'var(--font-body)',
              transition: 'transform 0.25s, box-shadow 0.25s',
              letterSpacing: '0.01em',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.04)'; e.currentTarget.style.boxShadow = '0 0 40px rgba(59,130,246,0.25)' }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = '' }}
          >
            Begin Investigation
          </button>

          {/* Feature Strip */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: 16,
            maxWidth: 1100,
            width: '100%',
            marginTop: 80,
          }}>
            {FEATURES.map((f, i) => (
              <div
                key={f.title}
                className="liquid-glass"
                style={{ borderRadius: 20, padding: '22px 20px', textAlign: 'left' }}
              >
                <div style={{
                  width: 38, height: 38, borderRadius: 10, marginBottom: 14,
                  background: 'rgba(59,130,246,0.12)',
                  border: '1px solid rgba(59,130,246,0.2)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <f.Icon size={18} color="rgba(147,197,253,0.85)" strokeWidth={1.8} />
                </div>
                <h3 style={{ fontSize: 14, fontWeight: 600, color: '#f0f4ff', marginBottom: 8, lineHeight: 1.3 }}>
                  {f.title}
                </h3>
                <p style={{ fontSize: 12, lineHeight: 1.65, color: 'rgba(240,244,255,0.45)' }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* ── About Section ──────────────────────────────── */}
        <section id="about" style={{
          padding: '120px 48px 100px',
          maxWidth: 1100,
          margin: '0 auto',
          width: '100%',
        }}>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(2rem, 4vw, 3.5rem)',
            color: '#f0f4ff',
            marginBottom: 40,
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: 16,
          }}>
            About AgentDesk
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: 48, alignItems: 'start' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24, fontSize: 15, color: 'rgba(240,244,255,0.7)', lineHeight: 1.85 }}>
              <p>
                <strong>AgentDesk</strong> is a next-generation multi-agent support intelligence system designed for production-level customer success operations. It replaces manual ticket categorization and data cross-referencing with autonomous, LLM-driven specialist agents.
              </p>
              <p>
                By simulating a live enterprise support environment, the system reviews customer history, checks enabled features, checks database entries, and calculates SLAs autonomously, verifying that what is promised in the contract matches live production configurations.
              </p>

              <div style={{
                borderRadius: 16, padding: '20px 24px',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border-subtle)',
                marginTop: 12,
              }}>
                <h4 style={{ color: '#f0f4ff', fontSize: 14, fontWeight: 600, marginBottom: 8 }}>Project Mission</h4>
                <p style={{ fontSize: 13, color: 'rgba(240,244,255,0.55)' }}>
                  To prove that orchestrating specialist AI agents can solve complex, contradictory, and logic-intensive operations that single prompt scripts fail to address, reducing support escalations by validating real-time database state anomalies automatically.
                </p>
              </div>
            </div>

            {/* Author Profile Card */}
            <div className="liquid-glass" style={{ borderRadius: 24, padding: '32px 28px', border: '1px solid var(--border-default)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
                <div style={{
                  width: 52, height: 52, borderRadius: 999,
                  background: 'linear-gradient(135deg, #a855f7, #3b82f6)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <User size={24} color="#fff" />
                </div>
                <div>
                  <h3 style={{ fontSize: 18, fontWeight: 600, color: '#ffffff' }}>Harsh Tailor</h3>
                  <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>AI Systems Engineer</p>
                </div>
              </div>
              <p style={{ fontSize: 13, color: 'rgba(240,244,255,0.6)', lineHeight: 1.7, marginBottom: 24 }}>
                Specializes in Doc Intelligence ,  designing agentic loops, LLM prompt templates, RAG based systems and structured database integrations. Built AgentDesk as a showcase of production-ready agent deployment using LangGraph, Groq, and Langfuse.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <a
                  href="mailto:harshtailor433@gmail.com"
                  style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'var(--text-secondary)', textDecoration: 'none' }}
                >
                  <Mail size={15} /> harshakhiltaylor@gmail.com
                </a>
                <a
                  href="https://github.com/harshakhiltaylor"
                  target="_blank"
                  rel="noreferrer"
                  style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'var(--text-secondary)', textDecoration: 'none' }}
                >
                  <svg viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg> github.com/harshakhiltaylor
                </a>
                <a
                  href="https://linkedin.com/in/harshakhiltaylor"
                  target="_blank"
                  rel="noreferrer"
                  style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'var(--text-secondary)', textDecoration: 'none' }}
                >
                  <svg viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg> linkedin.com/in/harshakhiltaylor
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* ── Architecture Section ───────────────────────── */}
        <section id="architecture" style={{
          padding: '100px 48px',
          maxWidth: 1100,
          margin: '0 auto',
          width: '100%',
        }}>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(2rem, 4vw, 3.5rem)',
            color: '#f0f4ff',
            marginBottom: 40,
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: 16,
          }}>
            Technical Architecture
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 40 }}>
            {/* Diagram Representation */}
            <div style={{
              display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12,
              background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-subtle)',
              borderRadius: 20, padding: 32, textAlign: 'center', position: 'relative',
            }}>
              {[
                { title: 'Orchestrator', desc: 'State Planner', Icon: Cpu, color: 'var(--accent)' },
                { title: 'Account Agent', desc: 'Tiers & Seat limits', Icon: Database, color: 'rgba(147,197,253,0.85)' },
                { title: 'Feature Agent', desc: 'Setup Guides & Docs', Icon: Brain, color: 'rgba(147,197,253,0.85)' },
                { title: 'Contract Agent', desc: 'SLAs & Legal T&Cs', Icon: GitFork, color: 'rgba(147,197,253,0.85)' },
                { title: 'Escalation Agent', desc: 'P1-P3 Direct Ticketing', Icon: AlertTriangle, color: 'var(--warning)' },
              ].map((step, idx) => (
                <div key={step.title} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, position: 'relative' }}>
                  <div style={{
                    width: 56, height: 56, borderRadius: 16,
                    background: 'var(--bg-surface)', border: '1px solid var(--border-default)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
                  }}>
                    <step.Icon size={24} color={step.color} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: 13, color: '#fff', fontWeight: 600 }}>{step.title}</h4>
                    <p style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>{step.desc}</p>
                  </div>
                  {idx < 4 && (
                    <div style={{
                      position: 'absolute', top: 28, left: 'calc(50% + 40px)', width: 'calc(100% - 80px)',
                      height: 1, background: 'linear-gradient(90deg, var(--border-default), transparent)',
                    }} />
                  )}
                </div>
              ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32 }}>
              <div className="liquid-glass" style={{ borderRadius: 20, padding: 28 }}>
                <h3 style={{ fontSize: 16, fontWeight: 600, color: '#f0f4ff', marginBottom: 16 }}>Runtime Orchestration Loop</h3>
                <ul style={{ paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 14, fontSize: 13, color: 'rgba(240,244,255,0.6)', lineHeight: 1.65 }}>
                  <li><strong>Dynamic State Routing:</strong> Instead of simple sequential routing, the orchestrator evaluates the system context after each node run and decides the next appropriate step dynamically.</li>
                  <li><strong>Unified Memory Context:</strong> All agents post structured findings into a shared state object in LangGraph, ensuring downstream specialists can cross-reference logs.</li>
                  <li><strong>LLM Engine:</strong> Powered by Groq LLaMA-3.3-70B running on custom prompt variables to enforce structured JSON output.</li>
                </ul>
              </div>

              <div className="liquid-glass" style={{ borderRadius: 20, padding: 28 }}>
                <h3 style={{ fontSize: 16, fontWeight: 600, color: '#f0f4ff', marginBottom: 16 }}>Production Observability</h3>
                <ul style={{ paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 14, fontSize: 13, color: 'rgba(240,244,255,0.6)', lineHeight: 1.65 }}>
                  <li><strong>Langfuse Integration:</strong> Full tracing enabled for each agent step, logging raw tool parameters, token usage counts, and intermediate LLM prompts.</li>
                  <li><strong>Failure Tolerance:</strong> Embedded tool handlers catch random timeouts and errors gracefully, returning static fallbacks to guarantee uptime.</li>
                  <li><strong>Security Audits:</strong> Complete isolation of credential storage via environment configurations, eliminating client-side API token leakage.</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* ── Research Section ───────────────────────────── */}
        <section id="research" style={{
          padding: '100px 48px',
          maxWidth: 1100,
          margin: '0 auto',
          width: '100%',
        }}>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(2rem, 4vw, 3.5rem)',
            color: '#f0f4ff',
            marginBottom: 40,
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: 16,
          }}>
            Conflict & Scenario Research
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: '0.8fr 1.2fr', gap: 48, alignItems: 'start' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <p style={{ fontSize: 14, color: 'rgba(240,244,255,0.6)', lineHeight: 1.8 }}>
                The core research challenge behind AgentDesk is identifying discrepancies between <strong>promotional documentation</strong> and <strong>actual database constraints</strong>.
              </p>
              <div style={{
                borderRadius: 16, padding: 20,
                background: 'rgba(251,191,36,0.04)', border: '1px solid rgba(251,191,36,0.15)',
                fontSize: 13, color: 'var(--warning)', lineHeight: 1.6,
              }}>
                <strong>API Rate Limit Contradiction:</strong> Marketing materials claim that Pro tiers get unlimited API endpoints, but the database schema restricts them to 1,000 monthly calls. Our Feature Agent isolates this contradiction and flags it for resolution.
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[
                { title: 'Scenario 1: SLA Violations (Alice Johnson)', desc: 'Enterprise accounts have 4-hour SLA targets with 10% daily MRR refund terms. The Contract Agent detects breaches and routes tickets to Customer Success.' },
                { title: 'Scenario 2: API & Rate Limit Conflicts (Bob Martinez)', desc: 'Identifies discrepancy between marketing specs and system limits, then handles upgrade offers.' },
                { title: 'Scenario 3: Suspended Billing Tiers (Eve Chen)', desc: 'System isolates accounts suspended for non-payment, restricts feature configs, and routes tickets to Finance.' },
                { title: 'Scenario 4: Seat Migration Mismatch (David Lee)', desc: 'Detects accounts exceeding their allocated seat licensing counts, flagging seat overage alerts.' }
              ].map(item => (
                <div key={item.title} className="liquid-glass" style={{ borderRadius: 16, padding: '16px 20px' }}>
                  <h4 style={{ fontSize: 14, fontWeight: 600, color: '#f0f4ff', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <ChevronRight size={14} color="var(--accent)" /> {item.title}
                  </h4>
                  <p style={{ fontSize: 12, color: 'rgba(240,244,255,0.45)', marginTop: 6, lineHeight: 1.6 }}>
                    {item.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Reach Us Section ───────────────────────────── */}
        <section id="reach-us" style={{
          padding: '100px 48px 120px',
          maxWidth: 600,
          margin: '0 auto',
          width: '100%',
        }}>
          <div className="liquid-glass" style={{ borderRadius: 24, padding: '40px 36px', border: '1px solid var(--border-default)' }}>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: '2.2rem',
              color: '#f0f4ff',
              marginBottom: 8,
              textAlign: 'center',
            }}>
              Reach Out
            </h2>
            <p style={{ fontSize: 13, color: 'rgba(240,244,255,0.45)', textAlign: 'center', marginBottom: 32 }}>
              Have questions about AgentDesk or want to discuss AI engineering? Send a message.
            </p>

            {submitted ? (
              <div style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
                padding: '24px 0', textAlign: 'center',
              }}>
                <CheckCircle2 size={36} color="var(--success)" />
                <h4 style={{ fontSize: 15, fontWeight: 600, color: '#fff' }}>Message Sent Successfully!</h4>
                <p style={{ fontSize: 12, color: 'rgba(240,244,255,0.45)' }}>
                  Thank you for reaching out. We will get in touch with you shortly.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Name
                  </label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder="Enter your name"
                    style={{
                      width: '100%', padding: '10px 14px', borderRadius: 8,
                      background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-subtle)',
                      color: '#fff', fontSize: 13, outline: 'none', fontFamily: 'var(--font-body)',
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Email
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    style={{
                      width: '100%', padding: '10px 14px', borderRadius: 8,
                      background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-subtle)',
                      color: '#fff', fontSize: 13, outline: 'none', fontFamily: 'var(--font-body)',
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Message
                  </label>
                  <textarea
                    required
                    rows={4}
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                    placeholder="How can we collaborate?"
                    style={{
                      width: '100%', padding: '10px 14px', borderRadius: 8,
                      background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-subtle)',
                      color: '#fff', fontSize: 13, outline: 'none', fontFamily: 'var(--font-body)',
                      resize: 'none',
                    }}
                  />
                </div>

                <button
                  type="submit"
                  style={{
                    marginTop: 8, padding: '12px 24px', borderRadius: 8, fontSize: 13, fontWeight: 600,
                    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)', color: '#fff',
                    border: 'none', cursor: 'pointer', transition: 'opacity 0.2s',
                    fontFamily: 'var(--font-body)',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.opacity = '0.9')}
                  onMouseLeave={e => (e.currentTarget.style.opacity = '1')}
                >
                  Send Message
                </button>
              </form>
            )}
          </div>
        </section>

        {/* ── Footer ──────────────────────────────────── */}
        <footer style={{
          textAlign: 'center', padding: '40px 0 28px',
          borderTop: '1px solid var(--border-subtle)',
          background: 'rgba(7, 24, 40, 0.4)',
        }}>
          <p style={{ fontSize: 11, color: 'rgba(240,244,255,0.25)', letterSpacing: '0.05em' }}>
            AgentDesk &nbsp;·&nbsp; LangGraph + Groq (LLaMA-3.3-70B) + Langfuse + Flask &nbsp;·&nbsp; Harsh Tailor
          </p>
        </footer>

      </div>
    </div>
  )
}

const FEATURES: { Icon: React.ElementType; title: string; desc: string }[] = [
  {
    Icon: Brain,
    title: 'Cognitive Orchestration',
    desc: 'LLM-driven dynamic planning — no hardcoded routing. Adapts the investigation plan after each agent step.',
  },
  {
    Icon: Zap,
    title: 'Specialist Agents',
    desc: 'Account, Feature, Contract, and Escalation agents own their domain and share unified state memory.',
  },
  {
    Icon: SearchCode,
    title: 'Conflict Detection',
    desc: 'Structural contradiction resolution between documentation and live production database state.',
  },
  {
    Icon: BarChart3,
    title: 'Full Observability',
    desc: 'Langfuse traces every LLM call, tool execution, routing decision, and token cost in production.',
  },
]
