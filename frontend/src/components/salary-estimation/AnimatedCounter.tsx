/**
 * Animated counter for primary salary estimate — Persian RTL.
 *
 * Counts up smoothly from 0 to the target Rial figure over 1.2 seconds using
 * requestAnimationFrame (60fps) with an ease-out curve.
 *
 * Invariant: Every intermediate value is snapped to an exact multiple of 10 Rial
 * so that `formatMoneyPreferringToman()` never rejects Toman conversion during
 * the animation. The final figure is unconditionally formatted through
 * `formatMoneyPreferringToman()` for canonical accuracy.
 */

import { useEffect, useState } from 'react';
import { formatMoneyPreferringToman } from '@/lib/money';

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}

function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return false;
  }
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export type AnimatedCounterProps = {
  targetRial: number;
  className?: string;
  durationMs?: number;
};

export function AnimatedCounter({
  targetRial,
  className,
  durationMs = 1200,
}: AnimatedCounterProps) {
  const finalFormatted = formatMoneyPreferringToman(targetRial).text;

  const [displayText, setDisplayText] = useState<string>(() => {
    // If reduced motion is requested, duration is 0, or in SSR/test, display final immediately.
    if (durationMs <= 0 || prefersReducedMotion()) return finalFormatted;
    // Initial frame starts at 0 Toman
    return formatMoneyPreferringToman(0).text;
  });

  useEffect(() => {
    if (durationMs <= 0 || prefersReducedMotion()) {
      setDisplayText(finalFormatted);
      return;
    }

    let animationFrameId: number;
    const startTime = performance.now();

    const step = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(1, elapsed / durationMs);
      const easedProgress = easeOutCubic(progress);

      if (progress < 1) {
        // Round to multiple of 10 Rial so Toman conversion is always exact
        const intermediateRial = Math.round((targetRial * easedProgress) / 10) * 10;
        setDisplayText(formatMoneyPreferringToman(intermediateRial).text);
        animationFrameId = requestAnimationFrame(step);
      } else {
        // Animation finished: guarantee final canonical string
        setDisplayText(finalFormatted);
      }
    };

    animationFrameId = requestAnimationFrame(step);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [targetRial, durationMs, finalFormatted]);

  return (
    <span className={className} data-machine-value={targetRial}>
      {displayText}
    </span>
  );
}
