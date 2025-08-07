import React from 'react';
import Dashboard from './src/Dashboard';
import dashboardData from './data/dashboard-data.json';
import dashboardConfig from './data/dashboard-config.json';

function App() {
  return <Dashboard config={dashboardConfig} data={dashboardData} />;
}

export default App;