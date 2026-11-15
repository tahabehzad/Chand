import { LoadingSkeleton } from '@/components/ui/states';

/** A content-shaped placeholder, announced politely, so the layout does not jump. */
export function RouteFallback() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="h-8 w-64 animate-pulse rounded bg-surface motion-reduce:animate-none" />
      <LoadingSkeleton rows={3} />
    </div>
  );
}
