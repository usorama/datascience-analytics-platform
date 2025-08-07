// Type definitions for the dashboard

export interface DashboardConfig {
  title: string;
  description: string;
  filters: FilterConfig[];
  visualizations: VisualizationConfig[];
  theme?: 'light' | 'dark';
}

export interface FilterConfig {
  field: string;
  label: string;
  type: 'dropdown' | 'multiselect' | 'daterange' | 'search' | 'range';
  placeholder?: string;
  defaultValue?: any;
  options?: FilterOption[];
}

export interface FilterOption {
  label: string;
  value: string | number;
}

export interface VisualizationConfig {
  id: string;
  type: ChartType;
  title: string;
  description?: string;
  dataColumns: string[];
  config: any;
  tab: 'analytics' | 'ml' | 'decisions';
}

export type ChartType = 
  | 'bar'
  | 'line'
  | 'scatter'
  | 'pie'
  | 'heatmap'
  | 'treemap'
  | 'kpi'
  | 'table';

export interface MLOutput {
  predictions: Prediction[];
  feature_importance: FeatureImportance[];
  model_performance: ModelPerformance;
  optimization_history: OptimizationPoint[];
}

export interface Prediction {
  id: string | number;
  value: number;
  confidence: number;
  category: string;
  recommendation: string;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
  category?: string;
}

export interface ModelPerformance {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix?: number[][];
}

export interface OptimizationPoint {
  iteration: number;
  score: number;
  component: string;
  improvement: number;
}