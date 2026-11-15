import { demoTrend } from '@/data/demo-accounting';
import { DemoMoney } from './demo-money';

export function IncomeExpenseChart() {
  return (
    <>
      <div className="mb-6 flex gap-5 text-xs text-ink-muted"><span className="flex items-center gap-2"><i className="size-2.5 rounded-sm bg-brand" />درآمد</span><span className="flex items-center gap-2"><i className="size-2.5 rounded-sm bg-chart-expense" />هزینه</span></div>
      <div role="img" aria-label="مقایسه درآمد و هزینه نمونه از خرداد تا آبان؛ مقادیر دقیق در جدول زیر نمودار آمده است" className="chart-grid flex h-52 items-end justify-around gap-2 border-b border-border-subtle px-1 sm:px-6">
        {demoTrend.map((point) => (
          <div key={point.month} className="flex h-full flex-1 items-end justify-center gap-1.5 sm:gap-2">
            <div className="w-3 rounded-t-md bg-brand sm:w-7" style={{ height: `${point.incomeHeight}%` }} />
            <div className="w-3 rounded-t-md bg-chart-expense sm:w-7" style={{ height: `${point.expenseHeight}%` }} />
          </div>
        ))}
      </div>
      <div aria-hidden="true" className="flex justify-around gap-2 pt-3 text-xs text-ink-muted sm:px-6">{demoTrend.map((point) => <span className="flex-1 text-center" key={point.month}>{point.month}</span>)}</div>
      <details className="mt-5 text-xs text-ink-muted">
        <summary className="w-fit cursor-pointer rounded py-1">مشاهده مقادیر دقیق نمودار</summary>
        <div className="mt-3 overflow-x-auto" tabIndex={0} role="region" aria-label="مقادیر نمودار نمونه">
          <table className="w-full min-w-[28rem] text-start"><caption className="sr-only">درآمد و هزینه ماهانه نمونه</caption><thead><tr>{['ماه', 'درآمد', 'هزینه'].map((label) => <th scope="col" className="py-2 text-start" key={label}>{label}</th>)}</tr></thead><tbody>{demoTrend.map((point) => <tr key={point.month}><th scope="row" className="py-2 text-start font-normal">{point.month}</th><td><DemoMoney rial={point.income} /></td><td><DemoMoney rial={point.expense} /></td></tr>)}</tbody></table>
        </div>
      </details>
    </>
  );
}
