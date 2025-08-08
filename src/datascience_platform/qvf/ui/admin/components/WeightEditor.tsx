/**
 * Weight Editor Component
 * 
 * Interactive weight configuration interface with real-time validation,
 * visual feedback, and accessibility features.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, Title, Text, Badge, Button } from '@tremor/react';
import {
  CriteriaWeights,
  ValidationResult,
  CATEGORY_INFO,
  CriteriaCategory
} from '../types';
import { useValidation } from '../hooks/useQVFApi';

interface WeightSliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  color?: string;
  disabled?: boolean;
  description?: string;
  icon?: string;
}

const WeightSlider: React.FC<WeightSliderProps> = ({
  label,
  value,
  onChange,
  color = 'blue',
  disabled = false,
  description,
  icon
}) => {
  const handleSliderChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(event.target.value);
    onChange(newValue);
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(event.target.value) || 0;
    onChange(Math.max(0, Math.min(1, newValue)));
  };

  const percentage = Math.round(value * 100);

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-2">
          {icon && <span className="text-gray-400">{icon}</span>}
          <Text className="font-medium">{label}</Text>
        </div>
        <div className="flex items-center space-x-2">
          <input
            type="number"
            value={percentage}
            onChange={handleInputChange}
            disabled={disabled}
            className="w-16 px-2 py-1 text-sm border rounded focus:ring-2 focus:ring-blue-500"
            min="0"
            max="100"
            step="1"
          />
          <Text className="text-sm text-gray-500">%</Text>
        </div>
      </div>
      
      {description && (
        <Text className="text-sm text-gray-600">{description}</Text>
      )}
      
      <div className="relative">
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={value}
          onChange={handleSliderChange}
          disabled={disabled}
          className={`w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer
            slider-${color} disabled:opacity-50 disabled:cursor-not-allowed`}
        />
        
        {/* Visual progress bar */}
        <div
          className={`absolute top-0 h-2 bg-${color}-500 rounded-lg pointer-events-none`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      <div className="flex justify-between text-xs text-gray-500">
        <span>0%</span>
        <span className="font-medium">{percentage}%</span>
        <span>100%</span>
      </div>
    </div>
  );
};

interface ValidationIndicatorProps {
  result: ValidationResult | null;
  isValidating: boolean;
}

