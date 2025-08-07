import { useEffect, useMemo } from 'react';
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
};