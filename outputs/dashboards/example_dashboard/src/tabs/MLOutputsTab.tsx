import React from 'react';
import { Grid, Card, Title, Text } from '@tremor/react';
import { useDashboardStore } from '../store';
import { model_performance } from '../visualizations/model_performance';

interface MLOutputsTabProps {
  data: any;
  filters: any;
  config: any;
}

export const MLOutputsTab: React.FC<MLOutputsTabProps> = ({ data, filters, config }) => {
  const { mlOutputs } = useDashboardStore();
  
  return (
    <div className="space-y-6">
      {/* Optimization Status */}
      <Card>
        <Title>ML Optimization Status</Title>
        <Text>Iterations: {config.optimization_status?.iterations || 0}</Text>
        <Text>Performance: {(config.optimization_status?.performance || 0).toFixed(4)}</Text>
        <Text>Status: {config.optimization_status?.converged ? 'Converged ✓' : 'In Progress...'}</Text>
      </Card>
      
      {/* ML Visualizations */}
      <Grid numItems={1} numItemsLg={2} className="gap-6">
        <model_performance data={mlOutputs} config={config} />
      </Grid>
    </div>
  );
};