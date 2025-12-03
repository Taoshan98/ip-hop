import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function proxy(request: NextRequest) {
    const path = request.nextUrl.pathname;

    // Skip API routes and static files
    if (path.startsWith('/api') || path.startsWith('/_next') || path.includes('.')) {
        return NextResponse.next();
    }

    try {
        // Check System Status
        // Note: We use the internal backend URL here because proxy runs on the server
        const backendUrl = 'http://127.0.0.1:8001/api/v1/system/status';
        const statusRes = await fetch(backendUrl);

        if (statusRes.ok) {
            const status = await statusRes.json();
            const isInitialized = status.initialized;

            // 1. If NOT initialized, force /setup
            if (!isInitialized && path !== '/setup') {
                return NextResponse.redirect(new URL('/setup', request.url));
            }

            // 2. If initialized and on /setup, redirect to /login
            if (isInitialized && path === '/setup') {
                return NextResponse.redirect(new URL('/login', request.url));
            }

            // 3. Auth Check (Basic check for token presence in cookie/localstorage is hard in proxy if using localStorage)
            // Since we are using localStorage for now (as per original plan), proxy can't check it.
            // We rely on client-side protection for /dashboard.
            // However, we can check if we are on root / and redirect to dashboard or login.
            if (path === '/') {
                return NextResponse.redirect(new URL('/dashboard', request.url));
            }
        }
    } catch (e) {
        console.error("Proxy Error checking system status:", e);
        // If backend is down, maybe allow access or show error? 
        // For now, let it pass or maybe fail safe.
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
