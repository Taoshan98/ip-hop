import { render, screen } from '@testing-library/react';
import { Input } from '@/components/ui/input';
import userEvent from '@testing-library/user-event';

describe('Input', () => {
    it('should render with default props', () => {
        render(<Input />);
        const input = screen.getByRole('textbox');
        expect(input).toBeInTheDocument();
    });

    it('should render with different types', () => {
        const { rerender } = render(<Input type="password" data-testid="password-input" />);
        const passwordInput = screen.getByTestId('password-input');
        expect(passwordInput).toHaveAttribute('type', 'password');

        rerender(<Input type="email" />);
        const emailInput = screen.getByRole('textbox');
        expect(emailInput).toHaveAttribute('type', 'email');

        rerender(<Input type="number" />);
        expect(screen.getByRole('spinbutton')).toHaveAttribute('type', 'number');
    });

    it('should handle value changes', async () => {
        const handleChange = jest.fn();
        const user = userEvent.setup();

        render(<Input onChange={handleChange} />);
        const input = screen.getByRole('textbox');

        await user.type(input, 'test value');

        expect(handleChange).toHaveBeenCalled();
        expect(input).toHaveValue('test value');
    });

    it('should have placeholder text', () => {
        render(<Input placeholder="Enter your name" />);
        expect(screen.getByPlaceholderText('Enter your name')).toBeInTheDocument();
    });

    it('should be disabled when disabled prop is true', () => {
        render(<Input disabled />);
        const input = screen.getByRole('textbox');
        expect(input).toBeDisabled();
        expect(input).toHaveClass('disabled:opacity-50');
    });

    it('should apply custom className', () => {
        render(<Input className="custom-input" />);
        expect(screen.getByRole('textbox')).toHaveClass('custom-input');
    });

    it('should accept HTML input attributes', () => {
        render(<Input name="username" required maxLength={100} />);
        const input = screen.getByRole('textbox');
        expect(input).toHaveAttribute('name', 'username');
        expect(input).toHaveAttribute('required');
        expect(input).toHaveAttribute('maxLength', '100');
    });

    it('should support controlled input', () => {
        const { rerender } = render(<Input value="controlled" onChange={() => { }} />);
        expect(screen.getByRole('textbox')).toHaveValue('controlled');

        rerender(<Input value="updated" onChange={() => { }} />);
        expect(screen.getByRole('textbox')).toHaveValue('updated');
    });
});
