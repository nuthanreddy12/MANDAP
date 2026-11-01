import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface Props {
  children: ReactNode
  fallbackTitle?: string
  fallbackMessage?: string
  onReset?: () => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ error, errorInfo })
    console.error('ErrorBoundary caught an unhandled runtime error:', error, errorInfo)
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
    if (this.props.onReset) {
      this.props.onReset()
    }
  }

  public render() {
    if (this.state.hasError) {
      const title = this.props.fallbackTitle || 'Module Temporarily Unavailable'
      const message =
        this.props.fallbackMessage ||
        'An unexpected runtime error occurred while rendering this module. Your wedding data is safe.'

      return (
        <div className="p-6 md:p-10 max-w-3xl mx-auto my-8 bg-white border border-[#E8E2D9] rounded-3xl shadow-sm text-center space-y-5">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700">
            <AlertTriangle className="w-7 h-7" />
          </div>

          <div className="space-y-2">
            <span className="text-[10px] uppercase tracking-wider font-semibold text-bronze block">
              Protected Recovery State
            </span>
            <h2 className="font-serif text-2xl font-bold text-ink">{title}</h2>
            <p className="text-xs text-ink-muted max-w-md mx-auto leading-relaxed">{message}</p>
          </div>

          {this.state.error && (
            <div className="text-left bg-[#FAF8F5] border border-warm-stone/60 p-4 rounded-xl font-mono text-[11px] text-ink-muted max-h-40 overflow-y-auto">
              <p className="font-semibold text-red-700 mb-1">{this.state.error.toString()}</p>
              {this.state.errorInfo?.componentStack && (
                <pre className="text-[10px] text-ink-muted whitespace-pre-wrap">
                  {this.state.errorInfo.componentStack.trim().slice(0, 500)}
                </pre>
              )}
            </div>
          )}

          <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
            <Button
              variant="bronze"
              size="md"
              leftIcon={<RefreshCw className="w-4 h-4" />}
              onClick={this.handleReset}
            >
              Retry Module
            </Button>
            <Button
              variant="outline"
              size="md"
              leftIcon={<Home className="w-4 h-4" />}
              onClick={() => {
                window.location.href = '/weddings'
              }}
            >
              Return to Weddings Desk
            </Button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
