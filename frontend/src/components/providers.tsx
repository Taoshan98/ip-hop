'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthContext';
import { ConfirmDialogProvider } from '@/components/confirm-dialog';
import { ThemeProvider } from 'next-themes';
import { Toaster } from 'sonner';
import { useState } from 'react';

export default function Providers({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(() => new QueryClient());

    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider
                attribute="class"
                defaultTheme="system"
                enableSystem
                disableTransitionOnChange={false}
            >
                <AuthProvider>
                    <ConfirmDialogProvider>
                        <Toaster position="top-right" richColors />
                        {children}
                    </ConfirmDialogProvider>
                </AuthProvider>
            </ThemeProvider>
        </QueryClientProvider>
    );
}
