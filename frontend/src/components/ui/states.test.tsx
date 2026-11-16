import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EmptyState, ErrorState, LoadingSkeleton, LoadingState } from './states';

describe('LoadingState', () => {
  it('announces politely through a status role', () => {
    render(<LoadingState />);
    expect(screen.getByRole('status')).toHaveTextContent('در حال بارگذاری');
  });
});

describe('LoadingSkeleton', () => {
  it('is labelled for assistive technology', () => {
    render(<LoadingSkeleton rows={2} />);
    expect(screen.getByRole('status', { name: 'در حال بارگذاری…' })).toBeInTheDocument();
  });
});

describe('EmptyState', () => {
  it('renders a heading, a description and an optional action', () => {
    render(
      <EmptyState title="داده‌ای نیست" description="توضیح حالت خالی" action={<button>اقدام</button>} />,
    );
    expect(screen.getByRole('heading', { name: 'داده‌ای نیست' })).toBeInTheDocument();
    expect(screen.getByText('توضیح حالت خالی')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'اقدام' })).toBeInTheDocument();
  });
});

describe('ErrorState', () => {
  it('uses the alert role and shows the correlation id in a bidi-isolated run', () => {
    render(
      <ErrorState description="اتصال برقرار نشد" correlationId="req-abc-123" />,
    );
    expect(screen.getByRole('alert')).toHaveTextContent('اتصال برقرار نشد');
    expect(screen.getByText('req-abc-123').closest('bdi')).not.toBeNull();
  });

  it('calls the retry handler exactly once', async () => {
    const onRetry = vi.fn();
    render(<ErrorState description="خطا" onRetry={onRetry} />);
    await userEvent.click(screen.getByRole('button', { name: 'تلاش دوباره' }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
