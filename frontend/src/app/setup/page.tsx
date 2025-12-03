'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { getErrorMessage } from '@/lib/errors';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { AlertCircle, CheckCircle, ShieldCheck, Globe } from 'lucide-react';

export default function SetupPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        try {
            await api.post('/auth/setup', { username, password });
            setSuccess(true);
            setTimeout(() => router.push('/login'), 2000);
        } catch (error: unknown) {
            setError(getErrorMessage(error));
        }
    };

    if (success) {
        return (
            <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 dark:bg-slate-900 p-4">
                <Card className="w-full max-w-sm shadow-lg border-green-200 bg-green-50">
                    <CardHeader className="text-center">
                        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                            <CheckCircle className="h-6 w-6 text-green-600" />
                        </div>
                        <CardTitle className="text-green-700">Setup Complete!</CardTitle>
                        <CardDescription className="text-green-600">Redirecting to login...</CardDescription>
                    </CardHeader>
                </Card>
            </div>
        )
    }

    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 dark:bg-slate-900 p-4">
            <div className="mb-8 flex items-center gap-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                    <Globe className="h-6 w-6" />
                </div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">IP-HOP Setup</h1>
            </div>

            <Card className="w-full max-w-md shadow-lg">
                <CardHeader>
                    <CardTitle>Create Admin Account</CardTitle>
                    <CardDescription>Configure your secure administrator access.</CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="rounded-md bg-blue-50 p-3 text-sm text-blue-700 flex gap-2">
                            <ShieldCheck className="h-5 w-5 shrink-0" />
                            <p>This will be the only account with access to manage your DDNS settings.</p>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="username">Username</Label>
                            <Input id="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                            <p className="text-xs text-muted-foreground">
                                Must contain 8+ chars, 1 uppercase, 1 special char, 2 numbers.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="confirmPassword">Confirm Password</Label>
                            <Input id="confirmPassword" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
                        </div>

                        {error && (
                            <div className="flex items-center gap-2 rounded-md bg-destructive/15 p-3 text-sm text-destructive">
                                <AlertCircle className="h-4 w-4" />
                                <p>{error}</p>
                            </div>
                        )}
                    </CardContent>
                    <CardFooter>
                        <Button type="submit" className="w-full">Create Account</Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
