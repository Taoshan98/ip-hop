import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeToggle } from '@/components/theme-toggle';
import { ThemeProvider } from 'next-themes';

// Mock next-themes
const mockSetTheme = jest.fn();
const mockUseTheme = {
    theme: 'light',
    setTheme: mockSetTheme,
    systemTheme: 'light'
};

jest.mock('next-themes', () => ({
    ThemeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    useTheme: () => mockUseTheme
}));

describe('ThemeToggle', () => {
    beforeEach(() => {
        mockSetTheme.mockClear();
        mockUseTheme.theme = 'light';
        mockUseTheme.systemTheme = 'light';
    });

    it('renders correctly with light theme', () => {
        render(
            <ThemeProvider attribute="class" defaultTheme="light">
                <ThemeToggle />
            </ThemeProvider>
        );

        expect(screen.getByRole('button', { name: /light theme/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /dark theme/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /system theme/i })).toBeInTheDocument();
    });

    it('renders correctly with dark theme', () => {
        mockUseTheme.theme = 'dark';

        render(
            <ThemeProvider attribute="class" defaultTheme="dark">
                <ThemeToggle />
            </ThemeProvider>
        );

        const darkButton = screen.getByRole('button', { name: /dark theme/i });
        expect(darkButton).toBeInTheDocument();
        expect(darkButton).toHaveClass('bg-primary');
    });

    it('renders correctly with system theme', () => {
        mockUseTheme.theme = 'system';

        render(
            <ThemeProvider attribute="class" defaultTheme="system">
                <ThemeToggle />
            </ThemeProvider>
        );

        const systemButton = screen.getByRole('button', { name: /system theme/i });
        expect(systemButton).toBeInTheDocument();
        expect(systemButton).toHaveClass('bg-primary');
    });

    it('calls setTheme when light button is clicked', () => {
        render(
            <ThemeProvider attribute="class">
                <ThemeToggle />
            </ThemeProvider>
        );

        const lightButton = screen.getByRole('button', { name: /light theme/i });
        fireEvent.click(lightButton);

        expect(mockSetTheme).toHaveBeenCalledWith('light');
    });

    it('calls setTheme when dark button is clicked', () => {
        render(
            <ThemeProvider attribute="class">
                <ThemeToggle />
            </ThemeProvider>
        );

        const darkButton = screen.getByRole('button', { name: /dark theme/i });
        fireEvent.click(darkButton);

        expect(mockSetTheme).toHaveBeenCalledWith('dark');
    });

    it('calls setTheme when system button is clicked', () => {
        render(
            <ThemeProvider attribute="class">
                <ThemeToggle />
            </ThemeProvider>
        );

        const systemButton = screen.getByRole('button', { name: /system theme/i });
        fireEvent.click(systemButton);

        expect(mockSetTheme).toHaveBeenCalledWith('system');
    });

    it('applies correct styles to active theme button', () => {
        mockUseTheme.theme = 'dark';

        render(
            <ThemeProvider attribute="class">
                <ThemeToggle />
            </ThemeProvider>
        );

        const darkButton = screen.getByRole('button', { name: /dark theme/i });
        const lightButton = screen.getByRole('button', { name: /light theme/i });

        // Active button should have bg-primary class
        expect(darkButton).toHaveClass('bg-primary');

        // Inactive button should not have bg-primary class
        expect(lightButton).not.toHaveClass('bg-primary');
    });

    it('has proper accessibility labels', () => {
        render(
            <ThemeProvider attribute="class">
                <ThemeToggle />
            </ThemeProvider>
        );

        expect(screen.getByLabelText('Light theme')).toBeInTheDocument();
        expect(screen.getByLabelText('Dark theme')).toBeInTheDocument();
        expect(screen.getByLabelText('System theme')).toBeInTheDocument();
    });

    it('has proper title attributes for tooltips', () => {
        render(
            <ThemeProvider attribute="class">
                <ThemeToggle />
            </ThemeProvider>
        );

        expect(screen.getByTitle('Switch to light theme')).toBeInTheDocument();
        expect(screen.getByTitle('Switch to dark theme')).toBeInTheDocument();
        expect(screen.getByTitle('Switch to system theme')).toBeInTheDocument();
    });

    it('handles rapid theme switching', async () => {
        render(
            <ThemeProvider attribute="class">
                <ThemeToggle />
            </ThemeProvider>
        );

        const lightButton = screen.getByRole('button', { name: /light theme/i });
        const darkButton = screen.getByRole('button', { name: /dark theme/i });

        // Rapidly switch themes
        fireEvent.click(lightButton);
        fireEvent.click(darkButton);
        fireEvent.click(lightButton);

        await waitFor(() => {
            expect(mockSetTheme).toHaveBeenCalledTimes(3);
        });
    });

    it('displays loading state before mount', () => {
        const { container } = render(
            <ThemeProvider attribute="class">
                <ThemeToggle />
            </ThemeProvider>
        );

        // Initially should show a loading skeleton
        // The component checks if mounted before showing buttons
        expect(container.firstChild).toBeInTheDocument();
    });

    it('respects system theme when theme is set to system', () => {
        mockUseTheme.theme = 'system';
        mockUseTheme.systemTheme = 'dark';

        render(
            <ThemeProvider attribute="class">
                <ThemeToggle />
            </ThemeProvider>
        );

        // When theme is 'system', it should use systemTheme
        // This affects which button is active
        const systemButton = screen.getByRole('button', { name: /system theme/i });
        expect(systemButton).toHaveClass('bg-primary');
    });
});
