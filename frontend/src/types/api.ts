/**
 * TypeScript types matching backend API schemas
 */

export interface IndividualVerificationRequest {
  bvn: string;
  nin: string;
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  phone_number?: string;
}

export interface CorporateVerificationRequest {
  rc_number: string;
  business_name?: string;
  expected_ubo_count?: number;
}

export interface CompleteVerificationRequest {
  bvn: string;
  nin: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  rc_number?: string;
  business_name?: string;
  occupation?: string;
  industry_sector?: string;
  is_pep?: boolean;
  nationality?: string;
}

export interface BVNData {
  verified: boolean;
  full_name?: string;
  date_of_birth?: string;
  phone_number?: string;
}

export interface NINData {
  verified: boolean;
  full_name?: string;
  date_of_birth?: string;
  address?: string;
}

export interface CrossValidationData {
  passed: boolean;
  confidence: number;
  issues: string[];
  explanation: string;
}

export interface UBOInfo {
  name: string;
  ownership_percentage: number;
  ownership_type: string;
  is_verified: boolean;
}

export interface CACData {
  verified: boolean;
  company_name?: string;
  incorporation_date?: string;
  status?: string;
  ubo_count?: number;
  ubos?: UBOInfo[];
}

export interface RiskAssessment {
  score: number;
  category: 'LOW' | 'MEDIUM' | 'HIGH' | 'PROHIBITED';
  breakdown: Record<string, number>;
  risk_drivers: string[];
  required_actions: string[];
}

export interface VerificationResponse {
  verification_id: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  verification_type: 'INDIVIDUAL' | 'CORPORATE' | 'COMPLETE';
  bvn_data?: BVNData;
  nin_data?: NINData;
  cross_validation?: CrossValidationData;
  cac_data?: CACData;
  risk_assessment?: RiskAssessment;
  report_url?: string;
  processing_time_ms?: number;
  created_at: string;
  error_code?: string;
  error_message?: string;
}

export interface ErrorResponse {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}
