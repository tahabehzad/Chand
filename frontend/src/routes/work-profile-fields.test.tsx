import { useState } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkProfileFields } from './work-profile-fields';
import { EMPTY_WORK_PROFILE, getWorkProfile, saveWorkProfile, getWorkDocuments, getLatestWorkResult, uploadWorkDocument } from './work-profile-api';

vi.mock('@/prototype/api', () => ({
  listPeople: vi.fn(async () => [{ id: 'employee-a', name: 'Demo', role: 'Analyst', startDate: '2025-01-01', createdAt: '' }]),
  createPerson: vi.fn(),
}));
vi.mock('./work-profile-api', async (original) => {
  const actual = await original<typeof import('./work-profile-api')>();
  return { ...actual, getWorkProfile: vi.fn(), saveWorkProfile: vi.fn(), getWorkDocuments: vi.fn(), getLatestWorkResult: vi.fn(), uploadWorkDocument: vi.fn(), downloadWorkDocument: vi.fn() };
});
const dirty = vi.fn();
const restored = vi.fn();
function Harness() {
  const [selected, setSelected] = useState('employee-a');
  return <WorkProfileFields employeeId={selected} onSelect={setSelected} onDirtyChange={dirty} onRestored={restored} />;
}
beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(getWorkProfile).mockResolvedValue({ profile: { ...EMPTY_WORK_PROFILE, daily_hours: '4.4', weekly_days: 5, recognised_seniority_months: 12 }, revision: 1 });
  vi.mocked(getWorkDocuments).mockResolvedValue([]);
  vi.mocked(getLatestWorkResult).mockResolvedValue(null);
});
afterEach(cleanup);

describe('Persisted work profile editor', () => {
  it('saves the revision-bound draft and restores values from the server on remount', async () => {
    const user = userEvent.setup();
    const first = render(<Harness />);
    const hours = await screen.findByLabelText('ساعات عادی کار در روز');
    await waitFor(() => expect(hours).toHaveValue('4.4'));
    await user.clear(hours); await user.type(hours, '4');
    vi.mocked(saveWorkProfile).mockImplementation(async (_id, profile) => ({ profile, revision: 2 }));
    await user.click(screen.getByRole('button', { name: 'ذخیره شرایط همکاری' }));
    await waitFor(() => expect(saveWorkProfile).toHaveBeenCalledWith('employee-a', expect.objectContaining({ daily_hours: '4' }), 1));
    await screen.findByText('ذخیره‌شده در پرونده');
    vi.mocked(getWorkProfile).mockResolvedValue({ profile: { ...EMPTY_WORK_PROFILE, daily_hours: '4' }, revision: 2 });
    first.unmount(); render(<Harness />);
    await waitFor(() => expect(screen.getByLabelText('ساعات عادی کار در روز')).toHaveValue('4'));
  });

  it('uploads actual bytes and shows only the server-confirmed document', async () => {
    const user = userEvent.setup(); render(<Harness />);
    await waitFor(() => expect(screen.getByLabelText('آپلود مدارک')).toBeEnabled());
    const file = new File(['%PDF-1.4\nsynthetic'], 'demo.pdf', { type: 'application/pdf' });
    vi.mocked(uploadWorkDocument).mockResolvedValue({ id: 'doc-a', fileName: 'demo.pdf', contentType: 'application/pdf', byteSize: file.size, sha256: 'a'.repeat(64) });
    await user.upload(screen.getByLabelText('آپلود مدارک'), file);
    await waitFor(() => expect(uploadWorkDocument).toHaveBeenCalledWith('employee-a', file));
    expect(await screen.findByText('demo.pdf')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'دریافت' })).toBeInTheDocument();
  });

  it('keeps unsaved state and shows a revision failure instead of false success', async () => {
    const user = userEvent.setup(); render(<Harness />);
    await waitFor(() => expect(screen.getByLabelText('ساعات عادی کار در روز')).toHaveValue('4.4'));
    await user.type(screen.getByLabelText('رشته تحصیلی'), 'Demo');
    vi.mocked(saveWorkProfile).mockRejectedValue(new Error('پرونده در زبانه دیگری تغییر کرده است.'));
    await user.click(screen.getByRole('button', { name: 'ذخیره شرایط همکاری' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('پرونده در زبانه دیگری');
    expect(screen.getByText('تغییرات ذخیره نشده')).toBeInTheDocument();
  });
});
