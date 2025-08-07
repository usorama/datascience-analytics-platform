import React from 'react';
import { 
  Select, 
  SelectItem, 
  MultiSelect, 
  MultiSelectItem,
  DateRangePicker,
  SearchSelect,
  SearchSelectItem,
  Text,
  Divider
} from '@tremor/react';
import { useDashboardStore } from './store';
import { FilterConfig } from './types';

export const FilterPanel: React.FC = () => {
  const { filters, setFilter, filterConfigs, resetFilters } = useDashboardStore();
  
  const renderFilter = (config: FilterConfig) => {
    const value = filters[config.field] || config.defaultValue;
    
    switch (config.type) {
      case 'dropdown':
        return (
          <Select
            value={value}
            onValueChange={(val) => setFilter(config.field, val)}
            placeholder={config.placeholder}
          >
            <SelectItem value="all">All</SelectItem>
            {config.options?.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </Select>
        );
      
      case 'multiselect':
        return (
          <MultiSelect
            value={value || []}
            onValueChange={(val) => setFilter(config.field, val)}
            placeholder={config.placeholder}
          >
            {config.options?.map((opt) => (
              <MultiSelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </MultiSelectItem>
            ))}
          </MultiSelect>
        );
      
      case 'daterange':
        return (
          <DateRangePicker
            value={value}
            onValueChange={(val) => setFilter(config.field, val)}
            placeholder={config.placeholder}
            enableYearNavigation
          />
        );
      
      case 'search':
        return (
          <SearchSelect
            value={value}
            onValueChange={(val) => setFilter(config.field, val)}
            placeholder={config.placeholder}
          >
            <SearchSelectItem value="all">All</SearchSelectItem>
            {config.options?.map((opt) => (
              <SearchSelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SearchSelectItem>
            ))}
          </SearchSelect>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Filters</h2>
        <button
          onClick={resetFilters}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Reset All
        </button>
      </div>
      
      {filterConfigs.map((config, index) => (
        <div key={config.field}>
          <Text className="mb-2">{config.label}</Text>
          {renderFilter(config)}
          {index < filterConfigs.length - 1 && <Divider className="my-4" />}
        </div>
      ))}
    </div>
  );
};