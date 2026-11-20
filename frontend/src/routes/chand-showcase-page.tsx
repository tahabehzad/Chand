import { useEffect } from 'react';

export default function ChandShowcasePage() {
  useEffect(() => {
    document.title = 'چند؟ | سامانه هوشمند برآورد حقوق و جبران خدمات سازمانی';
    // ریدایرکت مستقیم به سند مستقل چند برای حذف سربار آیفریم و اجرای بومی و روان در مرورگر
    window.location.replace('/chand.html');
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#060608] text-gold-300 font-sans">
      <div className="flex items-center gap-3">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-gold-400 border-t-transparent" />
        <span className="text-sm font-bold">در حال انتقال به سامانه چند؟...</span>
      </div>
    </div>
  );
}
