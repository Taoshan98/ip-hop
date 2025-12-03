import axios, { AxiosError } from 'axios';
import { isAxiosError, getErrorMessage } from '@/lib/errors';

describe('errors', () => {
    // Restore all mocks after each test to prevent pollution
    afterEach(() => {
        jest.restoreAllMocks();
    });

    describe('isAxiosError', () => {
        it('should return true for Axios errors', () => {
            const axiosError = new AxiosError('Test error');
            expect(isAxiosError(axiosError)).toBe(true);
        });

        it('should return false for regular errors', () => {
            const regularError = new Error('Test error');
            expect(isAxiosError(regularError)).toBe(false);
        });

        it('should return false for non-error values', () => {
            expect(isAxiosError('string')).toBe(false);
            expect(isAxiosError(null)).toBe(false);
            expect(isAxiosError(undefined)).toBe(false);
            expect(isAxiosError({})).toBe(false);
            expect(isAxiosError(42)).toBe(false);
        });
    });

    describe('getErrorMessage', () => {
        it('should extract detail from Axios error response', () => {
            const axiosError = {
                isAxiosError: true,
                response: {
                    data: {
                        detail: 'Detailed error message',
                    },
                },
                message: 'Generic message',
            } as AxiosError;

            jest.spyOn(axios, 'isAxiosError').mockReturnValue(true);
            const message = getErrorMessage(axiosError);
            expect(message).toBe('Detailed error message');
        });

        it('should fall back to error message if no detail', () => {
            const axiosError = {
                isAxiosError: true,
                response: {
                    data: {},
                },
                message: 'Network error',
            } as AxiosError;

            jest.spyOn(axios, 'isAxiosError').mockReturnValue(true);
            const message = getErrorMessage(axiosError);
            expect(message).toBe('Network error');
        });

        it('should handle Axios error without response', () => {
            const axiosError = {
                isAxiosError: true,
                message: 'Network error',
            } as AxiosError;

            jest.spyOn(axios, 'isAxiosError').mockReturnValue(true);
            const message = getErrorMessage(axiosError);
            expect(message).toBe('Network error');
        });

        it('should handle regular Error objects', () => {
            const error = new Error('Regular error');
            const message = getErrorMessage(error);
            expect(message).toBe('Regular error');
        });

        it('should handle unknown error types', () => {
            expect(getErrorMessage('string error')).toBe('An unknown error occurred');
            expect(getErrorMessage(null)).toBe('An unknown error occurred');
            expect(getErrorMessage(undefined)).toBe('An unknown error occurred');
            expect(getErrorMessage(42)).toBe('An unknown error occurred');
            expect(getErrorMessage({})).toBe('An unknown error occurred');
        });

        it('should prefer detail over message in Axios response', () => {
            const axiosError = {
                isAxiosError: true,
                response: {
                    data: {
                        detail: 'Specific detail',
                        message: 'Generic message',
                    },
                },
                message: 'Fallback message',
            } as AxiosError;

            jest.spyOn(axios, 'isAxiosError').mockReturnValue(true);
            const message = getErrorMessage(axiosError);
            expect(message).toBe('Specific detail');
        });

        it('should use default message when all else fails', () => {
            const axiosError = {
                isAxiosError: true,
                response: {
                    data: {},
                },
                message: '',
            } as AxiosError;

            jest.spyOn(axios, 'isAxiosError').mockReturnValue(true);
            const message = getErrorMessage(axiosError);
            expect(message).toBe('An error occurred');
        });
    });
});
