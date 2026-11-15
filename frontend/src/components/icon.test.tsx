import { describe, expect, it } from 'vitest';
import { render } from '@testing-library/react';
import { Icon } from './icon';
import { ICON_REGISTRY, MIRRORED_ICONS, RTL_MIRROR_CLASS, type IconName } from '@/lib/icons';

const names = Object.keys(ICON_REGISTRY) as IconName[];

describe('the icon registry', () => {
  it('gives every icon a Persian label and a path', () => {
    for (const name of names) {
      expect(ICON_REGISTRY[name].labelFa.length).toBeGreaterThan(0);
      expect(ICON_REGISTRY[name].path.length).toBeGreaterThan(0);
    }
  });

  it('records directionality for every icon rather than leaving it implicit', () => {
    for (const name of names) {
      expect(typeof ICON_REGISTRY[name].directional).toBe('boolean');
    }
  });

  it('mirrors the directional glyphs and only those', () => {
    expect(MIRRORED_ICONS).toEqual(
      expect.arrayContaining(['chevron-next', 'chevron-previous', 'arrow-back']),
    );
    expect(MIRRORED_ICONS).not.toContain('audit');
    expect(MIRRORED_ICONS).not.toContain('documents');
  });
});

describe('Icon', () => {
  it('applies the RTL mirror class to a directional glyph', () => {
    const { container } = render(<Icon name="chevron-previous" />);
    expect(container.querySelector('svg')?.getAttribute('class')).toContain(RTL_MIRROR_CLASS);
  });

  it('does not mirror a non-directional glyph', () => {
    const { container } = render(<Icon name="lock" />);
    expect(container.querySelector('svg')?.getAttribute('class')).not.toContain(RTL_MIRROR_CLASS);
  });

  it('is hidden from assistive technology unless labelled', () => {
    const { container, rerender } = render(<Icon name="info" />);
    expect(container.querySelector('svg')?.getAttribute('aria-hidden')).toBe('true');

    rerender(<Icon name="info" label="اطلاعات" />);
    expect(container.querySelector('svg')?.getAttribute('aria-label')).toBe('اطلاعات');
  });
});
