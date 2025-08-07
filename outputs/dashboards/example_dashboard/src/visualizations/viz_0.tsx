import React from 'react';
import { BarChart, Card, Title } from '@tremor/react';

interface viz_0Props {
  data: any[];
  config: any;
}

export const viz_0: React.FC<viz_0Props> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>Feature Importance</Title>
      <BarChart
        data={data}
        index="{viz_config['config'].get('x', 'category')}"
        categories={["feature"]}
        colors={["blue"]}
        className="h-80 mt-4"
      />
    </Card>
  );
};