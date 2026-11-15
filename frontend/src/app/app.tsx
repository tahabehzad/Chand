import { useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from 'react-router-dom';
import { createQueryClient } from '@/api/query-client';
import { RouteErrorBoundary } from './route-error';
import { router } from './router';

export function App() {
  const [queryClient] = useState(createQueryClient);

  return (
    <RouteErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </RouteErrorBoundary>
  );
}
