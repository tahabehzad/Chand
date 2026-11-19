import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SalaryRangeGauge } from '../SalaryRangeGauge';

describe('SalaryRangeGauge', () => {
  it('renders P25, P50, and P75 values and labels', () => {
    render(
      <SalaryRangeGauge
        minSalaryRial={350_000_000}
        medianSalaryRial={450_000_000}
        maxSalaryRial={580_000_000}
        primaryEstimateRial={450_000_000}
        legalMinimumWageRial={71_661_840}
      />,
    );

    expect(screen.getByText('محدودهٔ حقوق بازار کار')).toBeInTheDocument();
    // P25 label
    expect(screen.getAllByText('حد پایین').length).toBeGreaterThanOrEqual(1);
    // P50 label
    expect(screen.getAllByText(/میانهٔ بازار/).length).toBeGreaterThanOrEqual(1);
    // P75 label
    expect(screen.getAllByText('حد بالا').length).toBeGreaterThanOrEqual(1);

    // Formatted Toman amounts in Persian numerals:
    // 350M Rial = 35M Toman (۳۵٬۰۰۰٬۰۰۰)
    expect(screen.getAllByText(/۳۵[٬,]۰۰۰[٬,]۰۰۰/).length).toBeGreaterThanOrEqual(1);
    // 450M Rial = 45M Toman (۴۵٬۰۰۰٬۰۰۰)
    expect(screen.getAllByText(/۴۵[٬,]۰۰۰[٬,]۰۰۰/).length).toBeGreaterThanOrEqual(1);
    // 580M Rial = 58M Toman (۵۸٬۰۰۰٬۰۰۰)
    expect(screen.getAllByText(/۵۸[٬,]۰۰۰[٬,]۰۰۰/).length).toBeGreaterThanOrEqual(1);
  });

  it('renders statutory minimum wage reference', () => {
    render(
      <SalaryRangeGauge
        minSalaryRial={300_000_000}
        medianSalaryRial={400_000_000}
        maxSalaryRial={500_000_000}
        primaryEstimateRial={400_000_000}
        legalMinimumWageRial={71_661_840}
      />,
    );

    expect(screen.getByText(/کف قانون کار:/)).toBeInTheDocument();
    expect(screen.getByText(/۷[٬,]۱۶۶[٬,]۱۸۴/)).toBeInTheDocument();
  });
});
