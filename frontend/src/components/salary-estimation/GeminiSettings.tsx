/**
 * Gemini Settings Panel — Persian RTL.
 *
 * Allows managers to configure a Google Gemini API key for real-time web-grounded
 * salary estimation across Iranian job portals (Jobinja, Jobvision, IranTalent, Quera).
 *
 * Persists the key in localStorage under `pish_gemini_api_key`.
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  isValidGeminiKey,
  sanitizeGeminiKey,
  useGeminiApiKey,
} from '@/hooks/use-gemini-api-key';

export type ConnectionStatus = 'connected' | 'not_configured' | 'invalid';

export const GEMINI_KEY_FORMAT_ERROR =
  'فرمت کلید نامعتبر است. از AI Studio کلید AIza یا AQ را کپی کنید';

export async function testGeminiApiKey(key: string): Promise<{ ok: boolean; message: string }> {
  const cleaned = sanitizeGeminiKey(key);
  if (!cleaned) {
    return { ok: false, message: 'کلید دسترسی نمی‌تواند خالی باشد.' };
  }
  if (!isValidGeminiKey(cleaned)) {
    return { ok: false, message: GEMINI_KEY_FORMAT_ERROR };
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models?key=${encodeURIComponent(cleaned)}&pageSize=1`,
      { signal: controller.signal },
    );

    if (response.ok) {
      return { ok: true, message: 'اتصال به سرویس Gemini با موفقیت تأیید شد.' };
    }
    if (response.status === 400 || response.status === 401 || response.status === 403) {
      return { ok: false, message: 'کلید ارائه‌شده نامعتبر است یا مجوز کافی ندارد (کد ۴۰x).' };
    }
    return { ok: false, message: `پاسخ ناموفق از سرور گوگل (کد ${response.status}).` };
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return { ok: false, message: 'مهلت زمان ارتباط با سرور گوگل به پایان رسید.' };
    }
    return {
      ok: false,
      message: 'ارتباط با گوگل ناموفق (VPN/فیلترینگ)',
    };
  } finally {
    clearTimeout(timeout);
  }
}

export function GeminiSettings() {
  const { apiKey, setApiKey, isConfigured } = useGeminiApiKey();
  const [isOpen, setIsOpen] = useState(false);
  const [inputKey, setInputKey] = useState(apiKey ?? '');
  const [showPassword, setShowPassword] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testFeedback, setTestFeedback] = useState<{ ok: boolean; message: string } | null>(null);
  const [statusOverride, setStatusOverride] = useState<ConnectionStatus | null>(null);

  // Compute active status: empty=not_configured, regex fail=invalid, regex ok=connected
  let status: ConnectionStatus = 'not_configured';
  if (statusOverride) {
    status = statusOverride;
  } else if (isConfigured && apiKey) {
    status = isValidGeminiKey(apiKey) ? 'connected' : 'invalid';
  }

  const handleTestConnection = async () => {
    const candidate = sanitizeGeminiKey(inputKey);
    if (!candidate) {
      setTestFeedback({ ok: false, message: 'ابتدا کلید را وارد کنید.' });
      setStatusOverride('invalid');
      return;
    }

    if (!isValidGeminiKey(candidate)) {
      setTestFeedback({
        ok: false,
        message: GEMINI_KEY_FORMAT_ERROR,
      });
      setStatusOverride('invalid');
      return;
    }

    setIsTesting(true);
    setTestFeedback(null);
    try {
      const result = await testGeminiApiKey(candidate);
      setTestFeedback(result);
      if (result.ok) {
        setStatusOverride('connected');
        setApiKey(candidate);
      } else {
        setStatusOverride('invalid');
      }
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = () => {
    const candidate = sanitizeGeminiKey(inputKey);
    if (!candidate) {
      setApiKey(null);
      setStatusOverride('not_configured');
      setTestFeedback(null);
      return;
    }

    if (!isValidGeminiKey(candidate)) {
      setTestFeedback({
        ok: false,
        message: GEMINI_KEY_FORMAT_ERROR,
      });
      setStatusOverride('invalid');
      return;
    }

    setApiKey(candidate);
    setTestFeedback({ ok: true, message: 'کلید با موفقیت در مرورگر ذخیره شد.' });
    setStatusOverride('connected');
  };

  const handleClear = () => {
    setApiKey(null);
    setInputKey('');
    setStatusOverride('not_configured');
    setTestFeedback(null);
  };

  const isKeyFormatInvalid = inputKey.trim().length > 0 && !isValidGeminiKey(inputKey);

  return (
    <Card className='border border-border-subtle bg-surface transition-all duration-200'>
      <CardHeader className='p-4 sm:p-5'>
        <div className='flex flex-wrap items-center justify-between gap-3'>
          <div className='flex items-center gap-3'>
            <div className='flex size-8 items-center justify-center rounded-lg bg-surface-raised border border-border-subtle'>
              <span className='text-base' aria-hidden='true'>✨</span>
            </div>
            <div>
              <CardTitle className='text-base font-bold text-ink'>
                اتصال هوش مصنوعی و داده‌های زنده وب (Google Gemini)
              </CardTitle>
              <p className='text-xs text-ink-muted'>
                جستجوی زنده در پلتفرم‌های استخدامی جابینجا، جاب‌ویژن، ایران‌تلنت و کوئرا
              </p>
            </div>
          </div>

          <div className='flex items-center gap-2'>
            {status === 'connected' ? (
              <Badge tone='success' className='px-2.5 py-1 text-xs'>
                🟢 متصل (جستجوی زنده فعال)
              </Badge>
            ) : status === 'invalid' ? (
              <Badge tone='danger' className='px-2.5 py-1 text-xs'>
                🔴 کلید نامعتبر
              </Badge>
            ) : (
              <Badge tone='warning' className='px-2.5 py-1 text-xs'>
                🟡 تنظیم‌نشده (پایگاه داده پشتیبان)
              </Badge>
            )}

            <Button
              variant='secondary'
              size='sm'
              onClick={() => setIsOpen((prev) => !prev)}
              aria-expanded={isOpen}
            >
              {isOpen ? 'بستن تنظیمات' : 'تنظیم کلید API'}
            </Button>
          </div>
        </div>
      </CardHeader>

      {isOpen ? (
        <CardContent className='border-t border-border-subtle p-4 sm:p-5 space-y-4'>
          <div className='space-y-2'>
            <div className='relative'>
              <Input
                label='کلید دسترسی Google Gemini API'
                type={showPassword ? 'text' : 'password'}
                value={inputKey}
                onChange={(e) => {
                  setInputKey(e.target.value);
                  setTestFeedback(null);
                  setStatusOverride(null);
                }}
                placeholder='AIzaSy... یا AQ.Ab...'
                dir='ltr'
                className='pe-14'
                error={isKeyFormatInvalid ? GEMINI_KEY_FORMAT_ERROR : undefined}
                hint='کلید در مرورگر شما (localStorage) ذخیره می‌شود و مستقیماً برای جستجوی زنده وب ارسال می‌شود.'
              />
              <button
                type='button'
                onClick={() => setShowPassword((prev) => !prev)}
                className='absolute top-9 end-3 text-xs font-medium text-ink-muted hover:text-ink select-none'
                tabIndex={-1}
              >
                {showPassword ? 'مخفی' : 'نمایش'}
              </button>
            </div>
          </div>

          {testFeedback ? (
            <div
              className={`rounded-xl border p-3 text-xs font-medium ${
                testFeedback.ok
                  ? 'border-success/40 bg-success/10 text-success'
                  : 'border-danger/40 bg-danger/10 text-danger'
              }`}
              role='status'
            >
              {testFeedback.message}
            </div>
          ) : null}

          <div className='flex flex-wrap items-center justify-between gap-3 pt-2'>
            <div className='flex flex-wrap items-center gap-2'>
              <Button
                variant='secondary'
                size='sm'
                onClick={() => void handleTestConnection()}
                disabled={isTesting || !inputKey.trim()}
              >
                {isTesting ? 'در حال بررسی اتصال…' : 'تست اتصال'}
              </Button>
              <Button
                variant='primary'
                size='sm'
                onClick={handleSave}
                disabled={isTesting}
              >
                ذخیره کلید
              </Button>
            </div>

            {isConfigured ? (
              <Button
                variant='ghost'
                size='sm'
                onClick={handleClear}
                className='text-danger hover:text-danger hover:bg-danger/10'
              >
                حذف کلید ذخیره‌شده
              </Button>
            ) : null}
          </div>

          <div className='rounded-lg bg-surface-raised p-3 text-xs text-ink-muted'>
            <p className='font-semibold text-ink'>راهنمای اتصال:</p>
            <p className='mt-1'>
              برای دریافت کلید رایگان می‌توانید به Google AI Studio مراجعه کنید. در صورت عدم تنظیم کلید،
              محاسبات بر اساس نمونه‌های تأییدشدهٔ پایگاه دادهٔ پشتیبان انجام خواهد شد.
            </p>
          </div>
        </CardContent>
      ) : null}
    </Card>
  );
}
