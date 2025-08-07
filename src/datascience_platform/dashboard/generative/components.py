"""Component Generation for TypeScript/React Dashboard

This module generates TypeScript/React components based on data analysis
and ML outputs.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from .analyzer import ChartType, ColumnAnalysis, DataType


@dataclass
class ComponentSpec:
    """Specification for a generated component."""
    name: str
    type: str  # 'chart', 'filter', 'kpi', 'table'
    props: Dict[str, Any]
    data_binding: Dict[str, str]
    imports: List[str]
    dependencies: List[str]


class FilterType(Enum):
    """Types of filter components."""
    DROPDOWN = "dropdown"
    MULTI_SELECT = "multiselect"
    RANGE_SLIDER = "range"
    DATE_RANGE = "daterange"
    SEARCH = "search"
    TOGGLE = "toggle"


class ComponentGenerator:
    """Generates TypeScript/React components."""
    
    def __init__(self, use_tremor: bool = True):
        """
        Initialize component generator.
        
        Args:
            use_tremor: Whether to use Tremor components (recommended)
        """
        self.use_tremor = use_tremor
        self.component_library = "tremor" if use_tremor else "recharts"
        
    def generate_dashboard_scaffold(
        self,
        dashboard_config: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate the main dashboard scaffold."""
        components = {}
        
        # Main dashboard component
        components['Dashboard.tsx'] = self._generate_main_dashboard(dashboard_config)
        
        # Layout components
        components['Layout.tsx'] = self._generate_layout()
        components['FilterPanel.tsx'] = self._generate_filter_panel()
        components['TabContainer.tsx'] = self._generate_tab_container()
        
        # Utility files
        components['types.ts'] = self._generate_types()
        components['hooks.ts'] = self._generate_hooks()
        components['store.ts'] = self._generate_store()
        components['utils.ts'] = self._generate_utils()
        
        return components
    
    def _generate_main_dashboard(self, config: Dict[str, Any]) -> str:
        """Generate the main dashboard component."""
        return f"""import React from 'react';
import {{ Card, Grid, Title, Text }} from '@tremor/react';
import {{ Layout }} from './Layout';
import {{ TabContainer }} from './TabContainer';
import {{ useDashboardStore }} from './store';
import {{ DashboardConfig }} from './types';

interface DashboardProps {{
  config: DashboardConfig;
  data: any;
}}

export const Dashboard: React.FC<DashboardProps> = ({{ config, data }}) => {{
  const {{ filters, setFilter }} = useDashboardStore();
  
  return (
    <Layout>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="px-4 py-4 sm:px-6 lg:px-8">
            <Title>{{config.title || 'Analytics Dashboard'}}</Title>
            <Text>{{config.description || 'ML-powered insights and analytics'}}</Text>
          </div>
        </header>
        
        <TabContainer 
          data={{data}}
          filters={{filters}}
          config={{config}}
        />
      </div>
    </Layout>
  );
}};

export default Dashboard;"""
    
    def _generate_layout(self) -> str:
        """Generate the layout component with left filter panel."""
        return """import React, { ReactNode } from 'react';
import { FilterPanel } from './FilterPanel';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Filter Panel - Fixed */}
      <aside className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
        <FilterPanel />
      </aside>
      
      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
};"""
    
    def _generate_filter_panel(self) -> str:
        """Generate the filter panel component."""
        return """import React from 'react';
import { 
  Select, 
  SelectItem, 
  MultiSelect, 
  MultiSelectItem,
  DateRangePicker,
  SearchSelect,
  SearchSelectItem,
  Text,
  Divider
} from '@tremor/react';
import { useDashboardStore } from './store';
import { FilterConfig } from './types';

export const FilterPanel: React.FC = () => {
  const { filters, setFilter, filterConfigs, resetFilters } = useDashboardStore();
  
  const renderFilter = (config: FilterConfig) => {
    const value = filters[config.field] || config.defaultValue;
    
    switch (config.type) {
      case 'dropdown':
        return (
          <Select
            value={value}
            onValueChange={(val) => setFilter(config.field, val)}
            placeholder={config.placeholder}
          >
            <SelectItem value="all">All</SelectItem>
            {config.options?.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </Select>
        );
      
      case 'multiselect':
        return (
          <MultiSelect
            value={value || []}
            onValueChange={(val) => setFilter(config.field, val)}
            placeholder={config.placeholder}
          >
            {config.options?.map((opt) => (
              <MultiSelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </MultiSelectItem>
            ))}
          </MultiSelect>
        );
      
      case 'daterange':
        return (
          <DateRangePicker
            value={value}
            onValueChange={(val) => setFilter(config.field, val)}
            placeholder={config.placeholder}
            enableYearNavigation
          />
        );
      
      case 'search':
        return (
          <SearchSelect
            value={value}
            onValueChange={(val) => setFilter(config.field, val)}
            placeholder={config.placeholder}
          >
            <SearchSelectItem value="all">All</SearchSelectItem>
            {config.options?.map((opt) => (
              <SearchSelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SearchSelectItem>
            ))}
          </SearchSelect>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Filters</h2>
        <button
          onClick={resetFilters}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Reset All
        </button>
      </div>
      
      {filterConfigs.map((config, index) => (
        <div key={config.field}>
          <Text className="mb-2">{config.label}</Text>
          {renderFilter(config)}
          {index < filterConfigs.length - 1 && <Divider className="my-4" />}
        </div>
      ))}
    </div>
  );
};"""
    
    def _generate_tab_container(self) -> str:
        """Generate the tab container with three tabs."""
        return """import React, { useState } from 'react';
import { Tab, TabGroup, TabList, TabPanel, TabPanels } from '@tremor/react';
import { AnalyticsTab } from './tabs/AnalyticsTab';
import { MLOutputsTab } from './tabs/MLOutputsTab';
import { DecisionsTab } from './tabs/DecisionsTab';

interface TabContainerProps {
  data: any;
  filters: any;
  config: any;
}

export const TabContainer: React.FC<TabContainerProps> = ({ data, filters, config }) => {
  const [selectedTab, setSelectedTab] = useState(0);
  
  return (
    <div className="p-6">
      <TabGroup index={selectedTab} onIndexChange={setSelectedTab}>
        <TabList variant="solid">
          <Tab icon={() => <span>📊</span>}>Analytics</Tab>
          <Tab icon={() => <span>🤖</span>}>ML Outputs</Tab>
          <Tab icon={() => <span>🎯</span>}>Decisions & Predictions</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            <AnalyticsTab data={data} filters={filters} config={config} />
          </TabPanel>
          
          <TabPanel>
            <MLOutputsTab data={data} filters={filters} config={config} />
          </TabPanel>
          
          <TabPanel>
            <DecisionsTab data={data} filters={filters} config={config} />
          </TabPanel>
        </TabPanels>
      </TabGroup>
    </div>
  );
};"""
    
    def _generate_types(self) -> str:
        """Generate TypeScript type definitions."""
        return """// Type definitions for the dashboard

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
}"""
    
    def _generate_hooks(self) -> str:
        """Generate custom React hooks."""
        return """import { useEffect, useMemo } from 'react';
import { useDashboardStore } from './store';

// Custom hook for filtered data
export const useFilteredData = (data: any[], filters: Record<string, any>) => {
  return useMemo(() => {
    if (!data || data.length === 0) return data;
    
    return data.filter(item => {
      for (const [field, filterValue] of Object.entries(filters)) {
        if (!filterValue || filterValue === 'all') continue;
        
        if (Array.isArray(filterValue)) {
          // Multi-select filter
          if (!filterValue.includes(item[field])) return false;
        } else if (typeof filterValue === 'object' && 'from' in filterValue) {
          // Date range filter
          const itemDate = new Date(item[field]);
          const { from, to } = filterValue;
          if (itemDate < from || itemDate > to) return false;
        } else {
          // Single value filter
          if (item[field] !== filterValue) return false;
        }
      }
      return true;
    });
  }, [data, filters]);
};

// Custom hook for chart data preparation
export const useChartData = (
  data: any[], 
  xField: string, 
  yField: string,
  aggregation: 'sum' | 'avg' | 'count' = 'sum'
) => {
  return useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // Group by x field
    const grouped = data.reduce((acc, item) => {
      const key = item[xField];
      if (!acc[key]) acc[key] = [];
      acc[key].push(item[yField]);
      return acc;
    }, {} as Record<string, number[]>);
    
    // Aggregate
    return Object.entries(grouped).map(([key, values]) => {
      let value: number;
      switch (aggregation) {
        case 'sum':
          value = values.reduce((a, b) => a + b, 0);
          break;
        case 'avg':
          value = values.reduce((a, b) => a + b, 0) / values.length;
          break;
        case 'count':
          value = values.length;
          break;
      }
      
      return { [xField]: key, [yField]: value };
    });
  }, [data, xField, yField, aggregation]);
};

// Custom hook for responsive chart dimensions
export const useChartDimensions = (containerRef: React.RefObject<HTMLDivElement>) => {
  const [dimensions, setDimensions] = React.useState({ width: 800, height: 400 });
  
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width } = containerRef.current.getBoundingClientRect();
        setDimensions({ width: width - 40, height: Math.min(400, width * 0.5) });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [containerRef]);
  
  return dimensions;
};"""
    
    def _generate_store(self) -> str:
        """Generate Zustand store for state management."""
        return """import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { FilterConfig } from './types';

interface DashboardStore {
  // Filter state
  filters: Record<string, any>;
  filterConfigs: FilterConfig[];
  setFilter: (field: string, value: any) => void;
  setFilterConfigs: (configs: FilterConfig[]) => void;
  resetFilters: () => void;
  
  // UI state
  selectedTab: number;
  setSelectedTab: (tab: number) => void;
  
  // Data state
  rawData: any;
  setRawData: (data: any) => void;
  
  // ML outputs
  mlOutputs: any;
  setMLOutputs: (outputs: any) => void;
}

export const useDashboardStore = create<DashboardStore>()(
  persist(
    (set) => ({
      // Filter state
      filters: {},
      filterConfigs: [],
      setFilter: (field, value) => 
        set((state) => ({ 
          filters: { ...state.filters, [field]: value } 
        })),
      setFilterConfigs: (configs) => set({ filterConfigs: configs }),
      resetFilters: () => set({ filters: {} }),
      
      // UI state
      selectedTab: 0,
      setSelectedTab: (tab) => set({ selectedTab: tab }),
      
      // Data state
      rawData: null,
      setRawData: (data) => set({ rawData: data }),
      
      // ML outputs
      mlOutputs: null,
      setMLOutputs: (outputs) => set({ mlOutputs: outputs }),
    }),
    {
      name: 'dashboard-store',
      partialize: (state) => ({ 
        filters: state.filters,
        selectedTab: state.selectedTab 
      }),
    }
  )
);"""
    
    def _generate_utils(self) -> str:
        """Generate utility functions."""
        return """// Utility functions for the dashboard

export const formatNumber = (value: number, decimals: number = 2): string => {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(decimals)}M`;
  } else if (value >= 1000) {
    return `${(value / 1000).toFixed(decimals)}K`;
  }
  return value.toFixed(decimals);
};

export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

export const formatDate = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
};

export const getColorScale = (theme: 'blue' | 'green' | 'red' = 'blue') => {
  const scales = {
    blue: ['#EFF6FF', '#DBEAFE', '#BFDBFE', '#93C5FD', '#60A5FA', '#3B82F6'],
    green: ['#F0FDF4', '#DCFCE7', '#BBF7D0', '#86EFAC', '#4ADE80', '#22C55E'],
    red: ['#FEF2F2', '#FEE2E2', '#FECACA', '#FCA5A5', '#F87171', '#EF4444']
  };
  return scales[theme];
};

export const downloadData = (data: any[], filename: string = 'data.csv') => {
  // Convert to CSV
  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map(row => headers.map(h => row[h]).join(','))
  ].join('\\n');
  
  // Create download link
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
};"""


