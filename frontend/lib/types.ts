/**
 * TypeScript Type Definitions
 * Shared types for the CALIDUS application
 */

// User Types
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'engineer' | 'viewer';
  is_active: boolean;
  full_name?: string;
  created_at: string;
}

// Requirement Types
export type RequirementType = 'Aircraft_High_Level_Requirement' | 'System_Requirement' | 'Technical_Specification' | 'Certification_Requirement';
export type RequirementStatus = 'draft' | 'approved' | 'deprecated' | 'under_review';
export type RequirementPriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFORMATIONAL';
export type VerificationMethod = 'TEST' | 'ANALYSIS' | 'DEMONSTRATION' | 'INSPECTION';

export interface Requirement {
  id: number;
  requirement_id: string;
  type: RequirementType;
  category?: string;
  title: string;
  description: string;
  priority: RequirementPriority;
  status: RequirementStatus;
  verification_method?: VerificationMethod;
  regulatory_document?: string;
  regulatory_section?: string;
  regulatory_page?: number;
  file_path?: string;
  version: string;
  revision_notes?: string;
  created_by_id: number;
  created_at: string;
  updated_at?: string;
  test_case_count?: number;
  parent_trace_count?: number;
  child_trace_count?: number;
}

// Test Case Types
export type TestCaseStatus = 'pending' | 'passed' | 'failed' | 'blocked' | 'in_progress';
export type TestCasePriority = 'Critical' | 'High' | 'Medium' | 'Low';

export interface TestCase {
  id: number;
  test_case_id: string;
  title: string;
  description?: string;
  test_steps: string;
  expected_results: string;
  actual_results?: string;
  status: TestCaseStatus;
  priority: TestCasePriority;
  execution_date?: string;
  execution_duration?: number;
  executed_by?: string;
  test_type?: string;
  test_environment?: string;
  automated: boolean;
  automation_script?: string;
  requirement_id: number;
  created_by_id: number;
  created_at: string;
  updated_at?: string;
  requirement_title?: string;
  requirement_id_str?: string;
}

// Traceability Types
export type TraceLinkType = 'derives_from' | 'satisfies' | 'verifies' | 'depends_on' | 'refines' | 'conflicts_with';

export interface TraceabilityLink {
  id: number;
  source_id: number;
  target_id: number;
  link_type: TraceLinkType;
  description?: string;
  rationale?: string;
  created_by_id: number;
  created_at: string;
  updated_at?: string;
  source_requirement_id?: string;
  source_title?: string;
  target_requirement_id?: string;
  target_title?: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface RequirementsListResponse {
  total: number;
  page: number;
  page_size: number;
  requirements: Requirement[];
}

export interface TestCasesListResponse {
  total: number;
  page: number;
  page_size: number;
  test_cases: TestCase[];
}

export interface RequirementStats {
  total_requirements: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  total_with_tests: number;
  total_with_traces: number;
  coverage_percentage: number;
}

export interface TestCaseStats {
  total_test_cases: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  total_automated: number;
  total_manual: number;
  pass_rate: number;
  avg_execution_duration?: number;
}

export interface TraceabilityReport {
  total_requirements: number;
  total_trace_links: number;
  total_test_cases: number;
  requirements_with_parents: number;
  requirements_with_children: number;
  requirements_with_tests: number;
  orphaned_requirements: number;
  traceability_gaps: TraceabilityGap[];
  by_type: Record<string, number>;
  traceability_score: number;
  test_coverage_score: number;
}

export interface TraceabilityGap {
  requirement_id: number;
  requirement_identifier: string;
  title: string;
  type: string;
  gap_type: 'missing_parent' | 'missing_child' | 'missing_test' | 'orphan';
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
}

// Filter Types
export interface RequirementFilter {
  type?: RequirementType;
  category?: string;
  status?: RequirementStatus;
  priority?: RequirementPriority;
  search?: string;
  regulatory_document?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface TestCaseFilter {
  status?: TestCaseStatus;
  priority?: TestCasePriority;
  requirement_id?: number;
  automated?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface UserFilter {
  role?: string;
  is_active?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

// Compliance Types
export interface ComplianceMetrics {
  total_requirements: number;
  mapped_requirements: number;
  unmapped_requirements: number;
  coverage_percentage: number;
  total_regulations: number;
}

export interface RegulationCoverage {
  regulation: string;
  authority: string;
  total_requirements: number;
  by_type: Record<string, number>;
  by_priority: Record<string, number>;
  coverage_percentage: number;
}

export interface ComplianceOverview {
  metrics: ComplianceMetrics;
  by_regulation: RegulationCoverage[];
  top_regulations: Array<{
    regulation: string;
    authority: string;
    count: number;
    coverage: number;
  }>;
}

export interface RegulationResponse {
  name: string;
  abbreviation: string;
  authority: string;
  description?: string;
  total_requirements: number;
  coverage_percentage: number;
  total_sections: number;
  covered_sections: number;
}

export interface RegulationSection {
  section: string;
  title?: string;
  requirement_count: number;
  requirements: Array<{
    id: number;
    requirement_id: string;
    title: string;
    type: string;
    status: string;
    priority: string;
    page?: number;
  }>;
}

export interface RegulationDetail {
  regulation: string;
  authority: string;
  description?: string;
  total_requirements: number;
  total_sections: number;
  sections: RegulationSection[];
  coverage_percentage: number;
}

export interface ComplianceGap {
  gap_type: string;
  requirement_id?: string;
  requirement_title?: string;
  requirement_type?: string;
  priority?: string;
  regulation?: string;
  section?: string;
  severity: string;
  description: string;
}

export interface ComplianceStats {
  total_requirements: number;
  mapped_requirements: number;
  unmapped_requirements: number;
  coverage_percentage: number;
  regulations_count: number;
  sections_count: number;
  by_regulation: Record<string, number>;
  by_authority: Record<string, number>;
}
