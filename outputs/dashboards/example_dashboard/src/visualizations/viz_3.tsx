import React from 'react';
import { LineChart, Card, Title } from '@tremor/react';

interface viz_3Props {
  data: any[];
  config: any;
}

export const viz_3: React.FC<viz_3Props> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>feature_1 Over Time</Title>
      <LineChart
        data={data}
        index="{viz_config['config'].get('x', 'date')}"
        categories={["feature_1"]}
        colors={["blue"]}
        className="h-80 mt-4"
        showLegend={true}
      />
    </Card>
  );
};