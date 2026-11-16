import { Component, type ErrorInfo, type ReactNode } from 'react';
import { ErrorState } from '@/components/ui/states';

type Props = { children: ReactNode };
type State = { error: Error | null };

/**
 * A render failure is shown, never swallowed and never replaced with synthetic
 * content. No stack trace or payload is displayed: it could contain candidate
 * data, and the correlation id belongs to the API layer.
 */
export class RouteErrorBoundary extends Component<Props, State> {
  override state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  override componentDidCatch(error: Error, info: ErrorInfo): void {
    // Console only; no candidate data or token is logged by this boundary.
    console.error('route_render_failed', error.name, info.componentStack?.split('\n')[1] ?? '');
  }

  override render(): ReactNode {
    if (this.state.error !== null) {
      return (
        <div className="p-6">
          <ErrorState
            title="نمایش این بخش ممکن نشد"
            description="یک خطای غیرمنتظره در رابط رخ داد. اطلاعات نمایش‌داده‌شده نامعتبر است و نباید مبنای تصمیم قرار گیرد."
            onRetry={() => this.setState({ error: null })}
          />
        </div>
      );
    }
    return this.props.children;
  }
}
