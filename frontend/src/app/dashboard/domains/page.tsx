'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { getErrorMessage } from '@/lib/errors';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Trash2, Plus, RefreshCw, Globe, History, Clock, Pencil } from 'lucide-react';
import { useState } from 'react';
import { useConfirmDialog } from '@/components/confirm-dialog';
import { toast } from 'sonner';
import { HistoryModal } from '@/components/history-modal';

interface Provider {
    id: number;
    name: string;
    type: string;
}

interface Domain {
    id: number;
    domain_name: string;
    provider_id: number;
    external_id: string | null;
    config: Record<string, any>;
    last_known_ip: string | null;
    last_update_status: string | null;
    cron_schedule: string | null;
}

export default function DomainsPage() {
    const queryClient = useQueryClient();
    const { confirm } = useConfirmDialog();
    const [isAdding, setIsAdding] = useState(false);
    const [editingDomain, setEditingDomain] = useState<Domain | null>(null);
    const [updatingId, setUpdatingId] = useState<number | null>(null);
    const [historyDomain, setHistoryDomain] = useState<Domain | null>(null);
    const [isHistoryOpen, setIsHistoryOpen] = useState(false);

    // Form State
    const [domainName, setDomainName] = useState('');
    const [providerId, setProviderId] = useState<number | ''>('');
    const [externalId, setExternalId] = useState('');
    const [recordId, setRecordId] = useState('');
    const [proxied, setProxied] = useState(false);
    const [cronSchedule, setCronSchedule] = useState('');

    // Fetch providers for dropdown
    const { data: providers } = useQuery<Provider[]>({
        queryKey: ['providers'],
        queryFn: async () => {
            const res = await api.get('/providers');
            return res.data;
        },
    });

    // Fetch domains
    const { data: domains, isLoading } = useQuery<Domain[]>({
        queryKey: ['domains'],
        queryFn: async () => {
            const res = await api.get('/domains');
            return res.data;
        },
    });

    const createMutation = useMutation({
        mutationFn: async () => {
            const config: Record<string, any> = {};

            // Add provider-specific config
            const selectedProvider = providers?.find(p => p.id === providerId);
            if (selectedProvider?.type === 'cloudflare') {
                if (recordId) config.record_id = recordId;
                config.proxied = proxied;
            }

            await api.post('/domains', {
                domain_name: domainName,
                provider_id: providerId,
                external_id: externalId || null,
                config,
                cron_schedule: cronSchedule || null
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['domains'] });
            resetForm();
        },
        onError: (error: unknown) => {
            toast.error('Failed to create domain', {
                description: getErrorMessage(error)
            });
        }
    });

    const updateMutation = useMutation({
        mutationFn: async (id: number) => {
            const payload: Record<string, unknown> = {
                domain_name: domainName,
            };

            if (externalId) {
                payload.external_id = externalId;
            }

            // Add provider-specific config
            const domain = domains?.find(d => d.id === id);
            const selectedProvider = providers?.find(p => p.id === domain?.provider_id);
            if (selectedProvider?.type === 'cloudflare') {
                const config = {
                    ...domain?.config,
                    proxied
                } as Record<string, unknown>;
                if (recordId) {
                    config.record_id = recordId;
                }
                payload.config = config;
            }

            // Update cron schedule
            payload.cron_schedule = cronSchedule || null;

            await api.put(`/domains/${id}`, payload);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['domains'] });
            resetForm();
        },
        onError: (error: unknown) => {
            toast.error('Failed to update domain', {
                description: getErrorMessage(error)
            });
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            await api.delete(`/domains/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['domains'] });
        },
        onError: (error: unknown) => {
            toast.error('Failed to delete domain', {
                description: getErrorMessage(error)
            });
        }
    });

    const updateIpMutation = useMutation({
        mutationFn: async (id: number) => {
            setUpdatingId(id);
            await api.post(`/domains/${id}/update_ip`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['domains'] });
            setUpdatingId(null);
            toast.success('IP Updated', {
                description: 'Domain IP has been updated successfully'
            });
        },
        onError: (error: unknown) => {
            setUpdatingId(null);
            toast.error('Failed to update IP', {
                description: getErrorMessage(error)
            });
        }
    });

    const resetForm = () => {
        setIsAdding(false);
        setEditingDomain(null);
        setDomainName('');
        setProviderId('');
        setExternalId('');
        setRecordId('');
        setProxied(false);
        setCronSchedule('');
    };

    const handleEdit = (domain: Domain) => {
        setEditingDomain(domain);
        setDomainName(domain.domain_name);
        setProviderId(domain.provider_id);
        setExternalId(domain.external_id || '');
        setRecordId(domain.config?.record_id || '');
        setProxied(domain.config?.proxied || false);
        setCronSchedule(domain.cron_schedule || '');
        setIsAdding(true);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (editingDomain) {
            updateMutation.mutate(editingDomain.id);
        } else {
            createMutation.mutate();
        }
    };

    const getProviderName = (providerId: number) => {
        const provider = providers?.find(p => p.id === providerId);
        return provider?.name || 'Unknown';
    };

    const getProviderType = (providerId: number) => {
        const provider = providers?.find(p => p.id === providerId);
        return provider?.type || '';
    };

    const selectedProviderType = providerId ? getProviderType(Number(providerId)) : '';

    if (isLoading) return <div>Loading...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold tracking-tight">Domains</h2>
                {!isAdding && (
                    <Button onClick={() => { resetForm(); setIsAdding(true); }}>
                        <Plus className="w-4 h-4 mr-2" /> Add Domain
                    </Button>
                )}
            </div>

            {isAdding && (
                <Card className="mb-6 border-primary">
                    <CardHeader>
                        <CardTitle>{editingDomain ? 'Edit Domain' : 'Add New Domain'}</CardTitle>
                        <CardDescription>Configure domain settings.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Domain Name *</Label>
                                    <Input
                                        value={domainName}
                                        onChange={e => setDomainName(e.target.value)}
                                        placeholder="example.com"
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Provider *</Label>
                                    <select
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                                        value={providerId}
                                        onChange={e => setProviderId(Number(e.target.value))}
                                        required
                                        disabled={!!editingDomain}
                                    >
                                        <option value="">Select a provider</option>
                                        {providers?.map(provider => (
                                            <option key={provider.id} value={provider.id}>
                                                {provider.name} ({provider.type})
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Cloudflare-specific fields */}
                                {selectedProviderType === 'cloudflare' && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Zone ID *</Label>
                                            <Input
                                                value={externalId}
                                                onChange={e => setExternalId(e.target.value)}
                                                placeholder="Cloudflare Zone ID"
                                                required
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Record ID *</Label>
                                            <Input
                                                value={recordId}
                                                onChange={e => setRecordId(e.target.value)}
                                                placeholder="DNS Record ID"
                                                required
                                            />
                                        </div>
                                        <div className="col-span-2 flex items-center space-x-2">
                                            <input
                                                type="checkbox"
                                                id="proxied"
                                                checked={proxied}
                                                onChange={e => setProxied(e.target.checked)}
                                                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                            />
                                            <Label htmlFor="proxied">Enable Cloudflare Proxy (Orange Cloud)</Label>
                                        </div>
                                    </>
                                )}

                                {/* Dynu-specific field */}
                                {selectedProviderType === 'dynu' && (
                                    <div className="col-span-2 space-y-2">
                                        <Label>Domain ID (Optional)</Label>
                                        <Input
                                            value={externalId}
                                            onChange={e => setExternalId(e.target.value)}
                                            placeholder="Dynu Domain ID"
                                        />
                                    </div>
                                )}

                                {/* DuckDNS-specific field */}
                                {selectedProviderType === 'duckdns' && (
                                    <div className="col-span-2 p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-md text-sm">
                                        <p className="font-medium">DuckDNS Configuration</p>
                                        <p>No additional configuration needed! You can enter just the subdomain (e.g., "mysubdomain") or the full domain ("mysubdomain.duckdns.org").</p>
                                    </div>
                                )}

                                <div className="col-span-2 space-y-2">
                                    <Label>Auto-Update Schedule (Cron Expression)</Label>
                                    <Input
                                        value={cronSchedule}
                                        onChange={e => setCronSchedule(e.target.value)}
                                        placeholder="*/5 * * * * (Every 5 minutes)"
                                    />
                                    <p className="text-xs text-muted-foreground">
                                        Leave empty to disable auto-updates. Format: * * * * * (min hour day month week)
                                    </p>
                                </div>
                            </div>
                            <div className="flex justify-end gap-2">
                                <Button type="button" variant="ghost" onClick={resetForm}>Cancel</Button>
                                <Button type="submit">{editingDomain ? 'Update' : 'Save'} Domain</Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {domains?.map((domain) => (
                    <Card key={domain.id}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <div className="flex items-center gap-2">
                                <Globe className="h-4 w-4 text-muted-foreground" />
                                <CardTitle className="text-sm font-medium">
                                    {domain.domain_name}
                                </CardTitle>
                            </div>
                            {domain.last_update_status === 'SUCCESS' && (
                                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">✓</span>
                            )}
                            {domain.last_update_status === 'FAILED' && (
                                <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">✗</span>
                            )}
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-2 text-sm">
                                <div>
                                    <span className="text-muted-foreground">Provider:</span>{' '}
                                    <span className="font-medium">{getProviderName(domain.provider_id)}</span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Current IP:</span>{' '}
                                    <span className="font-mono text-xs">{domain.last_known_ip || 'Unknown'}</span>
                                </div>
                                {domain.external_id && (
                                    <div>
                                        <span className="text-muted-foreground">External ID:</span>{' '}
                                        <span className="font-mono text-xs">{domain.external_id}</span>
                                    </div>
                                )}
                            </div>

                            {domain.cron_schedule && (
                                <div className="flex items-center gap-2 px-4 py-2 my-3 rounded-xl bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm border border-gray-200 dark:border-gray-700 shadow-lg w-full">
                                    <div className="p-1.5 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600">
                                        <Clock className="w-3.5 h-3.5 text-white" />
                                    </div>
                                    <span className="font-mono my-1 text-sm font-medium text-gray-800 dark:text-gray-100">
                                        {domain.cron_schedule}
                                    </span>
                                </div>
                            )}

                            <div className="mt-4 flex flex-col gap-2">
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    className="w-full"
                                    onClick={() => {
                                        setHistoryDomain(domain);
                                        setIsHistoryOpen(true);
                                    }}
                                >
                                    <History className="w-4 h-4 mr-2" /> View History
                                </Button>
                                <div className="flex gap-2">
                                    <Button
                                        size="sm"
                                        className="flex-1 bg-yellow-500 hover:bg-yellow-600"
                                        disabled={updatingId === domain.id}
                                        onClick={() => updateIpMutation.mutate(domain.id)}
                                    >
                                        {updatingId === domain.id ? (
                                            <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                                        ) : (
                                            <RefreshCw className="w-4 h-4 mr-2" />
                                        )}
                                        {updatingId === domain.id ? 'Updating...' : 'Update IP'}
                                    </Button>
                                    <Button
                                        size="sm"
                                        className="flex-1"
                                        onClick={() => handleEdit(domain)}
                                    >
                                        <Pencil className="w-4 h-4 mr-2" /> Edit
                                    </Button>
                                    <Button
                                        variant="destructive"
                                        size="sm"
                                        className="flex-1"
                                        onClick={() => {
                                            confirm({
                                                title: 'Delete Domain',
                                                description: `Are you sure you want to delete "${domain.domain_name}"? This action cannot be undone.`,
                                                confirmText: 'Delete',
                                                cancelText: 'Cancel',
                                                variant: 'destructive',
                                                onConfirm: () => {
                                                    deleteMutation.mutate(domain.id);
                                                }
                                            });
                                        }}
                                    >
                                        <Trash2 className="w-4 h-4 mr-2" /> Delete
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
                {domains?.length === 0 && (
                    <div className="col-span-full text-center text-gray-500 py-10">
                        No domains configured. Add your first domain to get started.
                    </div>
                )}
            </div>

            <HistoryModal
                domainId={historyDomain?.id || null}
                domainName={historyDomain?.domain_name || ''}
                isOpen={isHistoryOpen}
                onClose={() => setIsHistoryOpen(false)}
            />
        </div>
    );
}
