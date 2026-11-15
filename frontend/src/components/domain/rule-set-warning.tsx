import { Alert } from '@/components/ui/alert';
import { LtrRun } from '@/components/ui/bidi';
import {
  RULE_SET_STATUS_LABELS_FA,
  needsRuleSetWarning,
  type FigureProvenance,
} from '@/api/provenance';

/**
 * The `rule_set_status` warning surface — `P3-T05` acceptance criterion.
 *
 * A non-`VERIFIED` rule set must surface here. The three statutory facts stay
 * in separate fields: the year is never concatenated with a verification claim.
 */
export function RuleSetWarning({
  provenance,
}: {
  provenance: Pick<FigureProvenance, 'rule_version' | 'rule_set_status' | 'is_verified'>;
}) {
  if (!needsRuleSetWarning(provenance)) return null;

  return (
    <Alert tone="warning" title="نسخه قوانین این نتیجه در وضعیت تأییدشده نیست">
      <p>
        سال قانونی: <bdi>{provenance.rule_version}</bdi> — وضعیت:{' '}
        {RULE_SET_STATUS_LABELS_FA[provenance.rule_set_status]} — تأییدشده:{' '}
        {provenance.is_verified ? 'بله' : 'خیر'}
      </p>
      <p className="mt-1">
        این نتیجه نباید به‌عنوان مبنای قانونی تأییدشده ارائه شود و نیازمند بازبینی انسانی است.
      </p>
    </Alert>
  );
}

/** Provenance footer for a computed figure: version, engine, hash — LTR-isolated. */
export function ProvenanceFooter({ provenance }: { provenance: FigureProvenance }) {
  return (
    <dl className="grid grid-cols-1 gap-x-6 gap-y-1 text-xs text-ink-muted sm:grid-cols-2">
      <div className="flex gap-1">
        <dt>نسخه قواعد:</dt>
        <dd>
          <bdi>{provenance.rule_version}</bdi>
        </dd>
      </div>
      <div className="flex gap-1">
        <dt>نسخه موتور:</dt>
        <dd>
          <bdi>{provenance.engine_version}</bdi>
        </dd>
      </div>
      <div className="flex gap-1">
        <dt>هش محاسبه:</dt>
        <dd>
          <LtrRun className="font-mono">{provenance.calculation_hash}</LtrRun>
        </dd>
      </div>
      <div className="flex gap-1">
        <dt>زمان تولید:</dt>
        <dd>
          <LtrRun className="font-mono">{provenance.generated_at}</LtrRun>
        </dd>
      </div>
    </dl>
  );
}
