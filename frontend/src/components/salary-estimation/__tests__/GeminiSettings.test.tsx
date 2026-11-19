import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GEMINI_API_KEY_STORAGE_KEY } from '@/hooks/use-gemini-api-key';
import { GEMINI_KEY_FORMAT_ERROR, GeminiSettings, testGeminiApiKey } from '../GeminiSettings';

const VALID_AIZA_KEY = 'AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7';
const VALID_AQ_KEY = 'AQ.AbCdEf12345678_.-TestKey';

describe('GeminiSettings Component', () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    window.localStorage.clear();
  });

  it('renders collapsed with not_configured badge when no key stored', () => {
    render(<GeminiSettings />);
    expect(
      screen.getByText('اتصال هوش مصنوعی و داده‌های زنده وب (Google Gemini)'),
    ).toBeInTheDocument();
    expect(screen.getByText('🟡 تنظیم‌نشده (پایگاه داده پشتیبان)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'تنظیم کلید API' })).toBeInTheDocument();
    expect(screen.queryByLabelText('کلید دسترسی Google Gemini API')).not.toBeInTheDocument();
  });

  it('renders connected badge when valid AIza key is already stored in localStorage', () => {
    window.localStorage.setItem(GEMINI_API_KEY_STORAGE_KEY, VALID_AIZA_KEY);
    render(<GeminiSettings />);
    expect(screen.getByText('🟢 متصل (جستجوی زنده فعال)')).toBeInTheDocument();
  });

  it('renders connected badge when valid AQ key is already stored in localStorage', () => {
    window.localStorage.setItem(GEMINI_API_KEY_STORAGE_KEY, VALID_AQ_KEY);
    render(<GeminiSettings />);
    expect(screen.getByText('🟢 متصل (جستجوی زنده فعال)')).toBeInTheDocument();
  });

  it('validates key format (rejects non-AIza/non-AQ with error text)', async () => {
    const user = userEvent.setup();
    render(<GeminiSettings />);

    await user.click(screen.getByRole('button', { name: 'تنظیم کلید API' }));
    const input = screen.getByLabelText('کلید دسترسی Google Gemini API');

    await user.type(input, 'invalidPrefixKey');
    expect(screen.getByText(GEMINI_KEY_FORMAT_ERROR)).toBeInTheDocument();
  });

  it('does NOT save invalid key to localStorage on handleSave and sets status to invalid', async () => {
    const user = userEvent.setup();
    render(<GeminiSettings />);

    await user.click(screen.getByRole('button', { name: 'تنظیم کلید API' }));
    const input = screen.getByLabelText('کلید دسترسی Google Gemini API');
    await user.type(input, 'invalidPrefixKey');

    const saveBtn = screen.getByRole('button', { name: 'ذخیره کلید' });
    await user.click(saveBtn);

    expect(window.localStorage.getItem(GEMINI_API_KEY_STORAGE_KEY)).toBeNull();
    expect(screen.getByText('🔴 کلید نامعتبر')).toBeInTheDocument();
  });

  it('saves valid AQ key to localStorage on handleSave', async () => {
    const user = userEvent.setup();
    render(<GeminiSettings />);

    await user.click(screen.getByRole('button', { name: 'تنظیم کلید API' }));
    const input = screen.getByLabelText('کلید دسترسی Google Gemini API');
    await user.type(input, VALID_AQ_KEY);

    const saveBtn = screen.getByRole('button', { name: 'ذخیره کلید' });
    await user.click(saveBtn);

    expect(window.localStorage.getItem(GEMINI_API_KEY_STORAGE_KEY)).toBe(VALID_AQ_KEY);
    expect(screen.getByText('🟢 متصل (جستجوی زنده فعال)')).toBeInTheDocument();
  });

  it('toggles password visibility between password and text types', async () => {
    const user = userEvent.setup();
    render(<GeminiSettings />);

    await user.click(screen.getByRole('button', { name: 'تنظیم کلید API' }));
    const input = screen.getByLabelText('کلید دسترسی Google Gemini API');
    expect(input).toHaveAttribute('type', 'password');

    const toggleShowBtn = screen.getByText('نمایش');
    await user.click(toggleShowBtn);
    expect(input).toHaveAttribute('type', 'text');

    const toggleHideBtn = screen.getByText('مخفی');
    await user.click(toggleHideBtn);
    expect(input).toHaveAttribute('type', 'password');
  });

  it('tests connection with native endpoint, saves key on success, and supports clearing', async () => {
    const user = userEvent.setup();
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ models: [{ name: 'models/gemini-2.0-flash' }] }),
    } as Response);

    render(<GeminiSettings />);
    await user.click(screen.getByRole('button', { name: 'تنظیم کلید API' }));

    const input = screen.getByLabelText('کلید دسترسی Google Gemini API');
    await user.type(input, VALID_AQ_KEY);

    const testBtn = screen.getByRole('button', { name: 'تست اتصال' });
    await user.click(testBtn);

    expect(fetchSpy).toHaveBeenCalledWith(
      `https://generativelanguage.googleapis.com/v1beta/models?key=${encodeURIComponent(VALID_AQ_KEY)}&pageSize=1`,
      expect.anything(),
    );
    expect(screen.getByText('اتصال به سرویس Gemini با موفقیت تأیید شد.')).toBeInTheDocument();
    expect(screen.getByText('🟢 متصل (جستجوی زنده فعال)')).toBeInTheDocument();
    expect(window.localStorage.getItem(GEMINI_API_KEY_STORAGE_KEY)).toBe(VALID_AQ_KEY);

    // Test clear key
    const clearBtn = screen.getByRole('button', { name: 'حذف کلید ذخیره‌شده' });
    await user.click(clearBtn);

    expect(window.localStorage.getItem(GEMINI_API_KEY_STORAGE_KEY)).toBeNull();
    expect(screen.getByText('🟡 تنظیم‌نشده (پایگاه داده پشتیبان)')).toBeInTheDocument();
  });

  it('returns network error message when fetch fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'));
    const result = await testGeminiApiKey(VALID_AQ_KEY);
    expect(result.ok).toBe(false);
    expect(result.message).toBe('ارتباط با گوگل ناموفق (VPN/فیلترینگ)');
  });
});
