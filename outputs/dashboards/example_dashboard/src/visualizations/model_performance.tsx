import React from 'react';
import { Card, Metric, Text, Flex, ProgressBar } from '@tremor/react';

interface model_performanceProps {
  data: any[];
  config: any;
}

export const model_performance: React.FC<model_performanceProps> = ({ data, config }) => {
  
  const value = data[0]?.metric || 0;
  const target = 100;
  const percentage = (value / target) * 100;
  
  return (
    <Card>
      <Flex alignItems="start">
        <div>
          <Text>Model Performance</Text>
          <Metric>{value.toFixed(2)}</Metric>
        </div>
      </Flex>
      <Flex className="mt-4">
        <Text className="truncate">{percentage.toFixed(1)}% of target</Text>
        <Text>{target}</Text>
      </Flex>
      <ProgressBar value={percentage} className="mt-2" />
    </Card>
  );
};