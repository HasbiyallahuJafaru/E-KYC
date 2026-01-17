/**
 * Corporate verification page
 */

import { CorporateVerificationForm } from '@/components/CorporateVerificationForm';

export function CorporateVerificationPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <a href="/" className="back-link">← Back to Home</a>
      </div>
      <CorporateVerificationForm />
    </div>
  );
}
