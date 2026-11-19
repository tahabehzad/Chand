import { describe, expect, it } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { CtcBreakdown } from '../CtcBreakdown';

describe('CtcBreakdown Component', () => {
  it('renders breakdown lines and formats Toman via formatMoney', async () => {
    // 400,000,000 Rial = 40,000,000 Toman
    render(<CtcBreakdown grossSalaryRial={400_000_000} />);

    await waitFor(() => {
      expect(
        screen.getByText('تفکیک هزینه کل کارفرما (CTC) و خالص پرداختی'),
      ).toBeInTheDocument();
    });

    // KPI cards
    expect(screen.getByText('خالص دریافتی کارمند')).toBeInTheDocument();
    expect(screen.getAllByText('حقوق ناخالص توافقی').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('هزینه کل کارفرما (CTC)')).toBeInTheDocument();

    // 40,000,000 Toman gross formatted as ۴۰٬۰۰۰٬۰۰۰ تومان
    expect(screen.getAllByText(/۴۰[٬,]۰۰۰[٬,]۰۰۰ تومان/).length).toBeGreaterThanOrEqual(1);

    // Employee deductions breakdown lines
    expect(screen.getByText(/بیمه تأمین اجتماعی سهم کارمند/)).toBeInTheDocument();
    expect(screen.getByText(/مالیات بر درآمد حقوق/)).toBeInTheDocument();

    // Employer overhead lines
    expect(screen.getByText(/حق بیمه تأمین اجتماعی سهم کارفرما/)).toBeInTheDocument();
    expect(screen.getByText(/بیمه بیکاری سهم کارفرما/)).toBeInTheDocument();
    expect(screen.getByText(/ذخیره ماهانه سنوات خدمت/)).toBeInTheDocument();
    expect(screen.getByText(/ذخیره ماهانه عیدی و پاداش/)).toBeInTheDocument();
    expect(screen.getByText('مجموع بالاسری ماهانه کارفرما')).toBeInTheDocument();

    // Annual CTC estimate
    expect(screen.getByText(/سالانه:/)).toBeInTheDocument();
  });
});
