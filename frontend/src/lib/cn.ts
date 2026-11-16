import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Shadcn/UI convention: merge conditional classes with Tailwind conflicts resolved. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
