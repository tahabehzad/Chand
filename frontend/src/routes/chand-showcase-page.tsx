import { useEffect } from 'react';

export default function ChandShowcasePage() {
  useEffect(() => {
    document.title = 'چند؟ | سامانه هوشمند برآورد حقوق و جبران خدمات سازمانی';
  }, []);

  return (
    <div className="fixed inset-0 z-50 h-dvh w-screen overflow-hidden bg-[#060608]">
      <iframe
        src="/chand.html"
        title="چند؟ | سامانه هوشمند برآورد حقوق"
        className="h-full w-full border-0"
        allow="autoplay"
      />
    </div>
  );
}
