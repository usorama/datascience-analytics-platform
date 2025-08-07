import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { FilterConfig } from './types';

interface DashboardStore {
  // Filter state
  filters: Record<string, any>;
  filterConfigs: FilterConfig[];
  setFilter: (field: string, value: any) => void;
  setFilterConfigs: (configs: FilterConfig[]) => void;
  resetFilters: () => void;
  
  // UI state
  selectedTab: number;
  setSelectedTab: (tab: number) => void;
  
  // Data state
  rawData: any;
  setRawData: (data: any) => void;
  
  // ML outputs
  mlOutputs: any;
  setMLOutputs: (outputs: any) => void;
}

export const useDashboardStore = create<DashboardStore>()(
  persist(
    (set) => ({
      // Filter state
      filters: {},
      filterConfigs: [],
      setFilter: (field, value) => 
        set((state) => ({ 
          filters: { ...state.filters, [field]: value } 
        })),
      setFilterConfigs: (configs) => set({ filterConfigs: configs }),
      resetFilters: () => set({ filters: {} }),
      
      // UI state
      selectedTab: 0,
      setSelectedTab: (tab) => set({ selectedTab: tab }),
      
      // Data state
      rawData: null,
      setRawData: (data) => set({ rawData: data }),
      
      // ML outputs
      mlOutputs: null,
      setMLOutputs: (outputs) => set({ mlOutputs: outputs }),
    }),
    {
      name: 'dashboard-store',
      partialize: (state) => ({ 
        filters: state.filters,
        selectedTab: state.selectedTab 
      }),
    }
  )
);