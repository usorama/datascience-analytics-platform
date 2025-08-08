/**
 * QVF Admin Dashboard
 * 
 * Main dashboard component for QVF administration with tabbed interface,
 * real-time configuration management, and comprehensive validation feedback.
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Title,
  Text,
  TabGroup,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Badge,
  Button,
  Grid,
  Metric,
  Flex,
  ProgressBar
} from '@tremor/react';
import {
  CogIcon,
  ChartBarIcon,
  DocumentCheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

import { ConfigurationManager } from './ConfigurationManager';
import { WeightEditor } from './WeightEditor';
import {
  QVFConfiguration,
  CriteriaWeights,
  ValidationResult,
  DEFAULT_CATEGORY_WEIGHTS
} from '../types';
import {
  useConfigurations,
  useConfiguration,
  useValidation
} from '../hooks/useQVFApi';

interface DashboardStatsProps {
  configurations: any[];
  isLoading: boolean;
}

const DashboardStats: React.FC<DashboardStatsProps> = ({
  configurations,
  isLoading
}) => {
  if (isLoading) {
    return (
      <Grid numItems={1} numItemsSm={2} numItemsLg={4} className="gap-6">
        {[1, 2, 3, 4].map(i => (
          <Card key={i} className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-2"></div>
            <div className="h-12 bg-gray-100 rounded"></div>
          </Card>
        ))}
      </Grid>
    );
  }

  const validConfigs = configurations.filter(c => c.is_valid).length;
  const totalConfigs = configurations.length;
  const avgCriteria = totalConfigs > 0 
    ? Math.round(configurations.reduce((sum, c) => sum + c.criteria_count, 0) / totalConfigs)
    : 0;
  const healthScore = totalConfigs > 0 ? (validConfigs / totalConfigs) * 100 : 0;

  return (
    <Grid numItems={1} numItemsSm={2} numItemsLg={4} className="gap-6">
      <Card>
        <Text>Total Configurations</Text>
        <Metric>{totalConfigs}</Metric>
      </Card>
      
      <Card>
        <Text>Valid Configurations</Text>
        <Flex alignItems="start">
          <Metric>{validConfigs}</Metric>
          <Badge color={validConfigs === totalConfigs ? 'green' : 'yellow'}>
            {totalConfigs > 0 ? Math.round((validConfigs / totalConfigs) * 100) : 0}%
          </Badge>
        </Flex>
      </Card>
      
      <Card>
        <Text>Average Criteria Count</Text>
        <Metric>{avgCriteria}</Metric>
      </Card>
      
      <Card>
        <Text>System Health</Text>
        <Metric>{healthScore.toFixed(1)}%</Metric>
        <ProgressBar value={healthScore} className="mt-2" />
      </Card>
    </Grid>
  );
};

interface WeightConfiguratorProps {
  selectedConfigId?: string;
}

const WeightConfigurator: React.FC<WeightConfiguratorProps> = ({
  selectedConfigId
}) => {
  const [weights, setWeights] = useState<CriteriaWeights>(DEFAULT_CATEGORY_WEIGHTS);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  
  const { configuration, updateConfiguration, isLoading } = useConfiguration(selectedConfigId || null);

  // Update weights when configuration changes
  useEffect(() => {
    if (configuration) {
      setWeights(configuration.category_weights);
      setHasChanges(false);
    }
  }, [configuration]);

  const handleWeightsChange = (newWeights: CriteriaWeights) => {
    setWeights(newWeights);
    setHasChanges(true);
  };

  const handleSave = async () => {
    if (!selectedConfigId || !hasChanges) return;
    
    try {
      await updateConfiguration(selectedConfigId, {
        category_weights: weights
      });
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to save weights:', error);
    }
  };

  const handleReset = () => {
    if (configuration) {
      setWeights(configuration.category_weights);
      setHasChanges(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-16 bg-gray-100 rounded"></div>
            ))}
          </div>
        </Card>
      </div>
    );
  }

  if (!selectedConfigId) {
    return (
      <Card>
        <div className="text-center py-12">
          <CogIcon className="mx-auto h-12 w-12 text-gray-400" />
          <Title className="mt-4">No Configuration Selected</Title>
          <Text className="mt-2">
            Select a configuration from the Configurations tab to edit its weights.
          </Text>
        </div>
      </Card>
    );
  }

  if (!configuration) {
    return (
      <Card>
        <div className="text-center py-12">
          <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
          <Title className="mt-4">Configuration Not Found</Title>
          <Text className="mt-2">
            The selected configuration could not be loaded.
          </Text>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Configuration Info */}
      <Card>
        <div className="flex justify-between items-start">
          <div>
            <Title>{configuration.name}</Title>
            {configuration.description && (
              <Text className="mt-1">{configuration.description}</Text>
            )}
          </div>
          <div className="flex space-x-2">
            {hasChanges && (
              <>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleReset}
                >
                  Reset
                </Button>
                <Button
                  size="sm"
                  onClick={handleSave}
                  color="blue"
                >
                  Save Changes
                </Button>
              </>
            )}
          </div>
        </div>
      </Card>

      {/* Weight Editor */}
      <WeightEditor
        weights={weights}
        onChange={handleWeightsChange}
        onValidation={setValidationResult}
        disabled={false}
        showPresets={true}
      />

      {/* Changes Indicator */}
      {hasChanges && (
        <Card>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500 mr-2" />
              <Text className="text-yellow-800 font-medium">
                You have unsaved changes
              </Text>
            </div>
            <Text className="text-yellow-700 mt-1 text-sm">
              Remember to save your changes to apply the new weights to this configuration.
            </Text>
          </div>
        </Card>
      )}
    </div>
  );
};

