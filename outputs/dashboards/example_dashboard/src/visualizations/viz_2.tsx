import React from 'react';
import { LineChart, Card, Title } from '@tremor/react';

interface viz_2Props {
  data: any[];
  config: any;
}

export const viz_2: React.FC<viz_2Props> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>feature_0 Over Time</Title>
      <LineChart
        data={data}
        index="{viz_config['config'].get('x', 'date')}"
        categories={["feature_0"]}
        colors={["blue"]}
        className="h-80 mt-4"
        showLegend={true}
      />
    </Card>
  );
};