import React from 'react';
import { BarChart, Card, Title } from '@tremor/react';

interface viz_5Props {
  data: any[];
  config: any;
}

export const viz_5: React.FC<viz_5Props> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>feature_0 by category</Title>
      <BarChart
        data={data}
        index="{viz_config['config'].get('x', 'category')}"
        categories={["feature_0"]}
        colors={["blue"]}
        className="h-80 mt-4"
      />
    </Card>
  );
};