/**
 * Configuration Manager Component
 * 
 * Main management interface for QVF configurations with list view,
 * CRUD operations, and export functionality.
 */

import React, { useState, useCallback } from 'react';
import {
  Card,
  Title,
  Text,
  Button,
  Table,
  TableHead,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Badge,
  Dialog,
  DialogPanel,
  TextInput,
  Textarea,
  Select,
  SelectItem
} from '@tremor/react';
import {
  PlusIcon,
  TrashIcon,
  PencilSquareIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  DocumentDuplicateIcon
} from '@heroicons/react/24/outline';

import {
  ConfigurationSummary,
  QVFConfiguration,
  ConfigurationCreateRequest,
  ValidationResult
} from '../types';
import {
  useConfigurations,
  useConfiguration,
  useCreateConfiguration,
  usePresets,
  useExport
} from '../hooks/useQVFApi';

interface ConfigurationListProps {
  configurations: ConfigurationSummary[];
  onSelect: (configId: string) => void;
  onEdit: (configId: string) => void;
  onDelete: (configId: string) => void;
  onExport: (configId: string) => void;
  onDuplicate: (configId: string) => void;
  isLoading?: boolean;
}

const ConfigurationList: React.FC<ConfigurationListProps> = ({
  configurations,
  onSelect,
  onEdit,
  onDelete,
  onExport,
  onDuplicate,
  isLoading = false
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <Card className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-12 bg-gray-100 rounded"></div>
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <Title>QVF Configurations</Title>
      <Text className="mt-2 mb-6">
        Manage your QVF configurations. Click on a configuration to view details.
      </Text>

      <Table>
        <TableHead>
          <TableRow>
            <TableHeaderCell>Name</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Criteria</TableHeaderCell>
            <TableHeaderCell>Last Modified</TableHeaderCell>
            <TableHeaderCell>Actions</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {configurations.map((config) => (
            <TableRow
              key={config.configuration_id}
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => onSelect(config.configuration_id)}
            >
              <TableCell>
                <div>
                  <Text className="font-medium">{config.name}</Text>
                  {config.description && (
                    <Text className="text-sm text-gray-500 mt-1">
                      {config.description}
                    </Text>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <Badge
                  color={config.is_valid ? 'green' : 'red'}
                  size="sm"
                >
                  {config.is_valid ? 'Valid' : 'Issues'}
                </Badge>
              </TableCell>
              <TableCell>
                <Text>{config.criteria_count} criteria</Text>
              </TableCell>
              <TableCell>
                <Text className="text-sm">
                  {formatDate(config.last_modified)}
                </Text>
              </TableCell>
              <TableCell>
                <div className="flex space-x-1" onClick={(e) => e.stopPropagation()}>
                  <Button
                    variant="light"
                    size="xs"
                    icon={EyeIcon}
                    onClick={() => onSelect(config.configuration_id)}
                    title="View Configuration"
                  />
                  <Button
                    variant="light"
                    size="xs"
                    icon={PencilSquareIcon}
                    onClick={() => onEdit(config.configuration_id)}
                    title="Edit Configuration"
                  />
                  <Button
                    variant="light"
                    size="xs"
                    icon={DocumentDuplicateIcon}
                    onClick={() => onDuplicate(config.configuration_id)}
                    title="Duplicate Configuration"
                  />
                  <Button
                    variant="light"
                    size="xs"
                    icon={ArrowDownTrayIcon}
                    onClick={() => onExport(config.configuration_id)}
                    title="Export Configuration"
                  />
                  <Button
                    variant="light"
                    size="xs"
                    icon={TrashIcon}
                    color="red"
                    onClick={() => onDelete(config.configuration_id)}
                    title="Delete Configuration"
                  />
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {configurations.length === 0 && (
        <div className="text-center py-8">
          <Text className="text-gray-500">
            No configurations found. Create your first QVF configuration to get started.
          </Text>
        </div>
      )}
    </Card>
  );
};

interface CreateConfigurationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (request: ConfigurationCreateRequest) => Promise<void>;
  presets: Array<{ id: string; name: string; description: string }>;
}

const CreateConfigurationModal: React.FC<CreateConfigurationModalProps> = ({
  isOpen,
  onClose,
  onCreate,
  presets
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    preset_type: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const request: ConfigurationCreateRequest = {
        name: formData.name,
        description: formData.description || undefined,
        preset_type: formData.preset_type as any || undefined
      };

      await onCreate(request);
      
      // Reset form and close
      setFormData({ name: '', description: '', preset_type: '' });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create configuration');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setFormData({ name: '', description: '', preset_type: '' });
      setError(null);
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onClose={handleClose}>
      <DialogPanel className="max-w-md mx-auto">
        <Title className="mb-4">Create New QVF Configuration</Title>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="config-name" className="block text-sm font-medium mb-2">
              Configuration Name *
            </label>
            <TextInput
              id="config-name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter configuration name"
              required
              disabled={isSubmitting}
            />
          </div>

          <div>
            <label htmlFor="config-description" className="block text-sm font-medium mb-2">
              Description
            </label>
            <Textarea
              id="config-description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe the purpose of this configuration"
              rows={3}
              disabled={isSubmitting}
            />
          </div>

          <div>
            <label htmlFor="preset-type" className="block text-sm font-medium mb-2">
              Start From Preset (Optional)
            </label>
            <Select
              value={formData.preset_type}
              onValueChange={(value) => setFormData(prev => ({ ...prev, preset_type: value }))}
              disabled={isSubmitting}
            >
              <SelectItem value="">Custom Configuration</SelectItem>
              {presets.map(preset => (
                <SelectItem key={preset.id} value={preset.id}>
                  {preset.name}
                </SelectItem>
              ))}
            </Select>
            {formData.preset_type && (
              <Text className="text-sm text-gray-600 mt-1">
                {presets.find(p => p.id === formData.preset_type)?.description}
              </Text>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <Text className="text-red-800">{error}</Text>
            </div>
          )}

          <div className="flex space-x-2 pt-4">
            <Button
              type="submit"
              disabled={!formData.name.trim() || isSubmitting}
              loading={isSubmitting}
            >
              Create Configuration
            </Button>
            <Button
              variant="secondary"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          </div>
        </form>
      </DialogPanel>
    </Dialog>
  );
};

export const ConfigurationManager: React.FC = () => {
  const [selectedConfigId, setSelectedConfigId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  // Hooks
  const { configurations, isLoading, error, reload, deleteConfiguration } = useConfigurations();
  const { configuration: selectedConfig } = useConfiguration(selectedConfigId);
  const { createConfiguration, isCreating } = useCreateConfiguration();
  const { presets } = usePresets();
  const { exportToJson, isExporting } = useExport();

  // Handlers
  const handleCreateConfiguration = useCallback(async (request: ConfigurationCreateRequest) => {
    const newConfig = await createConfiguration(request);
    await reload(); // Refresh the list
    setSelectedConfigId(newConfig.configuration_id);
  }, [createConfiguration, reload]);

  const handleDeleteConfiguration = useCallback(async (configId: string) => {
    try {
      await deleteConfiguration(configId);
      if (selectedConfigId === configId) {
        setSelectedConfigId(null);
      }
      setConfirmDelete(null);
    } catch (error) {
      console.error('Failed to delete configuration:', error);
    }
  }, [deleteConfiguration, selectedConfigId]);

  const handleExportConfiguration = useCallback(async (configId: string) => {
    try {
      const config = configurations.find(c => c.configuration_id === configId);
      const filename = config ? `${config.name.replace(/\s+/g, '-').toLowerCase()}.json` : undefined;
      await exportToJson(configId, filename);
    } catch (error) {
      console.error('Failed to export configuration:', error);
    }
  }, [exportToJson, configurations]);

  const handleDuplicateConfiguration = useCallback(async (configId: string) => {
    // TODO: Implement duplication by loading config and creating new one
    console.log('Duplicate configuration:', configId);
  }, []);

  if (error) {
    return (
      <div className="p-6">
        <Card>
          <div className="text-center py-8">
            <Text className="text-red-600 mb-4">Failed to load configurations</Text>
            <Text className="text-gray-500 mb-4">{error}</Text>
            <Button onClick={reload}>Retry</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <Title>QVF Configuration Manager</Title>
          <Text className="mt-1">
            Manage Quantified Value Framework configurations for prioritization
          </Text>
        </div>
        <Button
          icon={PlusIcon}
          onClick={() => setShowCreateModal(true)}
          disabled={isCreating}
        >
          New Configuration
        </Button>
      </div>

      {/* Configuration List */}
      <ConfigurationList
        configurations={configurations}
        onSelect={setSelectedConfigId}
        onEdit={setSelectedConfigId} // For now, same as select
        onDelete={(id) => setConfirmDelete(id)}
        onExport={handleExportConfiguration}
        onDuplicate={handleDuplicateConfiguration}
        isLoading={isLoading}
      />

      {/* Selected Configuration Details */}
      {selectedConfig && (
        <Card>
          <Title>Configuration Details</Title>
          <div className="mt-4 space-y-4">
            <div>
              <Text className="font-medium">Name:</Text>
              <Text>{selectedConfig.name}</Text>
            </div>
            {selectedConfig.description && (
              <div>
                <Text className="font-medium">Description:</Text>
                <Text>{selectedConfig.description}</Text>
              </div>
            )}
            <div>
              <Text className="font-medium">Criteria Count:</Text>
              <Text>{selectedConfig.criteria.length}</Text>
            </div>
            <div>
              <Text className="font-medium">Last Modified:</Text>
              <Text>{new Date(selectedConfig.last_modified).toLocaleDateString()}</Text>
            </div>
            {selectedConfig.validation && (
              <div>
                <Text className="font-medium">Validation Status:</Text>
                <Badge
                  color={selectedConfig.validation.is_valid ? 'green' : 'red'}
                  className="ml-2"
                >
                  {selectedConfig.validation.is_valid ? 'Valid' : 'Has Issues'}
                </Badge>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Create Modal */}
      <CreateConfigurationModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreate={handleCreateConfiguration}
        presets={presets}
      />

      {/* Delete Confirmation */}
      <Dialog open={!!confirmDelete} onClose={() => setConfirmDelete(null)}>
        <DialogPanel className="max-w-sm mx-auto">
          <Title className="mb-4">Confirm Deletion</Title>
          <Text className="mb-6">
            Are you sure you want to delete this configuration? This action cannot be undone.
          </Text>
          <div className="flex space-x-2">
            <Button
              color="red"
              onClick={() => confirmDelete && handleDeleteConfiguration(confirmDelete)}
            >
              Delete
            </Button>
            <Button
              variant="secondary"
              onClick={() => setConfirmDelete(null)}
            >
              Cancel
            </Button>
          </div>
        </DialogPanel>
      </Dialog>
    </div>
  );
};