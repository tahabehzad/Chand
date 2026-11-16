import { formatMoney } from '@/lib/money';
import { useUiStore } from '@/state/ui-store';

export function DemoMoney({ rial }: { rial: string }) {
  const unit = useUiStore((state) => state.preferredUnit);
  const result = formatMoney(rial, unit);
  return <bdi className="tabular whitespace-nowrap">{result.ok ? result.value.text : result.messageFa}</bdi>;
}
