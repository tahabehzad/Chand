import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import type { ComponentProps } from 'react';
import { cn } from '@/lib/cn';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-xs hover:shadow-md disabled:pointer-events-none disabled:opacity-60 disabled:hover:scale-100 disabled:hover:shadow-none focus-visible:outline-2 focus-visible:outline-offset-2',
  {
    variants: {
      variant: {
        primary: 'bg-brand text-white hover:bg-brand-strong',
        secondary: 'border border-border-subtle bg-surface-raised text-ink hover:bg-surface',
        ghost: 'text-ink-muted hover:bg-surface hover:text-ink',
        danger: 'bg-danger text-white hover:opacity-90',
        gradient: 'btn-gradient text-white shadow-sm hover:shadow-md',
      },
      size: {
        sm: 'min-h-9 px-3',
        md: 'min-h-11 px-4',
        lg: 'min-h-12 px-6 text-base',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  },
);

export type ButtonProps = ComponentProps<'button'> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  };

export function Button({
  className,
  variant,
  size,
  asChild = false,
  type = 'button',
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : 'button';
  return (
    <Component
      className={cn(buttonVariants({ variant, size }), className)}
      {...(asChild ? {} : { type })}
      {...props}
    />
  );
}

export { buttonVariants };
