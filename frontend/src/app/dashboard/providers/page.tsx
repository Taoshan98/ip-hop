'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { getErrorMessage } from '@/lib/errors';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Trash2, Plus, Pencil } from 'lucide-react';
import { useState } from 'react';
import { useConfirmDialog } from '@/components/confirm-dialog';
import { toast } from 'sonner';

interface Provider {
    id: number;
    name: string;
    type: string;
    is_enabled: boolean;
}

export default function ProvidersPage() {
    const queryClient = useQueryClient();
    const { confirm } = useConfirmDialog();
    const [isAdding, setIsAdding] = useState(false);
    const [editingProvider, setEditingProvider] = useState<Provider | null>(null);

    // Form State
    const [name, setName] = useState('');
    const [type, setType] = useState('dynu');
    const [token, setToken] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isEnabled, setIsEnabled] = useState(true);

    const { data: providers, isLoading } = useQuery<Provider[]>({
        queryKey: ['providers'],
        queryFn: async () => {
            const res = await api.get('/providers');
            return res.data;
        },
    });

    const createMutation = useMutation({
        mutationFn: async () => {
            // Build credentials based on provider type
            const credentials = type === 'noip'
                ? { username, password }
                : { token };

            await api.post('/providers', {
                name,
                type,
                is_enabled: isEnabled,
                credentials
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['providers'] });
            resetForm();
        },
        onError: (error: unknown) => {
            toast.error('Failed to create provider', {
                description: getErrorMessage(error)
            });
        }
    });

    const updateMutation = useMutation({
        mutationFn: async (id: number) => {
            const payload: Record<string, unknown> = {
                name,
                is_enabled: isEnabled,
            };
            // Build credentials based on provider type (for editing, we need to know the type)
            if (type === 'noip') {
                if (username || password) {
                    payload.credentials = { username, password };
                }
            } else {
                if (token) {
                    payload.credentials = { token };
                }
            }
            await api.put(`/providers/${id}`, payload);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['providers'] });
            resetForm();
        },
        onError: (error: unknown) => {
            toast.error('Failed to update provider', {
                description: getErrorMessage(error)
            });
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            await api.delete(`/providers/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['providers'] });
        },
        onError: (error: unknown) => {
            toast.error('Failed to delete provider', {
                description: getErrorMessage(error)
            });
        }
    });

    const resetForm = () => {
        setIsAdding(false);
        setEditingProvider(null);
        setName('');
        setType('dynu');
        setToken('');
        setUsername('');
        setPassword('');
        setIsEnabled(true);
    };

    const handleEdit = (provider: Provider) => {
        setEditingProvider(provider);
        setName(provider.name);
        setType(provider.type);
        setIsEnabled(provider.is_enabled);
        setToken(''); // Don't show existing credentials for security
        setUsername('');
        setPassword('');
        setIsAdding(true);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (editingProvider) {
            updateMutation.mutate(editingProvider.id);
        } else {
            createMutation.mutate();
        }
    };

    if (isLoading) return <div>Loading...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold tracking-tight">Providers</h2>
                {!isAdding && (
                    <Button onClick={() => { resetForm(); setIsAdding(true); }}>
                        <Plus className="w-4 h-4 mr-2" /> Add Provider
                    </Button>
                )}
            </div>

            {isAdding && (
                <Card className="mb-6 border-primary">
                    <CardHeader>
                        <CardTitle>{editingProvider ? 'Edit Provider' : 'Add New Provider'}</CardTitle>
                        <CardDescription>Configure DDNS provider settings.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Name</Label>
                                    <Input value={name} onChange={e => setName(e.target.value)} placeholder="My Provider" required />
                                </div>
                                <div className="space-y-2">
                                    <Label>Type</Label>
                                    <select
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                                        value={type}
                                        onChange={e => setType(e.target.value)}
                                        disabled={!!editingProvider} // Cannot change type after creation
                                    >
                                        <option value="dynu">Dynu</option>
                                        <option value="cloudflare">Cloudflare</option>
                                        <option value="duckdns">DuckDNS</option>
                                        <option value="noip">No-IP</option>
                                    </select>
                                </div>

                                {/* Conditional credentials fields based on provider type */}
                                {type === 'noip' ? (
                                    <>
                                        <div className="space-y-2">
                                            <Label>DDNS Key Username {editingProvider && '(Leave blank to keep unchanged)'}</Label>
                                            <Input
                                                type="text"
                                                value={username}
                                                onChange={e => setUsername(e.target.value)}
                                                placeholder="DDNS Key Username"
                                                required={!editingProvider}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>DDNS Key Password {editingProvider && '(Leave blank to keep unchanged)'}</Label>
                                            <Input
                                                type="password"
                                                value={password}
                                                onChange={e => setPassword(e.target.value)}
                                                placeholder="DDNS Key Password"
                                                required={!editingProvider}
                                            />
                                        </div>
                                        <div className="col-span-2 p-3 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 rounded-md text-sm">
                                            <p className="font-medium">No-IP Authentication</p>
                                            <p>Use your DDNS Key credentials (free). Generate them at noip.com → Dynamic DNS → DDNS Keys.</p>
                                        </div>
                                    </>
                                ) : (
                                    <div className="col-span-2 space-y-2">
                                        <Label>API Token {editingProvider && '(Leave blank to keep unchanged)'}</Label>
                                        <Input
                                            type="password"
                                            value={token}
                                            onChange={e => setToken(e.target.value)}
                                            placeholder="Secret Token"
                                            required={!editingProvider}
                                        />
                                    </div>
                                )}
                                <div className="col-span-2 flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        id="enabled"
                                        checked={isEnabled}
                                        onChange={e => setIsEnabled(e.target.checked)}
                                        className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                    />
                                    <Label htmlFor="enabled">Enabled</Label>
                                </div>
                            </div>
                            <div className="flex justify-end gap-2">
                                <Button type="button" variant="ghost" onClick={resetForm}>Cancel</Button>
                                <Button type="submit">{editingProvider ? 'Update' : 'Save'} Provider</Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {providers?.map((provider) => (
                    <Card key={provider.id}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                {provider.name}
                            </CardTitle>
                            <span className="text-xs font-bold px-2 py-1 bg-gray-300 text-gray-700 rounded uppercase">{provider.type}</span>
                        </CardHeader>
                        <CardContent>
                            <div className="text-sm text-muted-foreground mt-2">
                                Status: <span className={provider.is_enabled ? "text-green-600" : "text-red-600"}>{provider.is_enabled ? "Enabled" : "Disabled"}</span>
                            </div>
                            <div className="mt-4 flex justify-end gap-2">
                                <Button
                                    size="sm"
                                    onClick={() => handleEdit(provider)}
                                >
                                    <Pencil className="w-4 h-4 mr-2" /> Edit
                                </Button>
                                <Button
                                    variant="destructive"
                                    size="sm"
                                    onClick={() => {
                                        confirm({
                                            title: 'Delete Provider',
                                            description: `Are you sure you want to delete "${provider.name}"? This action cannot be undone.`,
                                            confirmText: 'Delete',
                                            cancelText: 'Cancel',
                                            variant: 'destructive',
                                            onConfirm: () => {
                                                deleteMutation.mutate(provider.id);
                                            }
                                        });
                                    }}
                                >
                                    <Trash2 className="w-4 h-4 mr-2" /> Delete
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
