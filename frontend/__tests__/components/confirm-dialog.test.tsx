import { render, screen, waitFor } from '@testing-library/react';
import { ConfirmDialogProvider, useConfirmDialog } from '@/components/confirm-dialog';
import userEvent from '@testing-library/user-event';

// Test component that uses the confirm dialog
function TestComponent() {
    const { confirm } = useConfirmDialog();

    return (
        <button onClick={() => confirm({
            title: 'Delete Item',
            description: 'Are you sure you want to delete this item?',
            confirmText: 'Delete',
            cancelText: 'Cancel',
            onConfirm: jest.fn(),
        })}>
            Open Dialog
        </button>
    );
}

describe('ConfirmDialog', () => {
    it('should render dialog when confirm is called', async () => {
        const user = userEvent.setup();

        render(
            <ConfirmDialogProvider>
                <TestComponent />
            </ConfirmDialogProvider>
        );

        const button = screen.getByText('Open Dialog');
        await user.click(button);

        await waitFor(() => {
            expect(screen.getByText('Delete Item')).toBeInTheDocument();
            expect(screen.getByText('Are you sure you want to delete this item?')).toBeInTheDocument();
        });
    });

    it('should use default text when not provided', async () => {
        const user = userEvent.setup();

        function DefaultTextComponent() {
            const { confirm } = useConfirmDialog();

            return (
                <button onClick={() => confirm({ onConfirm: jest.fn() })}>
                    Open
                </button>
            );
        }

        render(
            <ConfirmDialogProvider>
                <DefaultTextComponent />
            </ConfirmDialogProvider>
        );

        await user.click(screen.getByText('Open'));

        await waitFor(() => {
            expect(screen.getByText('Are you sure?')).toBeInTheDocument();
            expect(screen.getByText('This action cannot be undone.')).toBeInTheDocument();
        });
    });

    it('should call onConfirm when confirmed', async () => {
        const onConfirm = jest.fn();
        const user = userEvent.setup();

        function ConfirmTestComponent() {
            const { confirm } = useConfirmDialog();

            return (
                <button onClick={() => confirm({ onConfirm })}>
                    Test
                </button>
            );
        }

        render(
            <ConfirmDialogProvider>
                <ConfirmTestComponent />
            </ConfirmDialogProvider>
        );

        await user.click(screen.getByText('Test'));

        await waitFor(() => {
            expect(screen.getByText('Confirm')).toBeInTheDocument();
        });

        await user.click(screen.getByText('Confirm'));

        await waitFor(() => {
            expect(onConfirm).toHaveBeenCalled();
        });
    });

    it('should throw error when used outside provider', () => {
        // Suppress console errors for this test
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

        expect(() => {
            function InvalidComponent() {
                useConfirmDialog();
                return null;
            }
            render(<InvalidComponent />);
        }).toThrow('useConfirmDialog must be used within ConfirmDialogProvider');

        consoleSpy.mockRestore();
    });
});
