import type { ReactNode } from 'react';
import { PageHeader } from '@/app/page-header';
import { Alert } from '@/components/ui/alert';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/states';
import { Badge } from '@/components/ui/badge';
import { Bdi } from '@/components/ui/bidi';
import type { ContractDefinition } from '@/api/contracts';
import { Icon } from '@/components/icon';

type Props = {
  title: string;
  description: string;
  contract: ContractDefinition;
  /** The frontend task that will build this screen. */
  frontendTask: string;
  planned: readonly string[];
  /**
   * An optional note for a module whose figures are already delivered
   * elsewhere. ADR-008 places the employer cost and the termination
   * liability inside the gross-to-net response, so those screens must say
   * where the real figures live instead of implying that nothing exists.
   */
  note?: ReactNode;
};

/**
 * A module whose data contract does not exist yet.
 *
 * It states the missing contract, the task that owns it and the task that will
 * build the screen. It renders **no** figures and issues **no** request, so a
 * stakeholder cannot mistake this for a working feature, and no fixture stands
 * in for a failed real call.
 */
export function ModulePendingPage({
  title,
  description,
  contract,
  frontendTask,
  planned,
  note,
}: Props) {
  return (
    <>
      <PageHeader
        eyebrow="بخش برنامه‌ریزی‌شده"
        title={title}
        description={description}
        actions={
          <Badge tone="warning">
            {contract.availability === 'delivered' ? 'قرارداد موجود' : 'بدون قرارداد API'}
          </Badge>
        }
      />

      <Alert tone="warning" title="این بخش هنوز قابل استفاده نیست">
        <p>
          قرارداد مورد نیاز:{' '}
          <Bdi className="font-mono">
            {contract.method} {contract.path}
          </Bdi>{' '}
          (شناسه <Bdi className="font-mono">{contract.id}</Bdi>).
        </p>
        <p className="mt-1">
          مالک قرارداد <Bdi>{contract.ownerTask}</Bdi> و مالک این صفحه{' '}
          <Bdi>{frontendTask}</Bdi> است. ساخت این صفحه پیش از تحویل قرارداد، هیچ نتیجه‌ای
          تولید نمی‌کند.
        </p>
        {note ? <div className="mt-2">{note}</div> : null}
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>محتوای برنامه‌ریزی‌شده</CardTitle>
          <CardDescription>
            این فهرست از مشخصات وظیفه گرفته شده و هنوز پیاده‌سازی نشده است.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="flex flex-col gap-2 text-sm text-ink-muted">
            {planned.map((entry) => (
              <li key={entry} className="flex items-start gap-2">
                <Icon name="chevron-previous" className="mt-1 size-4" />
                <span>{entry}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <EmptyState
        title="داده‌ای برای نمایش وجود ندارد"
        description="پس از تحویل قرارداد و پیاده‌سازی این صفحه، نتایج واقعی سرویس در همین جایگاه نمایش داده می‌شود. در این نسخه هیچ داده ساختگی نمایش داده نمی‌شود."
        action={<Badge tone="neutral">در انتظار {contract.ownerTask}</Badge>}
      />
    </>
  );
}
