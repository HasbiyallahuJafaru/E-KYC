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

export interface DirectorInfo {
  name: string;
  position: string;
  appointment_date?: string;
  status?: string;  // ACTIVE, REMOVED, RESIGNED
  email?: string;
  phone?: string;
  address?: string;
}

export interface ShareholderInfo {
  name: string;
  percentage: number;
  is_corporate: boolean;
  corporate_rc?: string;
}

export interface ProprietorInfo {
  name: string;
  percentage?: number;
  address?: string;
  nationality?: string;
}

export interface TrusteeInfo {
  name: string;
  appointment_date?: string;
  address?: string;
}

export interface CACData {
  verified: boolean;
  company_name?: string;
  entity_type?: 'LIMITED' | 'PLC' | 'BUSINESS_NAME' | 'NGO' | 'INCORPORATED_TRUSTEES';
  incorporation_date?: string;
  status?: string;
  registered_address?: string;
  
  // Fields for Limited Companies (Ltd/PLC)
  directors?: DirectorInfo[];
  shareholders?: ShareholderInfo[];
  share_capital?: number;
  company_email?: string;
  company_phone?: string;
  
  // Fields for Business Names
  proprietors?: ProprietorInfo[];
  business_commencement_date?: string;
  nature_of_business?: string;
  
  // Fields for NGOs/Incorporated Trustees
  trustees?: TrusteeInfo[];
  aims_and_objectives?: string;
  
  // Common optional fields
  city?: string;
  state?: string;
  lga?: string;
  postal_code?: string;
  branch_address?: string;
  
  // UBO analysis (computed)
  ubo_count?: number;
  ubos?: UBOInfo[];
}

export interface RiskAssessment {
  score: number;  // 1-30 scale
  category: 'LOW' | 'MEDIUM' | 'HIGH';
  breakdown: Record<string, number>;  // Each category 0-5 points
  risk_drivers: string[];
  required_actions: string[];
  calculation_sheet?: string[];  // Human-readable breakdown
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
