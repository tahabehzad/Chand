import { create } from 'zustand';
import { Icon } from '@/components/icon';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/cn';

type ToastType = 'info' | 'success' | 'warning' | 'danger';

type Toast = {
  id: string;
  type: ToastType;
  title: string;
  description?: string;
  duration?: number;
  action?: { label: string; onClick: () => void };
};

type ToastState = {
  toasts: Toast[];
  add: (toast: Omit<Toast, 'id'>) => void;
  remove: (id: string) => void;
};

const TYPE_STYLES: Record<ToastType, string> = {
  info: 'border-brand/30 bg-brand/5 text-ink',
  success: 'border-success/40 bg-success/10 text-ink',
  warning: 'border-warning/40 bg-warning/10 text-ink',
  danger: 'border-danger/40 bg-danger/10 text-ink',
};

const TYPE_ICONS: Record<ToastType, 'info' | 'check' | 'alert'> = {
  info: 'info',
  success: 'check',
  warning: 'alert',
  danger: 'alert',
};

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  add: (toast) => {
    const id = Math.random().toString(36).slice(2);
    set((state) => ({ toasts: [...state.toasts, { ...toast, id }] }));
    if (toast.duration !== 0) {
      setTimeout(() => {
        set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
      }, toast.duration ?? 5000);
    }
  },
  remove: (id) => {
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
  },
}));

export function useToast() {
  const { add, remove } = useToastStore();
  return {
    toast: (toast: Omit<Toast, 'id'>) => add(toast),
    dismiss: (id: string) => remove(id),
  };
}

export function Toast({ toast, onDismiss }: { toast: Toast; onDismiss: (id: string) => void }) {
  const styles = TYPE_STYLES[toast.type];
  const IconName = TYPE_ICONS[toast.type];

  return (
    <div
      key={toast.id}
      className={cn(
        'flex items-start gap-3 rounded-lg border p-4 text-sm animate-in slide-in-from-right-2',
        styles,
      )}
    >
      <Icon name={IconName} className="mt-0.5 size-5 shrink-0" />
      <div className="flex flex-col gap-1 min-w-0">
        <p className="font-semibold text-ink">{toast.title}</p>
        {toast.description ? (
          <p className="text-xs text-ink-muted">{toast.description}</p>
        ) : null}
      </div>
      <div className="ms-auto flex flex-col gap-1">
        {toast.action ? (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              const action = toast.action;
              if (action) {
                action.onClick();
                onDismiss(toast.id);
              }
            }}
          >
            {toast.action.label}
          </Button>
        ) : null}
        <Button
          variant="ghost"
          size="sm"
          className="text-ink-muted hover:text-ink"
          onClick={() => onDismiss(toast.id)}
          aria-label="بستن اعلان"
        >
          <Icon name="close" className="size-4" />
        </Button>
      </div>
    </div>
  );
}

export function ToastContainer() {
  const toasts = useToastStore((state) => state.toasts);
  const remove = useToastStore((state) => state.remove);

  return (
    <div className="fixed top-4 start-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onDismiss={remove} />
      ))}
    </div>
  );
}
