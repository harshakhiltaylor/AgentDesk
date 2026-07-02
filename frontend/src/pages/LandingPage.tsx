import { useNavigate } from 'react-router-dom'
import { Brain, Zap, SearchCode, BarChart3, ArrowUpRight } from 'lucide-react'

const VIDEO_URL =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260314_131748_f2ca2a28-fed7-44c8-b9a9-bd9acdd5ec31.mp4'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div style={{ position: 'relative', minHeight: '100vh', overflow: 'hidden', background: '#071828' }}>

      {/* ── Background Video ────────────────────────────── */}
      <video
        autoPlay loop muted playsInline
        style={{
          position: 'absolute', inset: 0,
          width: '100%', height: '100%',
          objectFit: 'cover', zIndex: 0,
        }}
      >
        <source src={VIDEO_URL} type="video/mp4" />
      </video>

      {/* ── Gradient scrim for text legibility ─────────── */}
      <div style={{
        position: 'absolute', inset: 0, zIndex: 1,
        background: 'linear-gradient(to bottom, rgba(5,8,16,0.45) 0%, rgba(5,8,16,0.25) 50%, rgba(5,8,16,0.80) 100%)',
      }} />

      {/* ── All content ─────────────────────────────────── */}
      <div style={{ position: 'relative', zIndex: 10, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>

        {/* ── Nav ─────────────────────────────────────── */}
        <nav style={{ padding: '28px 48px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
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
            {['Home', 'About', 'Architecture', 'Research', 'Reach Us'].map((l, i) => (
              <span key={l} style={{
                fontSize: 14, cursor: 'pointer',
                color: i === 0 ? '#f0f4ff' : 'rgba(240,244,255,0.5)',
                transition: 'color 0.2s',
              }}
                onMouseEnter={e => (e.currentTarget.style.color = '#f0f4ff')}
                onMouseLeave={e => (e.currentTarget.style.color = i === 0 ? '#f0f4ff' : 'rgba(240,244,255,0.5)')}
              >{l}</span>
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

        {/* ── Hero ────────────────────────────────────── */}
        <section style={{
          flex: 1,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          textAlign: 'center',
          padding: '60px 48px 40px',
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

          {/* H1 — fixed: no overflow, proper max-width + word-break */}
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

          {/* Scroll hint */}
          <div
            className="animate-fade-rise-delay-3"
            style={{ marginTop: 60, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}
          >
            <span style={{ fontSize: 10, letterSpacing: '0.15em', textTransform: 'uppercase', color: 'rgba(240,244,255,0.28)' }}>
              Scroll
            </span>
            <div style={{ width: 1, height: 32, background: 'linear-gradient(to bottom, rgba(240,244,255,0.2), transparent)' }} />
          </div>
        </section>

        {/* ── Feature Strip ───────────────────────────── */}
        <section style={{ padding: '0 48px 64px' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: 16,
            maxWidth: 1100,
            margin: '0 auto',
          }}>
            {FEATURES.map((f, i) => (
              <div
                key={f.title}
                className={`liquid-glass animate-fade-rise-delay-${Math.min(i + 2, 3) as 2 | 3}`}
                style={{ borderRadius: 20, padding: '22px 20px' }}
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

        {/* ── Footer ──────────────────────────────────── */}
        <footer style={{ textAlign: 'center', paddingBottom: 28 }}>
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
