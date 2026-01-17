/**
 * Individual verification form component
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { apiClient } from '@/services/api';
import type { VerificationResponse } from '@/types/api';
import './VerificationForm.css';

const schema = z.object({
  bvn: z.string().length(11, 'BVN must be exactly 11 digits').regex(/^\d+$/, 'BVN must contain only digits'),
  nin: z.string().length(11, 'NIN must be exactly 11 digits').regex(/^\d+$/, 'NIN must contain only digits'),
});

type FormData = z.infer<typeof schema>;

export function IndividualVerificationForm() {
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('Submitting individual verification:', data);
      const response = await apiClient.verifyIndividual(data);
      console.log('Verification response:', response);
      setResult(response);
    } catch (err: any) {
      console.error('Verification error:', err);
      const errorMsg = err.response?.data?.message || err.response?.data?.error_code || err.message || 'Verification failed';
      const errorDetails = err.response?.data?.details ? JSON.stringify(err.response.data.details) : '';
      setError(`${errorMsg}${errorDetails ? ' - ' + errorDetails : ''}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    reset();
    setResult(null);
    setError(null);
  };

  return (
    <div className="verification-form">
      <h2>Individual Verification</h2>
      <p className="subtitle">Verify identity using BVN and NIN</p>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="bvn">Bank Verification Number (BVN) *</label>
            <input
              id="bvn"
              type="text"
              {...register('bvn')}
              placeholder="22123456789"
              maxLength={11}
              disabled={loading}
            />
            {errors.bvn && <span className="error">{errors.bvn.message}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="nin">National Identification Number (NIN) *</label>
            <input
              id="nin"
              type="text"
              {...register('nin')}
              placeholder="12345678901"
              maxLength={11}
              disabled={loading}
            />
            {errors.nin && <span className="error">{errors.nin.message}</span>}
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Verifying...' : 'Verify Identity'}
          </button>
          <button type="button" className="btn-secondary" onClick={handleReset} disabled={loading}>
            Reset
          </button>
        </div>
      </form>

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="result-card">
          <h3>Verification Result</h3>
          <div className="result-meta">
            <span className={`badge badge-${result.status.toLowerCase()}`}>
              {result.status}
            </span>
            <span className="verification-id">ID: {result.verification_id}</span>
          </div>

          {result.bvn_data && (
            <div className="result-section">
              <h4>BVN Verification</h4>
              <div className="verification-status">
                {result.bvn_data.verified ? '✓ Verified' : '✗ Not Verified'}
              </div>
              {result.bvn_data.full_name && (
                <p><strong>Name:</strong> {result.bvn_data.full_name}</p>
              )}
            </div>
          )}

          {result.nin_data && (
            <div className="result-section">
              <h4>NIN Verification</h4>
              <div className="verification-status">
                {result.nin_data.verified ? '✓ Verified' : '✗ Not Verified'}
              </div>
              {result.nin_data.full_name && (
                <p><strong>Name:</strong> {result.nin_data.full_name}</p>
              )}
            </div>
          )}

          {result.cross_validation && (
            <div className="result-section">
              <h4>Cross-Validation</h4>
              <div className={`validation-status ${result.cross_validation.passed ? 'passed' : 'failed'}`}>
                {result.cross_validation.passed ? '✓ Passed' : '✗ Failed'}
                <span className="confidence">Confidence: {result.cross_validation.confidence}%</span>
              </div>
              <p>{result.cross_validation.explanation}</p>
            </div>
          )}

          {result.risk_assessment && (
            <div className="result-section">
              <h4>Risk Assessment</h4>
              <div className={`risk-score risk-${result.risk_assessment.category.toLowerCase()}`}>
                <div className="score">{result.risk_assessment.score}/100</div>
                <div className="category">{result.risk_assessment.category}</div>
              </div>
              {result.risk_assessment.required_actions.length > 0 && (
                <div className="required-actions">
                  <strong>Required Actions:</strong>
                  <ul>
                    {result.risk_assessment.required_actions.map((action: string, i: number) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {result.report_url && (
            <div className="result-actions">
              <a
                href={apiClient.getReportUrl(result.verification_id)}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-outline"
              >
                View Report
              </a>
              <a
                href={apiClient.getPdfReportUrl(result.verification_id)}
                className="btn-outline"
                download
              >
                Download PDF
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
