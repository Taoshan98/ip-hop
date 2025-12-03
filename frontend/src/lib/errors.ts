import axios, { AxiosError } from 'axios';

// API Error response structure
interface ApiErrorResponse {
    detail?: string;
    message?: string;
}

// API Error type for typed error handling
export interface ApiError {
    message: string;
    detail?: string;
    status?: number;
}

// Type guard for Axios errors
export function isAxiosError(error: unknown): error is AxiosError<ApiErrorResponse> {
    return axios.isAxiosError(error);
}

// Extract error message from unknown error
export function getErrorMessage(error: unknown): string {
    if (isAxiosError(error)) {
        return error.response?.data?.detail || error.message || 'An error occurred';
    }

    if (error instanceof Error) {
        return error.message;
    }

    return 'An unknown error occurred';
}
