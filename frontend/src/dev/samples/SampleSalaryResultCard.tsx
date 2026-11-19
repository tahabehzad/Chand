import type { ReactNode } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function SalaryResultCard({
  title,
  subtitle,
  stats,
  onClick,
  selected = false,
}: {
  title: string;
  subtitle: string;
  stats: {
    label: string;
    value: string;
    color?: string;
  }[];
  onClick?: () => void;
  selected?: boolean;
}): ReactNode {
  return (
    <Card
      className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${selected ? 'border-brand ring-2 ring-brand/30' : ''}`}
      onClick={onClick}
    >
      <CardHeader className='pb-3'>
        <CardTitle className='text-lg'>{title}</CardTitle>
        <p className='text-sm text-ink-muted'>{subtitle}</p>
      </CardHeader>

      <CardContent className='space-y-4'>
        {stats.map((stat, index) => (
          <div key={index} className='flex justify-between items-center'>
            <span className='text-sm text-ink-muted'>{stat.label}:</span>
            <span className={`font-medium tabular-nums ${stat.color || ''}`}>{stat.value}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