interface ValidationSummaryProps {
  configurations: any[];
}

const ValidationSummary: React.FC<ValidationSummaryProps> = ({
  configurations
}) => {
  const [detailedValidation, setDetailedValidation] = useState<Record<string, ValidationResult>>({});
  const { validateConfiguration } = useValidation();

  // Run validation for all configurations
  useEffect(() => {
    const validateAll = async () => {
      const results: Record<string, ValidationResult> = {};
      
      for (const config of configurations) {
        try {
          const result = await validateConfiguration(config.configuration_id);
          results[config.configuration_id] = result;
        } catch (error) {
          results[config.configuration_id] = {
            is_valid: false,
            issues: ['Validation failed'],
            suggestions: ['Check configuration and try again']
          };
        }
      }
      
      setDetailedValidation(results);
    };

    if (configurations.length > 0) {
      validateAll();
    }
  }, [configurations, validateConfiguration]);

  const validConfigs = configurations.filter(c => c.is_valid);
  const invalidConfigs = configurations.filter(c => !c.is_valid);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <Grid numItems={1} numItemsSm={3} className="gap-6">
        <Card>
          <Text>Valid Configurations</Text>
          <Metric color="green">{validConfigs.length}</Metric>
        </Card>
        
        <Card>
          <Text>Configurations with Issues</Text>
          <Metric color="red">{invalidConfigs.length}</Metric>
        </Card>
        
        <Card>
          <Text>Validation Coverage</Text>
          <Metric>
            {configurations.length > 0 
              ? Math.round((Object.keys(detailedValidation).length / configurations.length) * 100)
              : 0}%
          </Metric>
        </Card>
      </Grid>

      {/* Configuration Validation Details */}
      <Card>
        <Title>Configuration Validation Details</Title>
        <div className="mt-4 space-y-4">
          {configurations.map(config => {
            const validation = detailedValidation[config.configuration_id];
            
            return (
              <div key={config.configuration_id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <Text className="font-medium">{config.name}</Text>
                    <Text className="text-sm text-gray-500">
                      {config.criteria_count} criteria
                    </Text>
                  </div>
                  <Badge
                    color={config.is_valid ? 'green' : 'red'}
                    size="sm"
                  >
                    {config.is_valid ? 'Valid' : 'Issues'}
                  </Badge>
                </div>
                
                {validation && !validation.is_valid && (
                  <div className="mt-2">
                    <Text className="text-sm font-medium text-red-800">Issues:</Text>
                    <ul className="text-sm text-red-700 mt-1 space-y-1">
                      {validation.issues.map((issue, index) => (
                        <li key={index} className="flex items-start space-x-1">
                          <span>•</span>
                          <span>{issue}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {validation && validation.suggestions.length > 0 && (
                  <div className="mt-2">
                    <Text className="text-sm font-medium text-blue-800">Suggestions:</Text>
                    <ul className="text-sm text-blue-700 mt-1 space-y-1">
                      {validation.suggestions.slice(0, 2).map((suggestion, index) => (
                        <li key={index} className="flex items-start space-x-1">
                          <span>💡</span>
                          <span>{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};

export const AdminDashboard: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedConfigForWeights, setSelectedConfigForWeights] = useState<string | undefined>();
  
  const { configurations, isLoading, error } = useConfigurations();

  // Auto-select first valid configuration for weights tab
  useEffect(() => {
    if (!selectedConfigForWeights && configurations.length > 0) {
      const validConfig = configurations.find(c => c.is_valid);
      if (validConfig) {
        setSelectedConfigForWeights(validConfig.configuration_id);
      }
    }
  }, [configurations, selectedConfigForWeights]);

  if (error) {
    return (
      <div className="p-6">
        <Card>
          <div className="text-center py-12">
            <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-500" />
            <Title className="mt-4">Failed to Load Admin Dashboard</Title>
            <Text className="mt-2 text-gray-600">{error}</Text>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Dashboard Header */}
      <div>
        <Title>QVF Administration Dashboard</Title>
        <Text className="mt-1">
          Manage Quantified Value Framework configurations, weights, and validation
        </Text>
      </div>

      {/* Dashboard Stats */}
      <DashboardStats 
        configurations={configurations}
        isLoading={isLoading}
      />

      {/* Tabbed Interface */}
      <Card>
        <TabGroup index={selectedTab} onIndexChange={setSelectedTab}>
          <TabList className="mb-6">
            <Tab icon={CogIcon}>
              Configurations
            </Tab>
            <Tab icon={ChartBarIcon}>
              Weight Configuration
            </Tab>
            <Tab icon={DocumentCheckIcon}>
              Validation Summary
            </Tab>
          </TabList>
          
          <TabPanels>
            {/* Configuration Management Tab */}
            <TabPanel>
              <ConfigurationManager />
            </TabPanel>
            
            {/* Weight Configuration Tab */}
            <TabPanel>
              <div className="space-y-4">
                {/* Configuration Selector */}
                {configurations.length > 0 && (
                  <Card>
                    <Title>Select Configuration</Title>
                    <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {configurations.map(config => (
                        <button
                          key={config.configuration_id}
                          onClick={() => setSelectedConfigForWeights(config.configuration_id)}
                          className={`text-left p-3 rounded-lg border transition-colors ${
                            selectedConfigForWeights === config.configuration_id
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <Text className="font-medium">{config.name}</Text>
                          <Text className="text-sm text-gray-500 mt-1">
                            {config.criteria_count} criteria
                          </Text>
                        </button>
                      ))}
                    </div>
                  </Card>
                )}
                
                <WeightConfigurator selectedConfigId={selectedConfigForWeights} />
              </div>
            </TabPanel>
            
            {/* Validation Summary Tab */}
            <TabPanel>
              <ValidationSummary configurations={configurations} />
            </TabPanel>
          </TabPanels>
        </TabGroup>
      </Card>
    </div>
  );
};