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
  const [downloadingPdf, setDownloadingPdf] = useState(false);

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

  const handlePdfDownload = async () => {
    if (!result) return;
    
    setDownloadingPdf(true);
    setError(null);
    
    try {
      await apiClient.downloadPdfReport(result.verification_id);
    } catch (err: any) {
      console.error('PDF download error:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to download PDF';
      setError(`PDF Download Error: ${errorMsg}`);
    } finally {
      setDownloadingPdf(false);
    }
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
              {result.cac_data.entity_type && (
                <p><strong>Entity Type:</strong> {result.cac_data.entity_type}</p>
              )}
              {result.cac_data.status && (
                <p><strong>Status:</strong> {result.cac_data.status}</p>
              )}
              {result.cac_data.incorporation_date && (
                <p><strong>Incorporated:</strong> {result.cac_data.incorporation_date}</p>
              )}
              {result.cac_data.registered_address && (
                <p><strong>Registered Address:</strong> {result.cac_data.registered_address}</p>
              )}

              {/* Display Directors for LIMITED/PLC */}
              {result.cac_data.directors && result.cac_data.directors.length > 0 && (
                <div className="directors-list">
                  <h5>Directors</h5>
                  <div className="directors-table">
                    {result.cac_data.directors.map((director, i) => (
                      <div key={i} className="director-row">
                        <div className="director-info">
                          <div className="director-name">
                            {director.name} ({director.position})
                            {director.status && (
                              <span className={`status-badge status-${director.status.toLowerCase()}`}>
                                {director.status}
                              </span>
                            )}
                          </div>
                          {director.email && <div className="director-contact">📧 {director.email}</div>}
                          {director.phone && <div className="director-contact">📱 {director.phone}</div>}
                          {director.appointment_date && (
                            <div className="director-date">Appointed: {director.appointment_date}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Display Shareholders for LIMITED/PLC */}
              {result.cac_data.shareholders && result.cac_data.shareholders.length > 0 && (
                <div className="shareholders-list">
                  <h5>Shareholders</h5>
                  <div className="shareholders-table">
                    {result.cac_data.shareholders.map((shareholder, i) => (
                      <div key={i} className="shareholder-row">
                        <div className="shareholder-name">
                          {shareholder.name}
                          {shareholder.is_corporate && <span className="corporate-badge">Corporate</span>}
                        </div>
                        <div className="shareholder-percentage">
                          {shareholder.percentage.toFixed(1)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Display Proprietors for BUSINESS_NAME */}
              {result.cac_data.proprietors && result.cac_data.proprietors.length > 0 && (
                <div className="proprietors-list">
                  <h5>Proprietors</h5>
                  <div className="proprietors-table">
                    {result.cac_data.proprietors.map((proprietor, i) => (
                      <div key={i} className="proprietor-row">
                        <div className="proprietor-name">{proprietor.name}</div>
                        {proprietor.percentage && (
                          <div className="proprietor-percentage">{proprietor.percentage.toFixed(1)}%</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Display Trustees for NGO/INCORPORATED_TRUSTEES */}
              {result.cac_data.trustees && result.cac_data.trustees.length > 0 && (
                <div className="trustees-list">
                  <h5>Trustees</h5>
                  <div className="trustees-table">
                    {result.cac_data.trustees.map((trustee, i) => (
                      <div key={i} className="trustee-row">
                        <div className="trustee-name">{trustee.name}</div>
                        {trustee.appointment_date && (
                          <div className="trustee-date">Appointed: {trustee.appointment_date}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
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
                <div className="score">{result.risk_assessment.score}/30</div>
                <div className="category">{result.risk_assessment.category} RISK</div>
              </div>
              
              {/* Risk Breakdown */}
              {result.risk_assessment.breakdown && (
                <div className="risk-breakdown">
                  <h5>Risk Breakdown (Each category 0-5 points)</h5>
                  <div className="breakdown-grid">
                    {Object.entries(result.risk_assessment.breakdown).map(([key, value]) => (
                      <div key={key} className="breakdown-item">
                        <span className="breakdown-label">
                          {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        <span className="breakdown-value">{value}/5</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Risk Drivers */}
              {result.risk_assessment.risk_drivers && result.risk_assessment.risk_drivers.length > 0 && (
                <div className="risk-drivers">
                  <strong>Risk Drivers:</strong>
                  <ul>
                    {result.risk_assessment.risk_drivers.map((driver: string, i: number) => (
                      <li key={i}>{driver}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Required Actions */}
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
              <button
                onClick={handlePdfDownload}
                className="btn-outline"
                disabled={downloadingPdf}
              >
                {downloadingPdf ? 'Downloading...' : 'Download PDF'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
