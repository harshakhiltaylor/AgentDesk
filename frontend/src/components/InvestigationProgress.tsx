import { Brain, Search, Scale, PenLine } from 'lucide-react'

interface InvestigationProgressProps {
  isLoading: boolean
  step: number
}

const STEPS = [
  { icon: Brain,   label: 'Orchestrator analyzing query and building investigation plan…' },
  { icon: Search,  label: 'Specialist agents gathering data from connected tools…' },
  { icon: Scale,   label: 'Cross-referencing findings across all agent outputs…' },
  { icon: PenLine, label: 'Synthesizing final customer-facing response…' },
]

export default function InvestigationProgress({ isLoading, step }: InvestigationProgressProps) {
  if (!isLoading) return null

  const progress = Math.min(8 + step * 23, 90)
  const current  = STEPS[step % STEPS.length]
  const StepIcon = current.icon

  return (
    <div style={{
      borderRadius: 16,
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      padding: '20px 24px',
      marginBottom: 20,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: 'var(--accent)',
            animation: 'pulse-dot 1.2s infinite',
          }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
            Investigation Running
          </span>
        </div>
        <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'monospace' }}>
          {Math.round(progress)}%
        </span>
      </div>

      {/* Progress bar */}
      <div style={{
        width: '100%', height: 4, borderRadius: 99,
        background: 'var(--bg-elevated)', overflow: 'hidden', marginBottom: 16,
      }}>
        <div
          className="progress-shimmer"
          style={{ height: '100%', borderRadius: 99, width: `${progress}%`, transition: 'width 0.6s ease' }}
        />
      </div>

      {/* Current step */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8, flexShrink: 0,
          background: 'var(--accent-soft)',
          border: '1px solid rgba(59,130,246,0.18)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <StepIcon size={15} color="var(--accent)" strokeWidth={2} />
        </div>
        <span style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
          {current.label}
        </span>
      </div>

      {/* Step dots */}
      <div style={{ display: 'flex', gap: 6, marginTop: 16 }}>
        {STEPS.map((_, i) => (
          <div key={i} style={{
            height: 3, borderRadius: 99,
            flex: i <= step % STEPS.length ? 2 : 1,
            background: i <= step % STEPS.length ? 'var(--accent)' : 'var(--bg-elevated)',
            transition: 'flex 0.4s ease, background 0.4s ease',
          }} />
        ))}
      </div>
    </div>
  )
}
