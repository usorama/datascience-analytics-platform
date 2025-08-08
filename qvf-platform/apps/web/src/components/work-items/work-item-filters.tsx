'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Button } from '@/components/ui/button'
import { X } from 'lucide-react'

interface WorkItemFilters {
  search: string
  priority: string[]
  type: string[]
  assignee: string[]
  status: string[]
}

interface ExtendedWorkItem {
  id: string
  priority: string
  work_item_type?: string
  assigned_to?: string
  state?: string
}

interface WorkItemFiltersProps {
  filters: WorkItemFilters
  onFiltersChange: (filters: WorkItemFilters) => void
  workItems: ExtendedWorkItem[]
}

export function WorkItemFilters({ filters, onFiltersChange, workItems }: WorkItemFiltersProps) {
  const uniqueTypes = Array.from(new Set(workItems.map(item => item.work_item_type).filter(Boolean)))
  const uniqueAssignees = Array.from(new Set(workItems.map(item => item.assigned_to).filter(Boolean)))
  const uniqueStatuses = Array.from(new Set(workItems.map(item => item.state).filter(Boolean)))
  const priorities = ['High', 'Medium', 'Low']
  
  const updateFilter = <K extends keyof WorkItemFilters>(key: K, value: WorkItemFilters[K]) => {
    onFiltersChange({ ...filters, [key]: value })
  }
  
  const toggleArrayFilter = <K extends keyof WorkItemFilters>(
    key: K, 
    value: string, 
    currentArray: string[]
  ) => {
    const newArray = currentArray.includes(value)
      ? currentArray.filter(item => item !== value)
      : [...currentArray, value]
    updateFilter(key, newArray as WorkItemFilters[K])
  }
  
  const clearAllFilters = () => {
    onFiltersChange({
      search: '',
      priority: [],
      type: [],
      assignee: [],
      status: []
    })
  }
  
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Filters</CardTitle>
          <Button variant="outline" size="sm" onClick={clearAllFilters}>
            <X className="h-4 w-4 mr-2" />
            Clear All
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Priority Filter */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm">Priority</h4>
            <div className="space-y-2">
              {priorities.map(priority => (
                <div key={priority} className="flex items-center space-x-2">
                  <Checkbox
                    checked={filters.priority.includes(priority)}
                    onCheckedChange={() => toggleArrayFilter('priority', priority, filters.priority)}
                  />
                  <span className="text-sm">{priority}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Type Filter */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm">Work Item Type</h4>
            <div className="space-y-2">
              {uniqueTypes.map(type => (
                <div key={type} className="flex items-center space-x-2">
                  <Checkbox
                    checked={filters.type.includes(type!)}
                    onCheckedChange={() => toggleArrayFilter('type', type!, filters.type)}
                  />
                  <span className="text-sm">{type}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Status Filter */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm">Status</h4>
            <div className="space-y-2">
              {uniqueStatuses.map(status => (
                <div key={status} className="flex items-center space-x-2">
                  <Checkbox
                    checked={filters.status.includes(status!)}
                    onCheckedChange={() => toggleArrayFilter('status', status!, filters.status)}
                  />
                  <span className="text-sm">{status}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Assignee Filter */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm">Assignee</h4>
            <div className="space-y-2">
              {uniqueAssignees.map(assignee => (
                <div key={assignee} className="flex items-center space-x-2">
                  <Checkbox
                    checked={filters.assignee.includes(assignee!)}
                    onCheckedChange={() => toggleArrayFilter('assignee', assignee!, filters.assignee)}
                  />
                  <span className="text-sm">{assignee}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Active Filters Summary */}
        {(filters.priority.length > 0 || filters.type.length > 0 || filters.status.length > 0 || filters.assignee.length > 0) && (
          <div className="pt-4 border-t">
            <div className="text-sm text-muted-foreground mb-2">Active filters:</div>
            <div className="flex flex-wrap gap-2">
              {filters.priority.map(priority => (
                <span key={`priority-${priority}`} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                  Priority: {priority}
                </span>
              ))}
              {filters.type.map(type => (
                <span key={`type-${type}`} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                  Type: {type}
                </span>
              ))}
              {filters.status.map(status => (
                <span key={`status-${status}`} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                  Status: {status}
                </span>
              ))}
              {filters.assignee.map(assignee => (
                <span key={`assignee-${assignee}`} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">
                  Assignee: {assignee}
                </span>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}