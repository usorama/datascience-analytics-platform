import React, { useState } from 'react';
import { Tab, TabGroup, TabList, TabPanel, TabPanels } from '@tremor/react';
import { AnalyticsTab } from './tabs/AnalyticsTab';
import { MLOutputsTab } from './tabs/MLOutputsTab';
import { DecisionsTab } from './tabs/DecisionsTab';

interface TabContainerProps {
  data: any;
  filters: any;
  config: any;
}

export const TabContainer: React.FC<TabContainerProps> = ({ data, filters, config }) => {
  const [selectedTab, setSelectedTab] = useState(0);
  
  return (
    <div className="p-6">
      <TabGroup index={selectedTab} onIndexChange={setSelectedTab}>
        <TabList variant="solid">
          <Tab icon={() => <span>📊</span>}>Analytics</Tab>
          <Tab icon={() => <span>🤖</span>}>ML Outputs</Tab>
          <Tab icon={() => <span>🎯</span>}>Decisions & Predictions</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            <AnalyticsTab data={data} filters={filters} config={config} />
          </TabPanel>
          
          <TabPanel>
            <MLOutputsTab data={data} filters={filters} config={config} />
          </TabPanel>
          
          <TabPanel>
            <DecisionsTab data={data} filters={filters} config={config} />
          </TabPanel>
        </TabPanels>
      </TabGroup>
    </div>
  );
};