import React from 'react';
import { LineChart, Card, Title } from '@tremor/react';

interface viz_4Props {
  data: any[];
  config: any;
}

export const viz_4: React.FC<viz_4Props> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>feature_2 Over Time</Title>
      <LineChart
        data={data}
        index="{viz_config['config'].get('x', 'date')}"
        categories={["feature_2"]}
        colors={["blue"]}
        className="h-80 mt-4"
        showLegend={true}
      />
    </Card>
  );
};