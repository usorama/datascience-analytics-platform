import React from 'react';
import { Card, Title, Text, Badge, List, ListItem } from '@tremor/react';
import { useFilteredData } from '../hooks';
import { recommendations } from '../visualizations/recommendations';

interface DecisionsTabProps {
  data: any;
  filters: any;
  config: any;
}

export const DecisionsTab: React.FC<DecisionsTabProps> = ({ data, filters, config }) => {
  const predictions = useFilteredData(data.predictions || [], filters);
  
  // Categorize predictions
  const highValue = predictions.filter(p => p.value_score > 0.7);
  const mediumValue = predictions.filter(p => p.value_score > 0.3 && p.value_score <= 0.7);
  const lowValue = predictions.filter(p => p.value_score <= 0.3);
  
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <Grid numItems={1} numItemsSm={3} className="gap-6">
        <Card>
          <Title>High Value Items</Title>
          <Text className="text-3xl font-bold text-green-600">{highValue.length}</Text>
          <Text>Recommended for immediate attention</Text>
        </Card>
        
        <Card>
          <Title>Medium Value Items</Title>
          <Text className="text-3xl font-bold text-yellow-600">{mediumValue.length}</Text>
          <Text>Should be reviewed</Text>
        </Card>
        
        <Card>
          <Title>Low Value Items</Title>
          <Text className="text-3xl font-bold text-gray-600">{lowValue.length}</Text>
          <Text>Can be deprioritized</Text>
        </Card>
      </Grid>
      
      {/* QVF Framework Analysis */}
      <Card>
        <Title>Quantified Value Framework (QVF) Analysis</Title>
        <Text>Optimization recommendations based on capacity and value</Text>
        
        <div className="mt-4 space-y-4">
          <div>
            <Text className="font-semibold">PI Capacity Optimization:</Text>
            <List>
              <ListItem>
                <span>Total Capacity: {data.capacity?.total || 0} story points</span>
              </ListItem>
              <ListItem>
                <span>Allocated to High Value: {data.capacity?.high_value || 0} points</span>
              </ListItem>
              <ListItem>
                <span>Optimization Potential: {data.capacity?.optimization_potential || 0}%</span>
              </ListItem>
            </List>
          </div>
        </div>
      </Card>
      
      {/* Decision Visualizations */}
      <recommendations data={predictions} config={config} />
    </div>
  );
};