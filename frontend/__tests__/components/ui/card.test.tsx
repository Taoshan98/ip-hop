import { render, screen } from '@testing-library/react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

describe('Card Components', () => {
    describe('Card', () => {
        it('should render children', () => {
            render(<Card>Card content</Card>);
            expect(screen.getByText('Card content')).toBeInTheDocument();
        });

        it('should apply custom className', () => {
            const { container } = render(<Card className="custom-card">Content</Card>);
            expect(container.firstChild).toHaveClass('custom-card');
        });
    });

    describe('CardHeader', () => {
        it('should render children', () => {
            render(<CardHeader>Header content</CardHeader>);
            expect(screen.getByText('Header content')).toBeInTheDocument();
        });
    });

    describe('CardTitle', () => {
        it('should render children', () => {
            render(<CardTitle>Title</CardTitle>);
            expect(screen.getByText('Title')).toBeInTheDocument();
        });

        it('should apply heading styles', () => {
            const { container } = render(<CardTitle>Title</CardTitle>);
            expect(container.firstChild).toHaveClass('font-semibold');
        });
    });

    describe('CardDescription', () => {
        it('should render children', () => {
            render(<CardDescription>Description text</CardDescription>);
            expect(screen.getByText('Description text')).toBeInTheDocument();
        });
    });

    describe('CardContent', () => {
        it('should render children', () => {
            render(<CardContent>Main content</CardContent>);
            expect(screen.getByText('Main content')).toBeInTheDocument();
        });
    });

    describe('CardFooter', () => {
        it('should render children', () => {
            render(<CardFooter>Footer content</CardFooter>);
            expect(screen.getByText('Footer content')).toBeInTheDocument();
        });
    });

    it('should render a complete card structure', () => {
        render(
            <Card>
                <CardHeader>
                    <CardTitle>Test Card</CardTitle>
                    <CardDescription>This is a test card</CardDescription>
                </CardHeader>
                <CardContent>Card body content</CardContent>
                <CardFooter>Card footer</CardFooter>
            </Card>
        );

        expect(screen.getByText('Test Card')).toBeInTheDocument();
        expect(screen.getByText('This is a test card')).toBeInTheDocument();
        expect(screen.getByText('Card body content')).toBeInTheDocument();
        expect(screen.getByText('Card footer')).toBeInTheDocument();
    });
});
