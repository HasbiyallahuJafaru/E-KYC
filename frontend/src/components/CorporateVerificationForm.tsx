/**
 * Corporate verification form component
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { apiClient } from '@/services/api';
import type { VerificationResponse, UBOInfo } from '@/types/api';
import './VerificationForm.css';

const schema = z.object({
  rc_number: z.string().min(5, 'RC/BN number must be at least 5 characters'),
});

type FormData = z.infer<typeof schema>;

export function CorporateVerificationForm() {
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
      console.log('Submitting corporate verification:', data);
      const response = await apiClient.verifyCorporate(data);
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
      <h2>Corporate Verification</h2>
      <p className="subtitle">Verify corporate entity and identify beneficial owners</p>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="rc_number">CAC Registration Number (RC/BN) *</label>
            <input
              id="rc_number"
              type="text"
              {...register('rc_number')}
              placeholder="RC123456 or BN123456"
              disabled={loading}
            />
            {errors.rc_number && <span className="error">{errors.rc_number.message}</span>}
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Verifying...' : 'Verify Company'}
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

          {result.cac_data && (
            <div className="result-section">
              <h4>CAC Verification</h4>
              <div className="verification-status">
                {result.cac_data.verified ? '✓ Verified' : '✗ Not Verified'}
              </div>
              {result.cac_data.company_name && (
                <p><strong>Company Name:</strong> {result.cac_data.company_name}</p>
              )}
              {result.cac_data.status && (
                <p><strong>Status:</strong> {result.cac_data.status}</p>
              )}
              {result.cac_data.incorporation_date && (
                <p><strong>Incorporated:</strong> {result.cac_data.incorporation_date}</p>
              )}

              {result.cac_data.ubos && result.cac_data.ubos.length > 0 && (
                <div className="ubos-list">
                  <h5>Ultimate Beneficial Owners (≥25% ownership)</h5>
                  <div className="ubos-table">
                    {result.cac_data.ubos.map((ubo: UBOInfo, i: number) => (
                      <div key={i} className="ubo-row">
                        <div className="ubo-name">
                          {ubo.name}
                          {ubo.is_verified && <span className="verified-badge">✓</span>}
                        </div>
                        <div className="ubo-ownership">
                          {ubo.ownership_percentage.toFixed(1)}% ({ubo.ownership_type})
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
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
