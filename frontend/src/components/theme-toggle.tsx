'use client';

import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

export function ThemeToggle() {
    const { theme, setTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return (
            <div className="inline-flex h-9 w-auto items-center rounded-full bg-secondary/30 p-1">
                <div className="h-7 w-7 rounded-full bg-primary/20 animate-pulse" />
            </div>
        );
    }

    const themeOptions = [
        { value: 'light', icon: Sun, label: 'Light' },
        { value: 'dark', icon: Moon, label: 'Dark' },
        { value: 'system', icon: Monitor, label: 'Auto' }
    ];

    return (
        <div className="inline-flex h-9 w-full lg:w-auto items-center justify-center rounded-full bg-secondary/50 p-0.5 backdrop-blur-sm border border-border/50">
            <div className="flex gap-0.5 w-full">
                {themeOptions.map(({ value, icon: Icon, label }) => {
                    const isActive = theme === value;
                    return (
                        <button
                            key={value}
                            onClick={() => setTheme(value)}
                            className={`
                                flex-1 lg:flex-none flex items-center justify-center h-8 lg:px-3 px-2 rounded-full
                                transition-all duration-200 ease-in-out
                                ${isActive
                                    ? 'bg-primary text-primary-foreground shadow-sm'
                                    : 'hover:bg-accent text-muted-foreground hover:text-foreground'
                                }
                            `}
                            aria-label={`${label} theme`}
                            title={`Switch to ${label.toLowerCase()} theme`}
                            type="button"
                        >
                            <Icon className="h-4 w-4 flex-shrink-0" />
                            <span className="ml-1.5 text-xs font-medium hidden lg:inline">
                                {label}
                            </span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
