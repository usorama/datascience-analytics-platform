import React from 'react';
import { Grid, Card } from '@tremor/react';
import { useFilteredData } from '../hooks';
import { viz_0 } from '../visualizations/viz_0';
import { viz_1 } from '../visualizations/viz_1';
import { viz_2 } from '../visualizations/viz_2';
import { viz_3 } from '../visualizations/viz_3';
import { viz_4 } from '../visualizations/viz_4';
import { viz_5 } from '../visualizations/viz_5';
import { viz_6 } from '../visualizations/viz_6';
import { viz_7 } from '../visualizations/viz_7';
import { viz_8 } from '../visualizations/viz_8';
import { viz_9 } from '../visualizations/viz_9';

interface AnalyticsTabProps {
  data: any;
  filters: any;
  config: any;
}

export const AnalyticsTab: React.FC<AnalyticsTabProps> = ({ data, filters, config }) => {
  const filteredData = useFilteredData(data.analytics || [], filters);
  
  return (
    <div className="space-y-6">
      <Grid numItems={1} numItemsSm={2} numItemsLg={3} className="gap-6">
        <viz_0 data={filteredData} config={config} /> <viz_1 data={filteredData} config={config} /> <viz_2 data={filteredData} config={config} />
      </Grid>
      
      <div className="space-y-6">
        <viz_3 data={filteredData} config={config} /> <viz_4 data={filteredData} config={config} /> <viz_5 data={filteredData} config={config} /> <viz_6 data={filteredData} config={config} /> <viz_7 data={filteredData} config={config} /> <viz_8 data={filteredData} config={config} /> <viz_9 data={filteredData} config={config} />
      </div>
    </div>
  );
};