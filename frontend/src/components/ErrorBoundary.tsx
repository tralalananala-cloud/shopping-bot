import { Component, type ReactNode } from 'react'

interface Props { children: ReactNode }
interface State { error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  render() {
    const { error } = this.state
    if (error) {
      return (
        <div
          style={{
            minHeight: '100vh',
            background: 'hsl(240 14% 2%)',
            color: 'hsl(0 0% 100%)',
            fontFamily: 'Space Grotesk, sans-serif',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
            gap: '12px',
          }}
        >
          <div style={{ fontSize: '2rem' }}>⚠️</div>
          <p style={{ fontWeight: 600, fontSize: '1rem', textAlign: 'center' }}>
            Ceva nu a funcționat
          </p>
          <pre
            style={{
              background: 'hsl(240 10% 8%)',
              border: '1px solid hsl(0 0% 100% / 0.1)',
              borderRadius: '12px',
              padding: '12px',
              fontSize: '0.7rem',
              color: 'hsl(0 84% 70%)',
              overflowX: 'auto',
              maxWidth: '100%',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
            }}
          >
            {error.message}
            {'\n'}
            {error.stack?.split('\n').slice(0, 5).join('\n')}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: 'hsl(185 100% 50%)',
              color: 'hsl(240 14% 2%)',
              border: 'none',
              borderRadius: '12px',
              padding: '10px 24px',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '0.875rem',
            }}
          >
            Reîncarcă
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
