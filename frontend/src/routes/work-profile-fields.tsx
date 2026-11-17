import { useEffect, useId, useState, type FormEvent } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { listPeople, createPerson } from '@/prototype/api';
import type { Person } from '@/prototype/types';
import { normaliseNumericInput } from '@/lib/numerals';
import { EMPTY_WORK_PROFILE, getWorkProfile, saveWorkProfile, getWorkDocuments, getLatestWorkResult, uploadWorkDocument, downloadWorkDocument, type WorkProfile, type WorkDocument, type WorkResult } from './work-profile-api';

type Props = { employeeId: string; onSelect: (id: string) => void; onDirtyChange: (value: boolean) => void; onRestored: (result: WorkResult | null) => void; locked?: boolean };

/** Employee-bound persistence; the browser never adjusts salary figures. */
export function WorkProfileFields({ employeeId, onSelect, onDirtyChange, onRestored, locked = false }: Props) {
  const id = useId();
  const [people, setPeople] = useState<Person[]>([]);
  const [draft, setDraft] = useState<WorkProfile>({ ...EMPTY_WORK_PROFILE });
  const [revision, setRevision] = useState(0);
  const [documents, setDocuments] = useState<WorkDocument[]>([]);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState('');
  const [newDate, setNewDate] = useState('');
  const cls = 'min-h-11 w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink';

  useEffect(() => {
    let active = true;
    void listPeople().then((rows) => { if (active) setPeople(rows); }).catch(() => { if (active) setError('دریافت فهرست پرونده‌ها ناموفق بود.'); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    let active = true;
    setError(null); setDocuments([]); setRevision(0); setDraft({ ...EMPTY_WORK_PROFILE });
    setDirty(false); onDirtyChange(false); onRestored(null);
    if (!employeeId) return () => { active = false; };
    setLoading(true);
    void Promise.all([getWorkProfile(employeeId), getWorkDocuments(employeeId), getLatestWorkResult(employeeId)])
      .then(([saved, files, result]) => {
        if (!active) return;
        setDraft(saved?.profile ?? { ...EMPTY_WORK_PROFILE }); setRevision(saved?.revision ?? 0);
        setDocuments(files); setLoading(false);
        onRestored(result?.profile_revision === saved?.revision ? result : null);
      }).catch((caught: unknown) => { if (active) { setLoading(false); setError(caught instanceof Error ? caught.message : 'دریافت پرونده ناموفق بود.'); } });
    return () => { active = false; };
  }, [employeeId, onDirtyChange, onRestored]);
  function change<K extends keyof WorkProfile>(key: K, value: WorkProfile[K]): void {
    setDraft((previous) => ({ ...previous, [key]: value })); setDirty(true); onDirtyChange(true); onRestored(null);
  }
  function numeric(key: keyof WorkProfile, label: string, max = 1200) {
    return <Input key={key} label={label} type="number" min={0} max={max} step={1} inputMode="numeric" dir="ltr" value={draft[key] === null ? '' : String(draft[key])} onChange={(event) => change(key, event.target.value === '' ? null : Number(event.target.value))} />;
  }
  async function save(event: FormEvent): Promise<void> {
    event.preventDefault(); setBusy(true); setError(null);
    try { const saved = await saveWorkProfile(employeeId, draft, revision); setDraft(saved.profile); setRevision(saved.revision); setDirty(false); onDirtyChange(false); }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'ذخیره ناموفق بود.'); }
    finally { setBusy(false); }
  }
  async function upload(files: FileList | null): Promise<void> {
    const selected = Array.from(files ?? []);
    if (selected.length > 5 || selected.some((file) => file.size > 5_000_000)) { setError('حداکثر پنج فایل، هر فایل تا پنج مگابایت.'); return; }
    setBusy(true); setError(null);
    try { for (const file of selected) { const stored = await uploadWorkDocument(employeeId, file); setDocuments((previous) => [...previous, stored]); } }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'آپلود ناموفق بود.'); }
    finally { setBusy(false); }
  }
  async function create(event: FormEvent): Promise<void> {
    event.preventDefault(); setBusy(true); setError(null);
    try { const person = await createPerson({ name: newName, role: newRole, startDate: newDate }); setPeople((previous) => [...previous, person]); onSelect(person.id); setCreating(false); }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'ساخت پرونده ناموفق بود.'); }
    finally { setBusy(false); }
  }
  return <Card>
    <CardHeader className="flex-row flex-wrap items-center justify-between gap-2"><CardTitle>شرایط همکاری</CardTitle><span role="status" className="text-xs text-ink-muted">{loading ? 'دریافت اطلاعات…' : dirty ? 'تغییرات ذخیره نشده' : revision > 0 ? 'ذخیره‌شده در پرونده' : 'انتخاب پرونده'}</span></CardHeader>
    <CardContent className="space-y-5">
      <div className="flex flex-wrap items-end gap-3"><div className="flex min-w-48 flex-1 flex-col gap-2"><label htmlFor={`${id}-employee`} className="text-sm font-medium text-ink">پرونده کارمند</label><select id={`${id}-employee`} className={cls} value={employeeId} disabled={busy || locked} onChange={(event) => onSelect(event.target.value)}><option value="">انتخاب کنید</option>{people.map((person) => <option key={person.id} value={person.id}>{person.name} — {person.role}</option>)}</select></div><Button variant="secondary" disabled={busy || locked} onClick={() => setCreating(!creating)}>پرونده جدید</Button></div>
      {creating && <form onSubmit={(event) => void create(event)} className="grid gap-3 rounded-xl border border-border-subtle p-4 sm:grid-cols-2"><Input label="نام نمایشی پرونده" value={newName} onChange={(event) => setNewName(event.target.value)} required maxLength={120} /><Input label="عنوان شغل پرونده" value={newRole} onChange={(event) => setNewRole(event.target.value)} required maxLength={60} /><Input label="شروع همکاری (میلادی)" type="date" value={newDate} onChange={(event) => setNewDate(event.target.value)} required /><Button type="submit" disabled={busy || locked}>ساخت پرونده</Button></form>}
      {error && <p role="alert" className="rounded-lg bg-danger/10 p-3 text-sm text-danger">{error}</p>}
      {employeeId && <form onSubmit={(event) => void save(event)}><fieldset disabled={busy || loading || locked} className="min-w-0 space-y-6 disabled:opacity-60">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Input label="عنوان شغلی" value={draft.job_title} onChange={(event) => change('job_title', event.target.value)} maxLength={120} />
          <div className="flex flex-col gap-2"><label htmlFor={`${id}-education`} className="text-sm font-medium text-ink">مدرک تحصیلی</label><select id={`${id}-education`} className={cls} value={draft.education} onChange={(event) => change('education', event.target.value)}><option value="">انتخاب کنید</option>{[['diploma','دیپلم'],['associate','کاردانی'],['bachelor','کارشناسی'],['master','کارشناسی ارشد'],['doctorate','دکتری']].map(([value,label]) => <option key={value} value={value}>{label}</option>)}</select></div>
          <Input label="رشته تحصیلی" value={draft.education_subject} onChange={(event) => change('education_subject', event.target.value)} maxLength={120} />
          {numeric('total_experience_months', 'کل سابقه حرفه‌ای (ماه)')}{numeric('relevant_experience_months', 'سابقه مرتبط با این شغل (ماه)')}{numeric('insurance_months', 'سابقه پرداخت حق بیمه (ماه)')}{numeric('employer_tenure_months', 'سابقه نزد کارفرمای فعلی (ماه)')}{numeric('recognised_seniority_months', 'سابقه مشمول پایه سنوات (ماه)')}
          <div className="flex flex-col gap-2"><label htmlFor={`${id}-workshop`} className="text-sm font-medium text-ink">طرح طبقه‌بندی مشاغل</label><select id={`${id}-workshop`} className={cls} value={draft.workshop_type} onChange={(event) => change('workshop_type', event.target.value as WorkProfile['workshop_type'])}><option value="unclassified">فاقد طرح</option><option value="classified">دارای طرح</option></select></div>
          {numeric('documented_daily_seniority_rial', 'پایه سنوات روزانه طبق حکم (ریال)', 10_000_000_000)}
        </div>
        <div className="grid gap-4 border-t border-border-subtle pt-5 sm:grid-cols-3">
          <Input label="ساعات عادی کار در روز" value={draft.daily_hours ?? ''} inputMode="decimal" dir="ltr" onChange={(event) => change('daily_hours', event.target.value === '' ? null : normaliseNumericInput(event.target.value))} />
          <div className="flex flex-col gap-2"><label htmlFor={`${id}-schedule`} className="text-sm font-medium text-ink">دوره برنامه کاری</label><select id={`${id}-schedule`} className={cls} value={draft.schedule_period} onChange={(event) => { const period = event.target.value as WorkProfile['schedule_period']; setDraft((previous) => ({ ...previous, schedule_period: period, weekly_days: null, monthly_paid_days: null })); setDirty(true); onDirtyChange(true); onRestored(null); }}><option value="weekly">هفتگی</option><option value="monthly">ماهانه</option></select></div>
          {draft.schedule_period === 'weekly' ? numeric('weekly_days', 'روزهای کار در هفته', 7) : numeric('monthly_paid_days', 'روزهای مشمول پرداخت با تعطیلات (ماه)', 31)}
        </div>
        <div className="flex flex-col gap-2"><label htmlFor={`${id}-qualifications`} className="text-sm font-medium text-ink">مهارت‌ها و توضیحات مدارک</label><textarea id={`${id}-qualifications`} className={cls} rows={3} maxLength={4000} value={draft.qualifications} onChange={(event) => change('qualifications', event.target.value)} /></div>
        <Button type="submit" disabled={!dirty || busy || loading || locked}>{busy ? 'در حال ذخیره…' : 'ذخیره شرایط همکاری'}</Button>
      </fieldset></form>}
      {employeeId && <div className="space-y-3 border-t border-border-subtle pt-4"><label htmlFor={`${id}-files`} className="block text-sm font-medium text-ink">آپلود مدارک</label><input id={`${id}-files`} disabled={busy || loading || locked} type="file" multiple accept="application/pdf,image/jpeg,image/png" onChange={(event) => { void upload(event.target.files); event.target.value = ''; }} className="block w-full min-w-0 text-sm text-ink-muted file:me-3 file:rounded-lg file:border-0 file:bg-brand/10 file:px-3 file:py-2 file:text-brand" /><p className="text-xs text-ink-muted">PDF، JPG و PNG · هر فایل تا پنج مگابایت</p><ul className="space-y-2" aria-label="مدارک ذخیره‌شده">{documents.map((document) => <li key={document.id} className="flex min-w-0 items-center justify-between gap-3 rounded-lg border border-border-subtle px-3 py-2 text-sm"><bdi className="truncate">{document.fileName}</bdi><Button variant="ghost" size="sm" onClick={() => { void downloadWorkDocument(employeeId, document).catch(() => setError('دریافت مدرک ناموفق بود.')); }}>دریافت</Button></li>)}</ul></div>}
    </CardContent>
  </Card>;
}
