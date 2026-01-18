/**
 * API client for E-KYC Check backend
 */

import axios from 'axios';
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import type {
  IndividualVerificationRequest,
  CorporateVerificationRequest,
  VerificationResponse,
  ErrorResponse,
} from '@/types/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const apiKey = import.meta.env.VITE_API_KEY || '';

    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      timeout: 30000, // 30 seconds
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error: unknown) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`[API] Response ${response.status}`, response.data);
        return response;
      },
      (error: AxiosError<ErrorResponse>) => {
        if (error.response) {
          console.error('[API] Error:', error.response.status, error.response.data);
        } else if (error.request) {
          console.error('[API] No response:', error.message);
        } else {
          console.error('[API] Request error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Verify an individual using BVN and NIN
   */
  async verifyIndividual(
    data: IndividualVerificationRequest
  ): Promise<VerificationResponse> {
    const response = await this.client.post<VerificationResponse>(
      '/api/v1/verify/individual',
      data
    );
    return response.data;
  }

  /**
   * Verify a corporate entity using CAC registration
   */
  async verifyCorporate(
    data: CorporateVerificationRequest
  ): Promise<VerificationResponse> {
    const response = await this.client.post<VerificationResponse>(
      '/api/v1/verify/corporate',
      data
    );
    return response.data;
  }

  /**
   * Get verification result by ID
   */
  async getVerification(verificationId: string): Promise<VerificationResponse> {
    const response = await this.client.get<VerificationResponse>(
      `/api/v1/verify/${verificationId}`
    );
    return response.data;
  }

  /**
   * Get HTML report URL
   */
  getReportUrl(verificationId: string): string {
    return `${this.client.defaults.baseURL}/api/v1/reports/${verificationId}`;
  }

  /**
   * Get PDF report URL
   */
  getPdfReportUrl(verificationId: string): string {
    return `${this.client.defaults.baseURL}/api/v1/reports/${verificationId}/pdf`;
  }

  /**
   * Download PDF report with authentication
   */
  async downloadPdfReport(verificationId: string): Promise<void> {
    try {
      console.log('[PDF Download] Starting download for:', verificationId);
      
      const response = await this.client.get(
        `/api/v1/reports/${verificationId}/pdf`,
        {
          responseType: 'blob', // Important for binary data
        }
      );

      console.log('[PDF Download] Response received:', {
        status: response.status,
        contentType: response.headers['content-type'],
        size: response.data.size
      });

      // Create a blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `verification_${verificationId}.pdf`;
      document.body.appendChild(link);
      link.click();
      
      console.log('[PDF Download] Download triggered');
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }, 100);
    } catch (error) {
      console.error('[PDF Download] Failed:', error);
      throw error;
    }
  }

  /**
   * Update API key (for when user changes it)
   */
  setApiKey(apiKey: string): void {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${apiKey}`;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
