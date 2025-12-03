import { render, screen } from '@testing-library/react';
import { Label } from '@/components/ui/label';

describe('Label', () => {
    it('should render with children', () => {
        render(<Label>Username</Label>);
        expect(screen.getByText('Username')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
        render(<Label className="custom-label">Label</Label>);
        const label = screen.getByText('Label');
        expect(label).toHaveClass('custom-label');
        expect(label).toHaveClass('text-sm');
    });

    it('should support htmlFor attribute', () => {
        render(<Label htmlFor="username-input">Username</Label>);
        const label = screen.getByText('Username');
        expect(label).toHaveAttribute('for', 'username-input');
    });

    it('should apply peer-disabled styles', () => {
        render(<Label>Disabled Label</Label>);
        expect(screen.getByText('Disabled Label')).toHaveClass('peer-disabled:opacity-70');
    });

    it('should maintain font and sizing classes', () => {
        render(<Label>Test</Label>);
        const label = screen.getByText('Test');
        expect(label).toHaveClass('text-sm');
        expect(label).toHaveClass('font-medium');
        expect(label).toHaveClass('leading-none');
    });
});