const ValidationIndicator: React.FC<ValidationIndicatorProps> = ({
  result,
  isValidating
}) => {
  if (isValidating) {
    return (
      <div className="flex items-center space-x-2 text-blue-600">
        <div className="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full" />
        <Text>Validating...</Text>
      </div>
    );
  }

  if (!result) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-2">
        <Badge
          color={result.is_valid ? 'green' : 'red'}
          size="sm"
        >
          {result.is_valid ? '✓ Valid' : '⚠ Issues Found'}
        </Badge>
      </div>
      
      {result.issues.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <Text className="font-medium text-red-800 mb-1">Issues:</Text>
          <ul className="text-sm text-red-700 space-y-1">
            {result.issues.map((issue, index) => (
              <li key={index} className="flex items-start space-x-1">
                <span>•</span>
                <span>{issue}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {result.suggestions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
          <Text className="font-medium text-blue-800 mb-1">Suggestions:</Text>
          <ul className="text-sm text-blue-700 space-y-1">
            {result.suggestions.map((suggestion, index) => (
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
};

interface WeightEditorProps {
  weights: CriteriaWeights;
  onChange: (weights: CriteriaWeights) => void;
  onValidation?: (result: ValidationResult) => void;
  disabled?: boolean;
  showPresets?: boolean;
}

export const WeightEditor: React.FC<WeightEditorProps> = ({
  weights,
  onChange,
  onValidation,
  disabled = false,
  showPresets = true
}) => {
  const [localWeights, setLocalWeights] = useState<CriteriaWeights>(weights);
  const [total, setTotal] = useState(0);
  const [isNormalized, setIsNormalized] = useState(false);
  
  const { validateWeightsDebounced, isValidating, lastResult } = useValidation(500);

  // Update local weights when props change
  useEffect(() => {
    setLocalWeights(weights);
  }, [weights]);

  // Calculate total and check normalization
  useEffect(() => {
    const newTotal = Object.values(localWeights).reduce((sum, weight) => sum + weight, 0);
    setTotal(newTotal);
    setIsNormalized(Math.abs(newTotal - 1.0) < 1e-6);
  }, [localWeights]);

  // Trigger validation when weights change
  useEffect(() => {
    validateWeightsDebounced(
      { category_weights: localWeights },
      (result) => {
        onValidation?.(result);
      }
    );
  }, [localWeights, validateWeightsDebounced, onValidation]);

  const handleWeightChange = useCallback((category: keyof CriteriaWeights, value: number) => {
    const newWeights = {
      ...localWeights,
      [category]: value
    };
    
    setLocalWeights(newWeights);
    onChange(newWeights);
  }, [localWeights, onChange]);

  const handleNormalize = useCallback(() => {
    const currentTotal = Object.values(localWeights).reduce((sum, weight) => sum + weight, 0);
    
    if (currentTotal === 0) return;
    
    const normalizedWeights: CriteriaWeights = {
      business_value: localWeights.business_value / currentTotal,
      strategic_alignment: localWeights.strategic_alignment / currentTotal,
      customer_value: localWeights.customer_value / currentTotal,
      implementation_complexity: localWeights.implementation_complexity / currentTotal,
      risk_assessment: localWeights.risk_assessment / currentTotal
    };
    
    setLocalWeights(normalizedWeights);
    onChange(normalizedWeights);
  }, [localWeights, onChange]);

  const handleReset = useCallback(() => {
    const defaultWeights: CriteriaWeights = {
      business_value: 0.25,
      strategic_alignment: 0.25,
      customer_value: 0.20,
      implementation_complexity: 0.15,
      risk_assessment: 0.15
    };
    
    setLocalWeights(defaultWeights);
    onChange(defaultWeights);
  }, [onChange]);

  const applyPreset = useCallback((preset: 'agile' | 'enterprise' | 'startup') => {
    let presetWeights: CriteriaWeights;
    
    switch (preset) {
      case 'agile':
        presetWeights = {
          business_value: 0.30,
          customer_value: 0.30,
          implementation_complexity: 0.20,
          strategic_alignment: 0.15,
          risk_assessment: 0.05
        };
        break;
      case 'enterprise':
        presetWeights = {
          strategic_alignment: 0.35,
          business_value: 0.25,
          risk_assessment: 0.20,
          customer_value: 0.15,
          implementation_complexity: 0.05
        };
        break;
      case 'startup':
        presetWeights = {
          customer_value: 0.35,
          business_value: 0.30,
          implementation_complexity: 0.25,
          strategic_alignment: 0.07,
          risk_assessment: 0.03
        };
        break;
    }
    
    setLocalWeights(presetWeights);
    onChange(presetWeights);
  }, [onChange]);

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex justify-between items-center mb-4">
          <Title>Category Weights Configuration</Title>
          <div className="flex items-center space-x-2">
            <Badge
              color={isNormalized ? 'green' : 'yellow'}
              size="sm"
            >
              Total: {(total * 100).toFixed(1)}%
            </Badge>
          </div>
        </div>
        
        <Text className="text-gray-600 mb-6">
          Configure the relative importance of each QVF category. Weights must sum to 100% (1.0).
        </Text>

        {/* Weight Sliders */}
        <div className="space-y-6">
          {(Object.entries(CATEGORY_INFO) as [CriteriaCategory, typeof CATEGORY_INFO[CriteriaCategory]][]).map(
            ([category, info]) => (
              <WeightSlider
                key={category}
                label={info.name}
                value={localWeights[category]}
                onChange={(value) => handleWeightChange(category, value)}
                color={info.color}
                disabled={disabled}
                description={info.description}
                icon={info.icon}
              />
            )
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between items-center mt-6 pt-4 border-t">
          <div className="flex space-x-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleNormalize}
              disabled={disabled || isNormalized}
            >
              Normalize
            </Button>
            <Button
              variant="secondary" 
              size="sm"
              onClick={handleReset}
              disabled={disabled}
            >
              Reset to Default
            </Button>
          </div>
          
          {/* Preset Buttons */}
          {showPresets && (
            <div className="flex space-x-2">
              <Button
                variant="light"
                size="sm"
                onClick={() => applyPreset('agile')}
                disabled={disabled}
                color="blue"
              >
                Agile
              </Button>
              <Button
                variant="light"
                size="sm"
                onClick={() => applyPreset('enterprise')}
                disabled={disabled}
                color="purple"
              >
                Enterprise
              </Button>
              <Button
                variant="light"
                size="sm"
                onClick={() => applyPreset('startup')}
                disabled={disabled}
                color="green"
              >
                Startup
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Validation Results */}
      <Card>
        <Title>Validation Results</Title>
        <div className="mt-4">
          <ValidationIndicator
            result={lastResult}
            isValidating={isValidating}
          />
        </div>
      </Card>
    </div>
  );
};