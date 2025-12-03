'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, CheckCircle, XCircle, Clock, Globe, TrendingUp, Activity, Server, Zap, AlertTriangle } from 'lucide-react';
import { useState } from 'react';

interface Domain {
    id: number;
    domain_name: string;
    provider_id: number;
    last_known_ip: string | null;
    last_update_status: string | null;
}

interface DashboardMetrics {
    total_domains: number;
    active_domains: number;
    success_rate_24h: number;
    total_updates_24h: number;
    failed_updates_24h: number;
    unique_ips_24h: number;
    last_update_time: string | null;
    providers_stats: Array<{
        type: string;
        count: number;
        active: number;
    }>;
}

interface UptimeMetrics {
    uptime_24h: number;
    uptime_7d: number;
    total_requests_24h: number;
    successful_requests_24h: number;
    scheduler_status: string;
}

interface IPChangeMetrics {
    total_changes_last_week: number;
    average_changes_per_day: number;
    domains: Array<{
        domain_id: number;
        domain_name: string;
        changes_last_week: number;
        changes_per_day: number;
    }>;
}

export default function DashboardPage() {
    const queryClient = useQueryClient();
    const [updatingId, setUpdatingId] = useState<number | null>(null);

    const { data: metrics, isLoading: metricsLoading } = useQuery<DashboardMetrics>({
        queryKey: ['dashboard-metrics'],
        queryFn: async () => {
            const res = await api.get('/metrics/dashboard');
            return res.data;
        },
        refetchInterval: 30000,
    });

    const { data: uptimeMetrics } = useQuery<UptimeMetrics>({
        queryKey: ['uptime-metrics'],
        queryFn: async () => {
            const res = await api.get('/metrics/uptime');
            return res.data;
        },
        refetchInterval: 60000,
    });

    const { data: ipChanges } = useQuery<IPChangeMetrics>({
        queryKey: ['ip-changes'],
        queryFn: async () => {
            const res = await api.get('/metrics/ip-changes');
            return res.data;
        },
        refetchInterval: 60000,
    });

    const { data: domains, isLoading, error } = useQuery<Domain[]>({
        queryKey: ['domains'],
        queryFn: async () => {
            const res = await api.get('/domains');
            return res.data;
        },
    });

    const updateMutation = useMutation({
        mutationFn: async (domainId: number) => {
            setUpdatingId(domainId);
            await api.post(`/domains/${domainId}/update_ip`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['domains'] });
            setUpdatingId(null);
        },
        onError: () => {
            setUpdatingId(null);
            alert("Update failed. Check logs.");
        }
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center space-y-3">
                    <RefreshCw className="w-10 h-10 animate-spin mx-auto text-primary" />
                    <p className="text-sm text-muted-foreground">Loading domains...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center space-y-3">
                    <XCircle className="w-12 h-12 mx-auto text-destructive" />
                    <p className="text-sm font-medium">Error loading domains</p>
                    <Button onClick={() => queryClient.invalidateQueries({ queryKey: ['domains'] })} variant="outline" size="sm">
                        <RefreshCw className="w-4 h-4 mr-2" /> Retry
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 sm:space-y-8">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
                <div>
                    <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">Dashboard</h2>
                    <p className="text-sm text-muted-foreground mt-1">Monitor your domains and system metrics</p>
                </div>
                <Button
                    onClick={() => queryClient.invalidateQueries({ queryKey: ['domains'] })}
                    variant="outline"
                    size="sm"
                    className="self-start sm:self-auto"
                >
                    <RefreshCw className="w-4 h-4 mr-2" /> Refresh
                </Button>
            </div>

            {/* Metrics Summary Cards */}
            <div className="grid gap-4 sm:gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
                <Card className="hover:shadow-md transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Domains</CardTitle>
                        <Globe className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{metrics?.total_domains || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {metrics?.active_domains || 0} active
                        </p>
                    </CardContent>
                </Card>

                <Card className="hover:shadow-md transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {metrics?.success_rate_24h?.toFixed(1) || '0.0'}%
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {metrics?.total_updates_24h || 0} updates (24h)
                        </p>
                    </CardContent>
                </Card>

                <Card className="hover:shadow-md transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Updates Today</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{metrics?.total_updates_24h || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {metrics?.failed_updates_24h || 0} failed
                        </p>
                    </CardContent>
                </Card>

                <Card className="hover:shadow-md transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Providers</CardTitle>
                        <Server className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {metrics?.providers_stats?.reduce((acc, p) => acc + (p.active > 0 ? 1 : 0), 0) || 0}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {metrics?.providers_stats?.reduce((acc, p) => acc + p.count, 0) || 0} total
                        </p>
                    </CardContent>
                </Card>

                <Card className="hover:shadow-md transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
                        <Zap className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {uptimeMetrics?.uptime_24h?.toFixed(1) || '100.0'}%
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {uptimeMetrics?.scheduler_status === 'running' ? '✓ Running' : '✗ Stopped'}
                        </p>
                    </CardContent>
                </Card>

                <Card className="hover:shadow-md transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">IP Changes</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{ipChanges?.total_changes_last_week || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {ipChanges?.average_changes_per_day?.toFixed(2) || '0.00'}/day
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Domain Cards */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="text-lg sm:text-xl font-semibold">Your Domains</h3>
                    <span className="text-sm text-muted-foreground">
                        {domains?.length || 0} {domains?.length === 1 ? 'domain' : 'domains'}
                    </span>
                </div>

                {domains && domains.length > 0 ? (
                    <div className="grid gap-4 grid-cols-1 md:grid-cols-2 xl:grid-cols-3">
                        {domains.map((domain) => (
                            <Card key={domain.id} className="hover:shadow-md transition-shadow">
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium truncate pr-2">
                                        {domain.domain_name}
                                    </CardTitle>
                                    {domain.last_update_status === 'SUCCESS' ? (
                                        <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                                    ) : domain.last_update_status === 'FAILED' ? (
                                        <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                                    ) : (
                                        <Clock className="h-4 w-4 text-gray-500 flex-shrink-0" />
                                    )}
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <div className="text-xl sm:text-2xl font-bold break-all">
                                            {domain.last_known_ip || "Unknown IP"}
                                        </div>
                                        <p className="text-xs text-muted-foreground mt-1">
                                            Status: {domain.last_update_status || "Pending"}
                                        </p>
                                    </div>
                                    <Button
                                        size="sm"
                                        className="w-full bg-yellow-500 hover:bg-yellow-600"
                                        disabled={updatingId === domain.id}
                                        onClick={() => updateMutation.mutate(domain.id)}
                                    >
                                        {updatingId === domain.id ? (
                                            <>
                                                <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                                                Updating...
                                            </>
                                        ) : (
                                            <>
                                                <RefreshCw className="w-4 h-4 mr-2" />
                                                Update IP
                                            </>
                                        )}
                                    </Button>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                ) : (
                    <Card>
                        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                            <Globe className="w-12 h-12 text-muted-foreground/50 mb-4" />
                            <h4 className="text-lg font-medium mb-2">No domains configured</h4>
                            <p className="text-sm text-muted-foreground mb-4 max-w-sm">
                                Get started by adding your first domain in the Domains section
                            </p>
                            <Button variant="outline" size="sm" asChild>
                                <a href="/dashboard/domains">Go to Domains</a>
                            </Button>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
