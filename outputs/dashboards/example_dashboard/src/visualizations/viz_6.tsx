import React from 'react';
import { BarChart, Card, Title } from '@tremor/react';

interface viz_6Props {
  data: any[];
  config: any;
}

export const viz_6: React.FC<viz_6Props> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>feature_1 by category</Title>
      <BarChart
        data={data}
        index="{viz_config['config'].get('x', 'category')}"
        categories={["feature_1"]}
        colors={["blue"]}
        className="h-80 mt-4"
      />
    </Card>
  );
};