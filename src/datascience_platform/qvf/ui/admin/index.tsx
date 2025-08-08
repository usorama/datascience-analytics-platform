/**
 * QVF Admin Interface Entry Point
 * 
 * Main entry point for the QVF administration interface.
 * Exports all components and utilities for easy integration.
 */

import React from 'react';
import { AdminDashboard } from './components/AdminDashboard';
import { ConfigurationManager } from './components/ConfigurationManager';
import { WeightEditor } from './components/WeightEditor';

// Export main dashboard component
export { AdminDashboard as default } from './components/AdminDashboard';

// Export individual components for custom layouts
export {
  AdminDashboard,
  ConfigurationManager,
  WeightEditor
};

// Export hooks for custom implementations
export {
  useConfigurations,
  useConfiguration,
  useCreateConfiguration,
  useValidation,
  usePresets,
  useExport
} from './hooks/useQVFApi';

// Export types for TypeScript consumers
export * from './types';

/**
 * QVF Admin App Component
 * 
 * Ready-to-use admin application component that can be embedded
 * in existing applications or served as a standalone interface.
 */
export const QVFAdminApp: React.FC<{
  className?: string;
  theme?: 'light' | 'dark';
}> = ({ className, theme = 'light' }) => {
  return (
    <div className={`qvf-admin-app ${theme} ${className || ''}`}>
      <AdminDashboard />
    </div>
  );
};

/**
 * Minimal Weight Editor for embedding in other interfaces
 */
export const QVFWeightEditor: React.FC<{
  configurationId: string;
  onSave?: () => void;
  className?: string;
}> = ({ configurationId, onSave, className }) => {
  const [weights, setWeights] = React.useState(null);
  // Implementation would load and manage weights for specific config
  
  return (
    <div className={className}>
      {/* Simplified weight editor implementation */}
      <div className="p-4 border rounded-lg">
        <h3 className="text-lg font-medium mb-4">QVF Weight Configuration</h3>
        <p className="text-gray-600">Weight editor for configuration: {configurationId}</p>
        {/* Would include actual WeightEditor component here */}
      </div>
    </div>
  );
};

/**
 * Configuration Picker for integration with other UIs
 */
export const QVFConfigPicker: React.FC<{
  onSelect: (configId: string) => void;
  selectedId?: string;
  compact?: boolean;
}> = ({ onSelect, selectedId, compact = false }) => {
  // Implementation would provide a compact configuration selector
  return (
    <div className={`qvf-config-picker ${compact ? 'compact' : ''}`}>
      <select 
        value={selectedId || ''} 
        onChange={(e) => onSelect(e.target.value)}
        className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Select QVF Configuration...</option>
        {/* Options would be loaded from API */}
      </select>
    </div>
  );
};