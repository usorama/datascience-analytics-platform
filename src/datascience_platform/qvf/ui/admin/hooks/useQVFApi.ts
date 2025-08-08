/**
 * React hooks for QVF API integration
 * 
 * Provides type-safe, React-friendly interface to the QVF configuration API.
 * Includes error handling, loading states, and optimistic updates.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  QVFConfiguration,
  ConfigurationSummary,
  ConfigurationCreateRequest,
  ConfigurationUpdateRequest,
  ValidationResult,
  WeightValidationRequest,
  PresetInfo,
  AsyncOperation,
  LoadingState
} from '../types';

// Base API configuration
const API_BASE = '/api/v1/qvf';

// Custom error class for API errors
class QVFApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'QVFApiError';
  }
}

// Generic API client
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      let errorMessage = `API call failed: ${response.status} ${response.statusText}`;
      let errorDetails = null;
      
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
          errorDetails = errorData;
        }
      } catch {
        // Ignore JSON parsing errors for error responses
      }
      
      throw new QVFApiError(errorMessage, response.status, errorDetails);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof QVFApiError) {
      throw error;
    }
    throw new QVFApiError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// Hook for managing configurations list
export function useConfigurations() {
  const [state, setState] = useState<AsyncOperation<ConfigurationSummary[]>>({
    state: 'idle',
    data: [],
  });

  const loadConfigurations = useCallback(async () => {
    setState(prev => ({ ...prev, state: 'loading' }));
    
    try {
      const configurations = await apiCall<ConfigurationSummary[]>('/configurations');
      setState({
        state: 'success',
        data: configurations,
      });
    } catch (error) {
      setState({
        state: 'error',
        error: error instanceof Error ? error.message : 'Failed to load configurations',
      });
    }
  }, []);

  useEffect(() => {
    loadConfigurations();
  }, [loadConfigurations]);

  const deleteConfiguration = useCallback(async (configId: string) => {
    try {
      await apiCall(`/configurations/${configId}`, { method: 'DELETE' });
      
      // Optimistic update
      setState(prev => ({
        ...prev,
        data: prev.data?.filter(config => config.configuration_id !== configId) || [],
      }));
      
      return true;
    } catch (error) {
      throw error;
    }
  }, []);

  return {
    configurations: state.data || [],
    isLoading: state.state === 'loading',
    error: state.error,
    reload: loadConfigurations,
    deleteConfiguration,
  };
}

// Hook for managing single configuration
export function useConfiguration(configId: string | null) {
  const [state, setState] = useState<AsyncOperation<QVFConfiguration>>({
    state: 'idle',
  });

  const loadConfiguration = useCallback(async (id: string) => {
    setState(prev => ({ ...prev, state: 'loading' }));
    
    try {
      const configuration = await apiCall<QVFConfiguration>(`/configurations/${id}`);
      setState({
        state: 'success',
        data: configuration,
      });
    } catch (error) {
      setState({
        state: 'error',
        error: error instanceof Error ? error.message : 'Failed to load configuration',
      });
    }
  }, []);

  useEffect(() => {
    if (configId) {
      loadConfiguration(configId);
    } else {
      setState({ state: 'idle' });
    }
  }, [configId, loadConfiguration]);

  const updateConfiguration = useCallback(async (
    id: string,
    updates: ConfigurationUpdateRequest
  ): Promise<QVFConfiguration> => {
    setState(prev => ({ ...prev, state: 'loading' }));
    
    try {
      const updated = await apiCall<QVFConfiguration>(`/configurations/${id}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      });
      
      setState({
        state: 'success',
        data: updated,
      });
      
      return updated;
    } catch (error) {
      setState(prev => ({
        ...prev,
        state: 'error',
        error: error instanceof Error ? error.message : 'Failed to update configuration',
      }));
      throw error;
    }
  }, []);

  const exportConfiguration = useCallback(async (id: string): Promise<any> => {
    try {
      return await apiCall(`/configurations/${id}/export`);
    } catch (error) {
      throw error;
    }
  }, []);

  return {
    configuration: state.data,
    isLoading: state.state === 'loading',
    error: state.error,
    reload: configId ? () => loadConfiguration(configId) : undefined,
    updateConfiguration,
    exportConfiguration,
  };
}

// Hook for creating configurations
export function useCreateConfiguration() {
  const [state, setState] = useState<LoadingState>('idle');
  const [error, setError] = useState<string | null>(null);

  const createConfiguration = useCallback(async (
    request: ConfigurationCreateRequest
  ): Promise<QVFConfiguration> => {
    setState('loading');
    setError(null);
    
    try {
      const configuration = await apiCall<QVFConfiguration>('/configurations', {
        method: 'POST',
        body: JSON.stringify(request),
      });
      
      setState('success');
      return configuration;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create configuration';
      setState('error');
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  return {
    createConfiguration,
    isCreating: state === 'loading',
    error,
  };
}

// Hook for real-time validation
export function useValidation(debounceMs: number = 500) {
  const [isValidating, setIsValidating] = useState(false);
  const [lastResult, setLastResult] = useState<ValidationResult | null>(null);
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null);

  const validateWeights = useCallback(async (
    request: WeightValidationRequest
  ): Promise<ValidationResult> => {
    setIsValidating(true);
    
    try {
      const result = await apiCall<ValidationResult>('/validate/weights', {
        method: 'POST',
        body: JSON.stringify(request),
      });
      
      setLastResult(result);
      return result;
    } catch (error) {
      const errorResult: ValidationResult = {
        is_valid: false,
        issues: [error instanceof Error ? error.message : 'Validation failed'],
        suggestions: ['Please check your input and try again'],
      };
      setLastResult(errorResult);
      return errorResult;
    } finally {
      setIsValidating(false);
    }
  }, []);

  const validateConfiguration = useCallback(async (
    configId: string
  ): Promise<ValidationResult> => {
    setIsValidating(true);
    
    try {
      const result = await apiCall<ValidationResult>(`/validate/configuration/${configId}`, {
        method: 'POST',
      });
      
      setLastResult(result);
      return result;
    } catch (error) {
      const errorResult: ValidationResult = {
        is_valid: false,
        issues: [error instanceof Error ? error.message : 'Configuration validation failed'],
        suggestions: ['Please check configuration and try again'],
      };
      setLastResult(errorResult);
      return errorResult;
    } finally {
      setIsValidating(false);
    }
  }, []);

  // Debounced validation for real-time feedback
  const validateWeightsDebounced = useCallback((
    request: WeightValidationRequest,
    callback?: (result: ValidationResult) => void
  ) => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    const timer = setTimeout(async () => {
      try {
        const result = await validateWeights(request);
        callback?.(result);
      } catch (error) {
        // Error already handled in validateWeights
      }
    }, debounceMs);

    setDebounceTimer(timer);
  }, [debounceMs, validateWeights, debounceTimer]);

  useEffect(() => {
    return () => {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
    };
  }, [debounceTimer]);

  return {
    validateWeights,
    validateConfiguration,
    validateWeightsDebounced,
    isValidating,
    lastResult,
  };
}

// Hook for managing presets
export function usePresets() {
  const [presets, setPresets] = useState<PresetInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPresets = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiCall<{ presets: Record<string, any> }>('/presets');
      
      const presetList: PresetInfo[] = Object.entries(response.presets).map(([id, preset]) => ({
        id,
        name: preset.name,
        description: preset.description,
        category_weights: preset.category_weights,
      }));
      
      setPresets(presetList);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load presets');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPresets();
  }, [loadPresets]);

  const createFromPreset = useCallback(async (
    presetType: string,
    name?: string
  ): Promise<QVFConfiguration> => {
    try {
      return await apiCall<QVFConfiguration>(`/presets/${presetType}`, {
        method: 'POST',
        body: name ? JSON.stringify({ name }) : undefined,
      });
    } catch (error) {
      throw error;
    }
  }, []);

  return {
    presets,
    isLoading,
    error,
    reload: loadPresets,
    createFromPreset,
  };
}

// Hook for exporting configurations
export function useExport() {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportToJson = useCallback(async (configId: string, filename?: string) => {
    setIsExporting(true);
    setError(null);
    
    try {
      const data = await apiCall(`/configurations/${configId}/export`);
      
      // Create and download file
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `qvf-config-${configId}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Export failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsExporting(false);
    }
  }, []);

  return {
    exportToJson,
    isExporting,
    error,
  };
}