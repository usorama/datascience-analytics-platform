import React from 'react';
import { BarChart, Card, Title } from '@tremor/react';

interface viz_7Props {
  data: any[];
  config: any;
}

export const viz_7: React.FC<viz_7Props> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>feature_0 by team</Title>
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