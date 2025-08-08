/**
 * TypeScript type definitions for QVF Admin Interface
 * 
 * Defines all data types and interfaces used throughout the QVF admin system.
 * These types match the Pydantic models from the backend.
 */

// Core QVF Types
export interface QVFCriterion {
  criterion_id: string;
  name: string;
  description: string;
  category: CriteriaCategory;
  weight: number;
  global_weight: number;
  importance_rank: number;
  data_source: string;
  data_type: 'numeric' | 'categorical' | 'boolean' | 'text';
  higher_is_better: boolean;
  normalization_method: 'minmax' | 'zscore' | 'percentile' | 'none';
  value_mapping?: Record<string, number>;
  threshold_min?: number;
  threshold_max?: number;
  financial_multiplier?: number;
  cost_of_delay?: number;
  revenue_impact?: number;
  scoring_function: 'linear' | 'logarithmic' | 'exponential' | 'step';
  diminishing_returns: boolean;
  confidence_factor: number;
  is_active: boolean;
  requires_manual_input: boolean;
  stakeholder_input_type?: string;
  data_quality_threshold: number;
  validation_rules: string[];
}

export type CriteriaCategory = 
  | 'business_value'
  | 'strategic_alignment' 
  | 'customer_value'
  | 'implementation_complexity'
  | 'risk_assessment';

export interface CriteriaWeights {
  business_value: number;
  strategic_alignment: number;
  customer_value: number;
  implementation_complexity: number;
  risk_assessment: number;
}

export interface QVFConfiguration {
  configuration_id: string;
  name: string;
  description?: string;
  criteria: QVFCriterion[];
  category_weights: CriteriaWeights;
  consistency_threshold: number;
  use_geometric_mean: boolean;
  enable_sensitivity_analysis: boolean;
  require_all_criteria: boolean;
  min_data_quality: number;
  allow_partial_scoring: boolean;
  max_calculation_time_seconds: number;
  batch_size: number;
  enable_parallel_processing: boolean;
  enable_financial_modeling: boolean;
  discount_rate: number;
  time_horizon_years: number;
  created_date: string;
  last_modified: string;
  version: string;
  created_by?: string;
  validation?: ValidationResult;
}

export interface ConfigurationSummary {
  configuration_id: string;
  name: string;
  description?: string;
  created_date: string;
  last_modified: string;
  criteria_count: number;
  is_valid: boolean;
}

// Validation Types
export interface ValidationResult {
  is_valid: boolean;
  issues: string[];
  normalized_weights?: Record<string, number>;
  suggestions: string[];
}

// API Request/Response Types
export interface ConfigurationCreateRequest {
  name: string;
  description?: string;
  criteria?: Partial<QVFCriterion>[];
  category_weights?: Partial<CriteriaWeights>;
  preset_type?: 'agile' | 'enterprise' | 'startup';
}

export interface ConfigurationUpdateRequest {
  name?: string;
  description?: string;
  criteria?: Partial<QVFCriterion>[];
  category_weights?: Partial<CriteriaWeights>;
}

export interface WeightValidationRequest {
  category_weights: Record<string, number>;
  criteria_weights?: Record<string, Record<string, number>>;
}

// UI State Types
export interface AdminUIState {
  configurations: ConfigurationSummary[];
  selectedConfiguration: QVFConfiguration | null;
  isLoading: boolean;
  error: string | null;
  validationResults: ValidationResult | null;
  presets: PresetInfo[];
}

export interface PresetInfo {
  id: string;
  name: string;
  description: string;
  category_weights: CriteriaWeights;
}

// Form Types
export interface WeightEditorProps {
  weights: CriteriaWeights;
  onChange: (weights: CriteriaWeights) => void;
  onValidation?: (result: ValidationResult) => void;
  disabled?: boolean;
}

export interface CriterionEditorProps {
  criterion: QVFCriterion;
  onChange: (criterion: QVFCriterion) => void;
  onDelete?: (criterionId: string) => void;
  categories: CriteriaCategory[];
}

export interface ConfigurationFormProps {
  configuration?: QVFConfiguration;
  onSave: (config: ConfigurationCreateRequest | ConfigurationUpdateRequest) => Promise<void>;
  onCancel: () => void;
  isEditing?: boolean;
}

// Validation Hook Types
export interface UseValidationOptions {
  realTime?: boolean;
  debounceMs?: number;
}

export interface UseValidationReturn {
  validate: (data: any) => Promise<ValidationResult>;
  isValidating: boolean;
  lastResult: ValidationResult | null;
}

// Component Props Types
export interface AdminDashboardProps {
  className?: string;
}

export interface ConfigurationListProps {
  configurations: ConfigurationSummary[];
  onSelect: (configId: string) => void;
  onDelete: (configId: string) => void;
  onExport: (configId: string) => void;
  selectedId?: string;
}

export interface WeightSliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  showPercentage?: boolean;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
}

export interface ValidationIndicatorProps {
  result: ValidationResult | null;
  isValidating?: boolean;
  compact?: boolean;
}

// Utility Types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncOperation<T = any> {
  state: LoadingState;
  data?: T;
  error?: string;
}

export interface ToastNotification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

// Category Configuration
export const CATEGORY_INFO: Record<CriteriaCategory, {
  name: string;
  description: string;
  color: string;
  icon: string;
}> = {
  business_value: {
    name: 'Business Value',
    description: 'Direct business impact and value creation',
    color: 'blue',
    icon: 'TrendingUpIcon'
  },
  strategic_alignment: {
    name: 'Strategic Alignment',
    description: 'Alignment with organizational strategy and goals',
    color: 'purple',
    icon: 'TargetIcon'
  },
  customer_value: {
    name: 'Customer Value',
    description: 'Impact on customer satisfaction and experience',
    color: 'green',
    icon: 'UserGroupIcon'
  },
  implementation_complexity: {
    name: 'Implementation Complexity',
    description: 'Technical and resource complexity of implementation',
    color: 'yellow',
    icon: 'CogIcon'
  },
  risk_assessment: {
    name: 'Risk Assessment',
    description: 'Implementation and business risks',
    color: 'red',
    icon: 'ShieldExclamationIcon'
  }
};

// Default Values
export const DEFAULT_CRITERION: Partial<QVFCriterion> = {
  weight: 0.2,
  importance_rank: 10,
  data_type: 'numeric',
  higher_is_better: true,
  normalization_method: 'minmax',
  scoring_function: 'linear',
  diminishing_returns: false,
  confidence_factor: 1.0,
  is_active: true,
  requires_manual_input: false,
  data_quality_threshold: 0.5,
  validation_rules: []
};

export const DEFAULT_CATEGORY_WEIGHTS: CriteriaWeights = {
  business_value: 0.25,
  strategic_alignment: 0.25,
  customer_value: 0.20,
  implementation_complexity: 0.15,
  risk_assessment: 0.15
};