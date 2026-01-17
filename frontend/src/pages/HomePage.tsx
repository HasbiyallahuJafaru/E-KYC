/**
 * Home page with navigation
 */

import { Link } from 'react-router-dom';

export function HomePage() {
  return (
    <div className="home-page">
      <div className="hero">
        <h1>E-KYC Check</h1>
        <p className="tagline">FATF/CBN Compliant KYC Verification Platform</p>
        <p className="description">
          White-labeled verification API for Nigerian financial institutions.
          Powered by VerifyMe.ng with intelligent cross-validation and risk scoring.
        </p>
      </div>

      <div className="features">
        <div className="feature-card">
          <div className="feature-icon">👤</div>
          <h3>Individual Verification</h3>
          <p>BVN and NIN cross-validation with intelligent name matching</p>
          <Link to="/verify/individual" className="btn-primary">
            Verify Individual
          </Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🏢</div>
          <h3>Corporate Verification</h3>
          <p>CAC registry lookup with Ultimate Beneficial Owner analysis</p>
          <Link to="/verify/corporate" className="btn-primary">
            Verify Corporate
          </Link>
        </div>
      </div>

      <div className="info-section">
        <h2>Features</h2>
        <div className="info-grid">
          <div className="info-item">
            <h4>✓ FATF Compliant</h4>
            <p>Implements Recommendations 10-12 (KYC/CDD) and 24 (UBO ≥25%)</p>
          </div>
          <div className="info-item">
            <h4>✓ CBN Regulations 2022</h4>
            <p>Risk-based approach with transparent scoring</p>
          </div>
          <div className="info-item">
            <h4>✓ Cross-Validation</h4>
            <p>Intelligent name reconciliation between BVN and NIN</p>
          </div>
          <div className="info-item">
            <h4>✓ Print-Ready Reports</h4>
            <p>Branded HTML/PDF verification reports</p>
          </div>
        </div>
      </div>

      <div className="pricing-section">
        <h2>Pricing</h2>
        <div className="pricing-card">
          <div className="price">₦1,000</div>
          <div className="price-label">per verification</div>
          <p className="price-note">
            Flat rate for all verification types, billable regardless of success/failure
          </p>
        </div>
      </div>
    </div>
  );
}
