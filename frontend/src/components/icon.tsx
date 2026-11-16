import { ICON_REGISTRY, RTL_MIRROR_CLASS, type IconName } from '@/lib/icons';
import { cn } from '@/lib/cn';

type IconProps = {
  name: IconName;
  className?: string;
  /** Persian accessible name. Omit when adjacent text already names the control. */
  label?: string;
};

/**
 * The single icon primitive. Mirroring is derived from the registry, so a
 * directional glyph can never be shipped unmirrored by omission.
 */
export function Icon({ name, className, label }: IconProps) {
  const definition = ICON_REGISTRY[name];
  const decorative = label === undefined;

  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.6}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={decorative ? true : undefined}
      role={decorative ? undefined : 'img'}
      aria-label={label}
      focusable="false"
      className={cn(
        'size-5 shrink-0',
        definition.directional && RTL_MIRROR_CLASS,
        className,
      )}
    >
      <path d={definition.path} />
    </svg>
  );
}
