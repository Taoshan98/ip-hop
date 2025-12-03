'use client';

import { useAuth } from '@/context/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { LayoutDashboard, Server, LogOut, Globe } from 'lucide-react';
import { ThemeToggle } from '@/components/theme-toggle';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { isAuthenticated, isLoading, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push('/login');
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="text-center">
                    <Globe className="w-12 h-12 animate-pulse mx-auto mb-4 text-primary" />
                    <p className="text-muted-foreground">Loading...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return null;
    }

    const navItems = [
        { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { href: '/dashboard/domains', icon: Globe, label: 'Domains' },
        { href: '/dashboard/providers', icon: Server, label: 'Providers' },
    ];

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            {/* Desktop Sidebar */}
            <aside className="hidden lg:flex lg:flex-col w-64 bg-card border-r border-border">
                {/* Header */}
                <div className="p-6 border-b border-border">
                    <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
                        <Globe className="w-6 h-6" /> IP-HOP
                    </h1>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = pathname === item.href;
                        return (
                            <Link key={item.href} href={item.href}>
                                <Button
                                    variant={isActive ? "secondary" : "ghost"}
                                    className="w-full justify-start gap-2 h-10"
                                >
                                    <Icon className="w-4 h-4" /> {item.label}
                                </Button>
                            </Link>
                        );
                    })}
                </nav>

                {/* Footer */}
                <div className="p-4 border-t border-border space-y-3">
                    <ThemeToggle />
                    <Button
                        variant="outline"
                        className="w-full gap-2 h-10"
                        onClick={logout}
                    >
                        <LogOut className="w-4 h-4" /> Logout
                    </Button>
                </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-h-0">
                {/* Mobile Header */}
                <header className="lg:hidden flex flex-col gap-3 p-3 border-b border-border bg-card flex-shrink-0">
                    {/* Logo Row */}
                    <div className="flex items-center justify-center">
                        <h1 className="text-lg font-bold text-primary flex items-center gap-2">
                            <Globe className="w-5 h-5" /> IP-HOP
                        </h1>
                    </div>
                    {/* Theme Toggle Row */}
                    <div className="w-full max-w-xs mx-auto">
                        <ThemeToggle />
                    </div>
                </header>

                {/* Scrollable Content */}
                <main className="flex-1 overflow-y-auto">
                    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto pb-20 lg:pb-8">
                        {children}
                    </div>
                </main>

                {/* Mobile Bottom Navigation */}
                <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-card border-t border-border safe-bottom z-40">
                    <div className="flex items-center justify-around h-16 px-2">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`
                                        flex flex-col items-center justify-center gap-1 px-3 py-2 rounded-lg
                                        transition-colors min-w-[60px]
                                        ${isActive
                                            ? 'text-primary bg-primary/10'
                                            : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                                        }
                                    `}
                                >
                                    <Icon className="w-5 h-5" />
                                    <span className="text-[10px] font-medium">{item.label}</span>
                                </Link>
                            );
                        })}
                        <button
                            onClick={logout}
                            className="flex flex-col items-center justify-center gap-1 px-3 py-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors min-w-[60px]"
                        >
                            <LogOut className="w-5 h-5" />
                            <span className="text-[10px] font-medium">Logout</span>
                        </button>
                    </div>
                </nav>
            </div>
        </div>
    );
}
