import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import { useRouter, usePathname } from 'next/navigation';

jest.mock('@/lib/api');
jest.mock('next/navigation');

// Test component that uses the auth context
function TestComponent() {
    const { isAuthenticated, isLoading, login, logout } = useAuth();

    if (isLoading) return <div>Loading...</div>;

    return (
        <div>
            <div data-testid="auth-status">{isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</div>
            <button onClick={login}>Login</button>
            <button onClick={logout}>Logout</button>
        </div>
    );
}

describe('AuthContext', () => {
    const mockPush = jest.fn();
    const mockGet = jest.fn();
    const mockPost = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
        (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
        (usePathname as jest.Mock).mockReturnValue('/dashboard');
        (api.get as jest.Mock) = mockGet;
        (api.post as jest.Mock) = mockPost;
    });

    it('should provide auth context to children', async () => {
        mockGet.mockResolvedValue({ data: { username: 'test' } });

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        expect(screen.getByText('Loading...')).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
        });
    });

    it('should set authenticated to false when API call fails', async () => {
        mockGet.mockRejectedValue(new Error('Unauthorized'));
        (usePathname as jest.Mock).mockReturnValue('/dashboard');

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => {
            expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
        });

        expect(mockPush).toHaveBeenCalledWith('/login');
    });

    it('should not redirect to login when on login or setup pages', async () => {
        mockGet.mockRejectedValue(new Error('Unauthorized'));
        (usePathname as jest.Mock).mockReturnValue('/login');

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => {
            expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
        });

        expect(mockPush).not.toHaveBeenCalled();
    });

    it('should handle login', async () => {
        mockGet.mockResolvedValue({ data: { username: 'test' } });

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => {
            expect(screen.getByTestId('auth-status')).toBeInTheDocument();
        });

        const loginButton = screen.getByText('Login');
        loginButton.click();

        expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });

    it('should handle logout', async () => {
        mockGet.mockResolvedValue({ data: { username: 'test' } });
        mockPost.mockResolvedValue({});

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => {
            expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
        });

        const logoutButton = screen.getByText('Logout');
        logoutButton.click();

        await waitFor(() => {
            expect(mockPost).toHaveBeenCalledWith('/auth/logout');
            expect(mockPush).toHaveBeenCalledWith('/login');
        });
    });

    it('should handle logout API failure gracefully', async () => {
        mockGet.mockResolvedValue({ data: { username: 'test' } });
        mockPost.mockRejectedValue(new Error('Network error'));

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => {
            expect(screen.getByTestId('auth-status')).toBeInTheDocument();
        });

        const logoutButton = screen.getByText('Logout');
        logoutButton.click();

        await waitFor(() => {
            expect(mockPush).toHaveBeenCalledWith('/login');
        });
    });
});
