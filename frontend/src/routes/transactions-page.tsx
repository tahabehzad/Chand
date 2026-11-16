import { PageHeader } from '@/app/page-header';
import { Card } from '@/components/ui/card';
import { TransactionsTable } from '@/components/dashboard/transactions-table';
import { DEMO_NOTICE } from '@/data/demo-accounting';

export default function TransactionsPage() {
  return <><PageHeader eyebrow="دریافت‌ها و پرداخت‌ها" title="تراکنش‌های نمونه" description={DEMO_NOTICE} /><Card className="min-w-0 overflow-hidden"><TransactionsTable /></Card><p className="text-xs text-ink-muted">این فهرست فقط خواندنی است و هیچ تراکنش واقعی ثبت نمی‌کند.</p></>;
}
