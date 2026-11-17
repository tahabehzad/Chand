import { useCallback, useEffect, useId, useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { PageHeader } from '@/app/page-header';
import { Icon } from '@/components/icon';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { EmptyState, ErrorState, LoadingSkeleton } from '@/components/ui/states';
import {
  addObservation,
  correctObservation,
  evaluatePerson,
  getPerson,
  getRules,
  importObservations,
  isPrototypeError,
  listEvidence,
  listObservations,
  listRecommendations,
  rejectObservation,
  updatePerson,
  uploadEvidence,
} from '@/prototype/api';
import type {
  DecisionAction,
  EvaluationRules,
  Evidence,
  ImportSummary,
  MetricCode,
  Observation,
  Person,
  RecommendationSummary,
} from '@/prototype/types';
import { PrototypeNotice } from './prototype-notice';
import { faDigits, isoDateText, rialText } from './format';

const STATE_LABELS: Record<Observation['state'], string> = {
  valid: 'معتبر',
  corrected: 'اصلاح‌شده',
  rejected: 'ردشده',
};

const STATE_TONES: Record<Observation['state'], 'success' | 'info' | 'danger'> = {
  valid: 'success',
  corrected: 'info',
  rejected: 'danger',
};

const SOURCE_LABELS: Record<Observation['source'], string> = {
  manual: 'ورود دستی',
  import: 'ورود از فایل',
};

const DECISION_LABELS: Record<DecisionAction, string> = {
  approve: 'تأیید',
  edit: 'ویرایش',
  reject: 'رد',
};

const DECISION_TONES: Record<DecisionAction, 'success' | 'info' | 'danger'> = {
  approve: 'success',
  edit: 'info',
  reject: 'danger',
};

function messageOf(caught: unknown, fallback: string): string {
  return isPrototypeError(caught) ? caught.message : fallback;
}

export default function PrototypePersonPage() {
  const { personId } = useParams<{ personId: string }>();
  const navigate = useNavigate();
  const importInputId = useId();
  const evidenceInputId = useId();
  const noteInputId = useId();

  const [person, setPerson] = useState<Person | null>(null);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [rules, setRules] = useState<EvaluationRules | null>(null);
  const [history, setHistory] = useState<RecommendationSummary[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [profileOpen, setProfileOpen] = useState(false);
  const [profileName, setProfileName] = useState('');
  const [profileRole, setProfileRole] = useState('');
  const [profileStartDate, setProfileStartDate] = useState('');

  const [code, setCode] = useState<MetricCode>('sales');
  const [period, setPeriod] = useState('1404-Q2');
  const [raw, setRaw] = useState('');
  const [editId, setEditId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  const [importFile, setImportFile] = useState<File | null>(null);
  const [importResult, setImportResult] = useState<ImportSummary | null>(null);
  const [evidenceFile, setEvidenceFile] = useState<File | null>(null);
  const [evidenceNote, setEvidenceNote] = useState('');

  const [bandMin, setBandMin] = useState('80000000');
  const [bandMax, setBandMax] = useState('140000000');
  const [current, setCurrent] = useState('100000000');

  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async (): Promise<void> => {
    if (personId === undefined) {
      setLoaded(true);
      return;
    }
    try {
      setLoadError(null);
      const [loadedPerson, loadedRules] = await Promise.all([getPerson(personId), getRules()]);
      setPerson(loadedPerson);
      setRules(loadedRules);
      if (loadedPerson !== null) {
        const [loadedObservations, loadedEvidence, loadedHistory] = await Promise.all([
          listObservations(personId),
          listEvidence(personId),
          listRecommendations(personId),
        ]);
        setObservations(loadedObservations);
        setEvidence(loadedEvidence);
        setHistory(loadedHistory);
        setProfileName(loadedPerson.name);
        setProfileRole(loadedPerson.role);
        setProfileStartDate(loadedPerson.startDate);
      }
    } catch (caught) {
      setLoadError(messageOf(caught, 'دریافت اطلاعات کارمند ناموفق بود.'));
    } finally {
      setLoaded(true);
    }
  }, [personId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function run(task: () => Promise<void>, fallback: string): Promise<void> {
    setBusy(true);
    setError(null);
    try {
      await task();
    } catch (caught) {
      setError(messageOf(caught, fallback));
    } finally {
      setBusy(false);
    }
  }

  async function onSaveProfile(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (personId === undefined) return;
    await run(async () => {
      const updated = await updatePerson(personId, {
        name: profileName,
        role: profileRole,
        startDate: profileStartDate,
      });
      setPerson(updated);
      setProfileOpen(false);
      await load();
    }, 'ویرایش اطلاعات کارمند ناموفق بود.');
  }

  async function onAdd(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (personId === undefined) return;
    await run(async () => {
      await addObservation({ personId, code, period, raw });
      setRaw('');
      await load();
    }, 'ثبت مشاهده ناموفق بود.');
  }

  async function onCorrect(observationId: string): Promise<void> {
    await run(async () => {
      await correctObservation(observationId, editValue);
      setEditId(null);
      setEditValue('');
      await load();
    }, 'اصلاح مشاهده ناموفق بود.');
  }

  async function onReject(observationId: string): Promise<void> {
    await run(async () => {
      await rejectObservation(observationId);
      await load();
    }, 'رد مشاهده ناموفق بود.');
  }

  async function onImport(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (personId === undefined || importFile === null) return;
    await run(async () => {
      setImportResult(await importObservations(personId, importFile));
      setImportFile(null);
      await load();
    }, 'بارگذاری فایل ناموفق بود.');
  }

  async function onEvidence(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (personId === undefined || evidenceFile === null) return;
    await run(async () => {
      await uploadEvidence(personId, evidenceFile, evidenceNote);
      setEvidenceFile(null);
      setEvidenceNote('');
      await load();
    }, 'بارگذاری شواهد ناموفق بود.');
  }

  async function onEvaluate(): Promise<void> {
    if (personId === undefined) return;
    await run(async () => {
      const recommendation = await evaluatePerson(personId, {
        bandMinRial: bandMin,
        bandMaxRial: bandMax,
        currentRial: current,
      });
      navigate(`/prototype/recommendations/${recommendation.id}`);
    }, 'محاسبهٔ امتیاز و پیشنهاد ناموفق بود.');
  }

  if (!loaded) {
    return <LoadingSkeleton rows={5} />;
  }

  if (person === null) {
    return (
      <EmptyState
        title="این کارمند یافت نشد"
        description={
          loadError ??
          'شناسهٔ درخواستی در سازمانِ نشست شما وجود ندارد. فهرست کارکنان را دوباره بررسی کنید.'
        }
        action={
          <Button asChild variant="secondary">
            <Link to="/prototype/people">بازگشت به فهرست کارکنان</Link>
          </Button>
        }
      />
    );
  }

  const valid = observations.filter((observation) => observation.state !== 'rejected');
  const covered = new Set(valid.map((observation) => observation.code));
  const criteria = rules?.criteria ?? [];
  const missing = criteria.filter((criterion) => !covered.has(criterion.code));
  const selected = criteria.find((criterion) => criterion.code === code);
  const duplicateKeys = new Map<string, number>();
  for (const observation of valid) {
    const key = `${observation.code}::${observation.period}`;
    duplicateKeys.set(key, (duplicateKeys.get(key) ?? 0) + 1);
  }
  const conflicting = [...duplicateKeys.entries()]
    .filter(([, count]) => count > 1)
    .map(([key]) => {
      const [metricCode, duplicatePeriod] = key.split('::');
      const label = criteria.find((criterion) => criterion.code === metricCode)?.labelFa;
      return `${label ?? metricCode} در دورهٔ ${duplicatePeriod}`;
    });

  return (
    <>
      <PageHeader
        eyebrow="گام ۲ از ۴ · کارمند"
        title={person.name}
        description={`${person.role} · شروع ${isoDateText(person.startDate)} · شناسهٔ داخلی ${person.id}`}
        actions={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => setProfileOpen((open) => !open)}>
              {profileOpen ? 'بستن ویرایش' : 'ویرایش اطلاعات'}
            </Button>
            <Button asChild variant="secondary">
              <Link to="/prototype/people">
                <Icon name="arrow-back" />
                فهرست کارکنان
              </Link>
            </Button>
          </div>
        }
      />

      <PrototypeNotice compact />

      {loadError ? (
        <ErrorState description={loadError} onRetry={() => void load()} />
      ) : null}

      {error ? (
        <div
          role="alert"
          className="rounded-lg border border-danger/40 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          {error}
        </div>
      ) : null}

      {profileOpen ? (
        <Card>
          <CardHeader>
            <CardTitle>ویرایش اطلاعات کارمند</CardTitle>
            <CardDescription>همان اعتبارسنجی سرور روی هر سه فیلد اعمال می‌شود.</CardDescription>
          </CardHeader>
          <CardContent>
            <form
              className="grid gap-4 sm:grid-cols-3"
              onSubmit={(event) => void onSaveProfile(event)}
            >
              <Input
                label="نام نمایشی"
                value={profileName}
                onChange={(event) => setProfileName(event.target.value)}
                maxLength={120}
                required
              />
              <Input
                label="عنوان شغلی"
                value={profileRole}
                onChange={(event) => setProfileRole(event.target.value)}
                maxLength={60}
                required
              />
              <Input
                label="تاریخ شروع (میلادی)"
                value={profileStartDate}
                onChange={(event) => setProfileStartDate(event.target.value)}
                dir="ltr"
                maxLength={10}
                required
              />
              <div className="sm:col-span-3">
                <Button type="submit" disabled={busy}>
                  {busy ? 'در حال ذخیره…' : 'ذخیرهٔ تغییرات'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.5fr)]">
        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>ثبت دادهٔ عملکرد</CardTitle>
            <CardDescription>
              هر مشاهده یک منبع، یک دوره و یک مقدار دارد. بازه و وزن هر معیار از سرور خوانده
              می‌شود؛ مرورگر خودش امتیاز نمی‌دهد.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="flex flex-col gap-4" onSubmit={(event) => void onAdd(event)}>
              <div className="flex flex-col gap-2">
                <label htmlFor="criterion" className="text-sm font-medium text-ink">
                  معیار
                </label>
                <select
                  id="criterion"
                  value={code}
                  onChange={(event) => setCode(event.target.value as MetricCode)}
                  className="min-h-11 w-full rounded-lg border border-border-subtle bg-surface-raised px-3 text-sm text-ink"
                >
                  {criteria.map((criterion) => (
                    <option key={criterion.code} value={criterion.code}>
                      {criterion.labelFa} — وزن {faDigits(criterion.weightBp / 100)}٪
                    </option>
                  ))}
                </select>
                {selected ? (
                  <p className="text-xs text-ink-muted">
                    واحد: {selected.unitFa} · {selected.guidanceFa}
                  </p>
                ) : null}
              </div>
              <Input
                label="دورهٔ ارزیابی"
                value={period}
                onChange={(event) => setPeriod(event.target.value)}
                hint="برچسب آزاد؛ مثلاً 1404-Q2 یا 1404-08"
                maxLength={40}
                required
              />
              <Input
                label="مقدار"
                value={raw}
                onChange={(event) => setRaw(event.target.value)}
                hint="عدد صحیح؛ ارقام فارسی هم پذیرفته و به ASCII تبدیل می‌شوند."
                dir="ltr"
                inputMode="numeric"
                required
              />
              <Button type="submit" disabled={busy}>
                {busy ? 'در حال ثبت…' : 'افزودن مشاهده'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>مشاهدات ثبت‌شده</CardTitle>
            <CardDescription>
              مشاهدهٔ ردشده در امتیاز وارد نمی‌شود. اصلاح، مقدار را جایگزین می‌کند و وضعیت را
              «اصلاح‌شده» می‌گذارد.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            {observations.length === 0 ? (
              <EmptyState
                title="هیچ مشاهده‌ای ثبت نشده"
                description="دست‌کم یک معیار را وارد کنید تا امتیازدهی ممکن شود."
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[44rem] text-sm">
                  <thead>
                    <tr className="text-start text-xs text-ink-muted">
                      <th className="px-2 py-2 text-start font-medium">معیار</th>
                      <th className="px-2 py-2 text-start font-medium">دوره</th>
                      <th className="px-2 py-2 text-start font-medium">مقدار</th>
                      <th className="px-2 py-2 text-start font-medium">منبع</th>
                      <th className="px-2 py-2 text-start font-medium">وضعیت</th>
                      <th className="px-2 py-2 text-start font-medium">اقدام</th>
                    </tr>
                  </thead>
                  <tbody>
                    {observations.map((observation) => {
                      const definition = criteria.find(
                        (criterion) => criterion.code === observation.code,
                      );
                      return (
                        <tr key={observation.id} className="border-t border-border-subtle">
                          <td className="px-2 py-2">{definition?.labelFa ?? observation.code}</td>
                          <td className="px-2 py-2 text-ink-muted">{observation.period}</td>
                          <td className="px-2 py-2 tabular">
                            {faDigits(observation.raw)}
                            {definition ? (
                              <span className="ms-1 text-xs text-ink-muted">
                                {definition.code === 'sales' ? 'ریال' : ''}
                              </span>
                            ) : null}
                          </td>
                          <td className="px-2 py-2 text-xs text-ink-muted">
                            {SOURCE_LABELS[observation.source]}
                          </td>
                          <td className="px-2 py-2">
                            <Badge tone={STATE_TONES[observation.state]}>
                              {STATE_LABELS[observation.state]}
                            </Badge>
                          </td>
                          <td className="px-2 py-2">
                            {observation.state === 'rejected' ? (
                              <span className="text-xs text-ink-muted">—</span>
                            ) : editId === observation.id ? (
                              <span className="flex flex-wrap items-center gap-2">
                                <input
                                  value={editValue}
                                  onChange={(event) => setEditValue(event.target.value)}
                                  dir="ltr"
                                  inputMode="numeric"
                                  aria-label={`مقدار اصلاح‌شدهٔ ${definition?.labelFa ?? observation.code}`}
                                  className="min-h-9 w-24 rounded-lg border border-border-subtle px-2 text-end tabular"
                                />
                                <Button
                                  size="sm"
                                  onClick={() => void onCorrect(observation.id)}
                                  disabled={busy}
                                >
                                  ثبت
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => setEditId(null)}
                                >
                                  انصراف
                                </Button>
                              </span>
                            ) : (
                              <span className="flex flex-wrap items-center gap-2">
                                <Button
                                  size="sm"
                                  variant="secondary"
                                  onClick={() => {
                                    setEditId(observation.id);
                                    setEditValue(observation.raw);
                                  }}
                                >
                                  اصلاح
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => void onReject(observation.id)}
                                  disabled={busy}
                                >
                                  رد
                                </Button>
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}

            <div className="rounded-lg border border-border-subtle bg-surface px-3 py-2 text-xs">
              <p className="font-medium text-ink">کیفیت داده</p>
              {missing.length > 0 ? (
                <p className="mt-1 text-warning">
                  معیارهای ثبت‌نشده:{' '}
                  {missing.map((criterion) => criterion.labelFa).join('، ')}. این معیارها صفر
                  امتیاز می‌گیرند و وزن‌ها بازمحاسبه نمی‌شوند.
                </p>
              ) : (
                <p className="mt-1 text-ink-muted">همهٔ معیارهای مدل برای این کارمند داده دارند.</p>
              )}
              {conflicting.length > 0 ? (
                <p className="mt-1 text-warning">
                  دادهٔ هم‌پوشان: {conflicting.join('، ')}. امتیاز از آخرین مشاهدهٔ ثبت‌شده
                  استفاده می‌کند؛ برای رفع ابهام یکی را رد کنید.
                </p>
              ) : null}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>بارگذاری داده از فایل</CardTitle>
            <CardDescription>
              یک فایل CSV با کدگذاری UTF-8 و ستون‌های <bdi dir="ltr">metric_code,period,raw_value</bdi>.
              هر سطر جداگانه اعتبارسنجی می‌شود.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="flex flex-col gap-3" onSubmit={(event) => void onImport(event)}>
              <label htmlFor={importInputId} className="text-sm font-medium text-ink">
                فایل مشاهدات
              </label>
              <input
                id={importInputId}
                type="file"
                accept=".csv,text/csv"
                onChange={(event) => setImportFile(event.target.files?.[0] ?? null)}
                className="min-h-11 w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink"
              />
              <Button type="submit" disabled={busy || importFile === null}>
                {busy ? 'در حال بارگذاری…' : 'بارگذاری فایل'}
              </Button>
            </form>
            {importResult ? (
              <div className="mt-4 flex flex-col gap-2 text-sm">
                <p className="text-success">
                  {faDigits(importResult.imported)} سطر ثبت شد و{' '}
                  {faDigits(importResult.rejected.length)} سطر رد شد.
                </p>
                {importResult.rejected.length > 0 ? (
                  <ul className="list-inside list-disc text-xs text-warning">
                    {importResult.rejected.map((row) => (
                      <li key={`${row.row}-${row.reason}`}>
                        سطر {faDigits(row.row)}: {row.reason}
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>شواهد پشتیبان</CardTitle>
            <CardDescription>
              فایل حداکثر ۵ مگابایت؛ اثر انگشت SHA-256 در سرور محاسبه و با فراداده ذخیره می‌شود.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <form className="flex flex-col gap-3" onSubmit={(event) => void onEvidence(event)}>
              <label htmlFor={evidenceInputId} className="text-sm font-medium text-ink">
                فایل شاهد
              </label>
              <input
                id={evidenceInputId}
                type="file"
                onChange={(event) => setEvidenceFile(event.target.files?.[0] ?? null)}
                className="min-h-11 w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink"
              />
              <label htmlFor={noteInputId} className="text-sm font-medium text-ink">
                یادداشت (اختیاری)
              </label>
              <textarea
                id={noteInputId}
                value={evidenceNote}
                onChange={(event) => setEvidenceNote(event.target.value)}
                rows={2}
                maxLength={500}
                className="w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink"
              />
              <Button type="submit" disabled={busy || evidenceFile === null}>
                {busy ? 'در حال بارگذاری…' : 'افزودن شاهد'}
              </Button>
            </form>
            {evidence.length === 0 ? (
              <p className="text-xs text-ink-muted">هنوز شاهدی بارگذاری نشده است.</p>
            ) : (
              <ul className="flex flex-col gap-2 text-sm">
                {evidence.map((item) => (
                  <li
                    key={item.id}
                    className="rounded-lg border border-border-subtle bg-surface px-3 py-2"
                  >
                    <p className="font-medium text-ink">{item.fileName}</p>
                    <p className="text-xs text-ink-muted">
                      {faDigits(item.byteSize)} بایت · {item.contentType} ·{' '}
                      {isoDateText(item.createdAt)}
                    </p>
                    <p className="mt-1 break-all font-mono text-[11px] text-ink-muted" dir="ltr">
                      {item.sha256}
                    </p>
                    {item.note ? <p className="mt-1 text-xs">{item.note}</p> : null}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      {rules ? (
        <p className="rounded-lg border border-border-subtle bg-surface px-3 py-2 text-xs text-ink-muted">
          مدل: <bdi dir="ltr">{rules.ruleSetVersion}</bdi> · وضعیت: {rules.statusLabelFa}.{' '}
          {rules.missingPolicyFa}
        </p>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>محاسبهٔ امتیاز و ساخت پیشنهاد</CardTitle>
          <CardDescription>
            بازهٔ حقوق را مدیر تعیین می‌کند؛ سرور امتیاز را محاسبه می‌کند، جایگاه آن را در بازه
            می‌یابد و هزینهٔ قانونی مبلغ پیشنهادی را از موتور ۱۴۰۴ می‌گیرد.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <Input
              label="حداقل بازه (ریال)"
              value={bandMin}
              onChange={(event) => setBandMin(event.target.value)}
              dir="ltr"
              inputMode="numeric"
              required
            />
            <Input
              label="حداکثر بازه (ریال)"
              value={bandMax}
              onChange={(event) => setBandMax(event.target.value)}
              dir="ltr"
              inputMode="numeric"
              required
            />
            <Input
              label="حقوق فعلی (ریال، اختیاری)"
              value={current}
              onChange={(event) => setCurrent(event.target.value)}
              dir="ltr"
              inputMode="numeric"
              hint="برای نمایش اختلاف پیشنهاد با وضعیت فعلی."
            />
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button
              size="lg"
              onClick={() => void onEvaluate()}
              disabled={busy || valid.length === 0}
            >
              {busy ? 'در حال محاسبه…' : 'محاسبهٔ امتیاز و پیشنهاد'}
            </Button>
            <span className="text-xs text-ink-muted">
              مدل: <bdi dir="ltr">{rules?.ruleSetVersion ?? 'perf-v1'}</bdi> · وزن‌ها پیش‌نویس و
              تأییدنشده‌اند.
            </span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>سابقهٔ ارزیابی و تصمیم</CardTitle>
          <CardDescription>هر ارزیابی و تصمیم ثبت‌شده، ماندگار و قابل ردیابی است.</CardDescription>
        </CardHeader>
        <CardContent>
          {history.length === 0 ? (
            <EmptyState
              title="هنوز پیشنهادی ساخته نشده"
              description="پس از ثبت مشاهدات، دکمهٔ «محاسبهٔ امتیاز و پیشنهاد» را بزنید."
            />
          ) : (
            <ul className="flex flex-col gap-2 text-sm">
              {history.map((item) => (
                <li key={item.id}>
                  <Link
                    to={`/prototype/recommendations/${item.id}`}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border-subtle bg-surface px-3 py-2.5 hover:border-brand/30"
                  >
                    <span className="flex flex-col gap-0.5">
                      <span className="font-medium text-ink">
                        امتیاز {faDigits(item.score100)} · {rialText(item.suggestedGrossRial)}
                      </span>
                      <span className="text-xs text-ink-muted">
                        دورهٔ {item.period || '—'} · {isoDateText(item.createdAt)}
                      </span>
                    </span>
                    {item.decisionAction === null ? (
                      <Badge tone="warning">در انتظار تصمیم</Badge>
                    ) : (
                      <Badge tone={DECISION_TONES[item.decisionAction]}>
                        {DECISION_LABELS[item.decisionAction]}
                      </Badge>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </>
  );
}
