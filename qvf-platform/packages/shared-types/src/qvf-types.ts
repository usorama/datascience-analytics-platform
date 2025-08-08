// Core QVF Types
export interface QVFScore {
  id: number;
  title: string;
  qvf_score: number;
  quality_score: number;
  value_score: number;
  framework_alignment: number;
}

export interface WorkItem {
  id: number;
  title: string;
  state: string;
  work_item_type: string;
  assigned_to?: string;
  story_points?: number;
  priority?: number;
  tags: string[];
  created_date?: string;
  modified_date?: string;
}

export interface WorkItemsResponse {
  items: WorkItem[];
  total_count: number;
  page: number;
  page_size: number;
}

export interface QVFScoreRequest {
  work_items: WorkItem[];
  criteria_weights: Record<string, number>;
}

export interface QVFScoreResponse {
  scores: QVFScore[];
  summary: QVFScoreSummary;
}

export interface QVFScoreSummary {
  total_items: number;
  average_score: number;
  high_priority_count: number;
  medium_priority_count: number;
  low_priority_count: number;
}

// Authentication Types
export interface User {
  username: string;
  email: string;
  roles?: string[];
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

// Dashboard Types
export interface DashboardMetric {
  label: string;
  value: number | string;
  change?: number;
  trend?: 'up' | 'down' | 'stable';
}

export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string;
  borderColor?: string;
}

// Configuration Types
export interface QVFCriteria {
  quality_criteria: string[];
  value_criteria: string[];
}

export interface TeamConfiguration {
  team_id: string;
  team_name: string;
  criteria_weights: Record<string, number>;
  thresholds: {
    high_priority: number;
    medium_priority: number;
  };
}