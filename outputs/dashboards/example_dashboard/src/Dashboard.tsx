import React from 'react';
import { Card, Grid, Title, Text } from '@tremor/react';
import { Layout } from './Layout';
import { TabContainer } from './TabContainer';
import { useDashboardStore } from './store';
import { DashboardConfig } from './types';

interface DashboardProps {
  config: DashboardConfig;
  data: any;
}

export const Dashboard: React.FC<DashboardProps> = ({ config, data }) => {
  const { filters, setFilter } = useDashboardStore();
  
  return (
    <Layout>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="px-4 py-4 sm:px-6 lg:px-8">
            <Title>{config.title || 'Analytics Dashboard'}</Title>
            <Text>{config.description || 'ML-powered insights and analytics'}</Text>
          </div>
        </header>
        
        <TabContainer 
          data={data}
          filters={filters}
          config={config}
        />
      </div>
    </Layout>
  );
};

export default Dashboard;