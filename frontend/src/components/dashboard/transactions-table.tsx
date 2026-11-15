import { demoTransactions } from '@/data/demo-accounting';
import { DemoMoney } from './demo-money';
import { Icon } from '@/components/icon';
import { Badge } from '@/components/ui/badge';

export function TransactionsTable() {
  return (
    <div className="overflow-x-auto" role="region" aria-label="جدول تراکنش‌های نمونه" tabIndex={0}>
      <table className="w-full min-w-[38rem] text-start text-sm">
        <caption className="sr-only">تراکنش‌های ساختگی آبان ۱۴۰۵؛ همه موارد نمونه هستند</caption>
        <thead className="bg-surface-muted text-xs text-ink-muted">
          <tr>{['شرح تراکنش', 'دسته‌بندی', 'تاریخ', 'نوع', 'مبلغ'].map((label) => <th key={label} scope="col" className="px-5 py-3 text-start font-medium">{label}</th>)}</tr>
        </thead>
        <tbody className="divide-y divide-border-subtle">
          {demoTransactions.map((transaction) => (
            <tr key={transaction.id} className="hover:bg-surface-muted/60">
              <th scope="row" className="px-5 py-4 text-start font-medium">
                <span className="flex items-center gap-3"><span className={transaction.kind === 'income' ? 'transaction-icon text-success' : 'transaction-icon text-warning'}><Icon name={transaction.kind} /></span>{transaction.title}</span>
              </th>
              <td className="px-5 py-4 text-ink-muted">{transaction.category}</td>
              <td className="whitespace-nowrap px-5 py-4 text-ink-muted">{transaction.date}</td>
              <td className="px-5 py-4"><Badge tone={transaction.kind === 'income' ? 'success' : 'warning'}>{transaction.kind === 'income' ? 'درآمد' : 'هزینه'}</Badge></td>
              <td className="px-5 py-4 font-medium"><DemoMoney rial={transaction.rial} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
