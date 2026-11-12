'use client';

// Local ErrorBoundary: isolates a failing block so the page does not go blank.
// Wrap each content area / feature with it, not only the whole app.
import { Component, type ReactNode } from 'react';

// `message` and `retryLabel` are required (no default): UI text must follow the client-facing language,
// so copying this file never leaks an internal language into the customer UI.
type Props = { children: ReactNode; message: string; retryLabel: string; label?: string; onRetry?: () => void };
type State = { error: Error | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: { componentStack?: string | null }) {
    // Report to the project's logging/monitoring; never show a stack trace to the user.
    console.error('[ErrorBoundary]', this.props.label ?? 'block', error.message, info.componentStack);
  }

  private retry = () => {
    this.setState({ error: null });
    this.props.onRetry?.();
  };

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div role="alert" className="rounded-md border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <p className="font-medium text-slate-900 dark:text-slate-100">{this.props.message}</p>
        <button type="button" onClick={this.retry} className="mt-3 rounded-md border px-3 py-1.5 text-sm">
          {this.props.retryLabel}
        </button>
      </div>
    );
  }
}