class FilterGenerator:
    """Generates filter configurations from data analysis."""
    
    def generate_filter_configs(
        self,
        column_analyses: Dict[str, ColumnAnalysis]
    ) -> List[Dict[str, Any]]:
        """Generate filter configurations based on data analysis."""
        filter_configs = []
        
        for col_name, analysis in column_analyses.items():
            if not analysis.is_filterable:
                continue
            
            filter_config = {
                'field': col_name,
                'label': self._humanize_field_name(col_name),
                'type': analysis.filter_type,
                'placeholder': f'Select {self._humanize_field_name(col_name)}',
                'defaultValue': 'all' if analysis.filter_type in ['dropdown', 'search'] else None
            }
            
            # Add options for categorical filters
            if analysis.value_distribution and len(analysis.value_distribution) <= 50:
                filter_config['options'] = [
                    {'label': str(val), 'value': val}
                    for val in sorted(analysis.value_distribution.keys())
                ]
            
            filter_configs.append(filter_config)
        
        # Sort by priority
        priority_order = ['dropdown', 'multiselect', 'daterange', 'range', 'search']
        filter_configs.sort(key=lambda x: priority_order.index(x['type']))
        
        return filter_configs[:10]  # Limit to 10 filters
    
    def _humanize_field_name(self, field_name: str) -> str:
        """Convert field name to human-readable format."""
        # Handle common patterns
        replacements = {
            '_': ' ',
            'id': 'ID',
            'okr': 'OKR',
            'kpi': 'KPI',
            'roi': 'ROI'
        }
        
        result = field_name
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        # Title case
        return result.title()