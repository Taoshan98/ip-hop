import { cn } from '@/lib/utils';

describe('utils', () => {
    describe('cn', () => {
        it('should merge class names correctly', () => {
            const result = cn('foo', 'bar');
            expect(result).toBe('foo bar');
        });

        it('should handle conditional classes', () => {
            const result = cn('foo', false && 'bar', 'baz');
            expect(result).toBe('foo baz');
        });

        it('should merge Tailwind classes without conflicts', () => {
            const result = cn('px-2 py-1', 'p-3');
            expect(result).toBe('p-3');
        });

        it('should handle empty inputs', () => {
            const result = cn();
            expect(result).toBe('');
        });

        it('should handle undefined and null', () => {
            const result = cn('foo', undefined, null, 'bar');
            expect(result).toBe('foo bar');
        });

        it('should handle arrays of class names', () => {
            const result = cn(['foo', 'bar'], 'baz');
            expect(result).toBe('foo bar baz');
        });

        it('should handle objects with boolean values', () => {
            const result = cn({
                foo: true,
                bar: false,
                baz: true,
            });
            expect(result).toBe('foo baz');
        });
    });
});
