/**
 * Individual verification page
 */

import { IndividualVerificationForm } from '@/components/IndividualVerificationForm';

export function IndividualVerificationPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <a href="/" className="back-link">← Back to Home</a>
      </div>
      <IndividualVerificationForm />
    </div>
  );
}
