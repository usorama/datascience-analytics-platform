'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  ChevronRight, 
  ChevronDown, 
  Plus, 
  Edit, 
  Trash2, 
  MoreHorizontal,
  AlertCircle,
  CheckCircle2,
  Clock
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface ExtendedWorkItem {
  id: string
  title: string
  business_value: number
  technical_complexity: number
  story_points: number
  priority: 'High' | 'Medium' | 'Low'
  risk_level: number
  qvf_score?: number
  priority_tier?: 'High' | 'Medium' | 'Low'
  work_item_type?: string
  parent_id?: string
  state?: string
  assigned_to?: string
  children?: ExtendedWorkItem[]
  dependencies?: string[]
  created_date?: string
  modified_date?: string
}

interface WorkItemHierarchyProps {
  workItems: ExtendedWorkItem[]
  selectedItems: Set<string>
  onSelectionChange: (selected: Set<string>) => void
  onEdit: (id: string) => void
  onDelete: (id: string) => void
  onCreate: (type: 'Epic' | 'Feature' | 'User Story', parentId?: string) => void
}

interface WorkItemRowProps {
  item: ExtendedWorkItem
  level: number
  isSelected: boolean
  isExpanded: boolean
  onToggleExpanded: (id: string) => void
  onToggleSelected: (id: string) => void
  onEdit: (id: string) => void
  onDelete: (id: string) => void
  onCreate: (type: 'Epic' | 'Feature' | 'User Story', parentId?: string) => void
  children?: ExtendedWorkItem[]
}

function WorkItemRow({
  item,
  level,
  isSelected,
  isExpanded,
  onToggleExpanded,
  onToggleSelected,
  onEdit,
  onDelete,
  onCreate,
  children
}: WorkItemRowProps) {
  const hasChildren = children && children.length > 0
  
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'bg-red-100 text-red-800 border-red-200'
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'Low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }
  
  const getStateIcon = (state?: string) => {
    switch (state) {
      case 'Active': return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'New': return <Clock className="h-4 w-4 text-blue-500" />
      case 'Blocked': return <AlertCircle className="h-4 w-4 text-red-500" />
      default: return <Clock className="h-4 w-4 text-gray-400" />
    }
  }
  
  const getTypeColor = (type?: string) => {
    switch (type) {
      case 'Epic': return 'bg-purple-100 text-purple-800'
      case 'Feature': return 'bg-blue-100 text-blue-800'
      case 'User Story': return 'bg-green-100 text-green-800'
      case 'Task': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }
  
  return (
    <div>
      <div 
        className={cn(
          "flex items-center p-4 border-b hover:bg-accent/50 transition-colors",
          isSelected && "bg-accent",
          level > 0 && "border-l-2 border-l-muted"
        )}
        style={{ paddingLeft: `${1 + level * 1.5}rem` }}
      >
        {/* Expand/Collapse */}
        <div className="w-6 flex justify-center">
          {hasChildren ? (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => onToggleExpanded(item.id)}
            >
              {isExpanded ? 
                <ChevronDown className="h-4 w-4" /> : 
                <ChevronRight className="h-4 w-4" />
              }
            </Button>
          ) : (
            <div className="w-6" />
          )}
        </div>
        
        {/* Selection */}
        <div className="w-6 flex justify-center">
          <Checkbox
            checked={isSelected}
            onCheckedChange={() => onToggleSelected(item.id)}
          />
        </div>
        
        {/* Work Item Details */}
        <div className="flex-1 min-w-0 ml-3">
          <div className="flex items-start space-x-3">
            {/* Title and ID */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <span className="font-medium text-sm truncate">{item.title}</span>
                <Badge variant="outline" className="text-xs">{item.id}</Badge>
              </div>
              
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                {getStateIcon(item.state)}
                {item.assigned_to && (
                  <span>Assigned to {item.assigned_to}</span>
                )}
              </div>
            </div>
            
            {/* Type Badge */}
            {item.work_item_type && (
              <Badge className={cn("text-xs", getTypeColor(item.work_item_type))}>
                {item.work_item_type}
              </Badge>
            )}
          </div>
        </div>
        
        {/* Metrics */}
        <div className="flex items-center space-x-4 text-sm">
          {/* Story Points */}
          <div className="text-center min-w-[60px]">
            <div className="font-medium">{item.story_points}</div>
            <div className="text-xs text-muted-foreground">SP</div>
          </div>
          
          {/* QVF Score */}
          <div className="text-center min-w-[80px]">
            {item.qvf_score ? (
              <>
                <div className="font-medium">{item.qvf_score.toFixed(2)}</div>
                <div className="text-xs text-muted-foreground">QVF</div>
              </>
            ) : (
              <div className="text-xs text-muted-foreground">No QVF</div>
            )}
          </div>
          
          {/* Priority */}
          <div className="min-w-[80px]">
            <Badge className={cn("text-xs", getPriorityColor(item.priority))}>
              {item.priority}
            </Badge>
          </div>
          
          {/* Business Value Progress */}
          <div className="min-w-[100px]">
            <div className="text-xs text-muted-foreground mb-1">Value: {item.business_value}%</div>
            <Progress value={item.business_value} className="h-2" />
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center space-x-1 ml-4">
          {item.work_item_type && ['Epic', 'Feature'].includes(item.work_item_type) && (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0"
              onClick={() => {
                const childType = item.work_item_type === 'Epic' ? 'Feature' : 'User Story'
                onCreate(childType as any, item.id)
              }}
            >
              <Plus className="h-4 w-4" />
            </Button>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={() => onEdit(item.id)}
          >
            <Edit className="h-4 w-4" />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 text-red-600 hover:text-red-800"
            onClick={() => onDelete(item.id)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* Children */}
      {hasChildren && isExpanded && children!.map(child => (
        <WorkItemRow
          key={child.id}
          item={child}
          level={level + 1}
          isSelected={false} // Children selection would be implemented separately
          isExpanded={false} // Child expansion state would be managed separately  
          onToggleExpanded={onToggleExpanded}
          onToggleSelected={onToggleSelected}
          onEdit={onEdit}
          onDelete={onDelete}
          onCreate={onCreate}
        />
      ))}
    </div>
  )
}

export function WorkItemHierarchy({
  workItems,
  selectedItems,
  onSelectionChange,
  onEdit,
  onDelete,
  onCreate
}: WorkItemHierarchyProps) {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())
  
  // Build hierarchy from flat list
  const buildHierarchy = (items: ExtendedWorkItem[]): ExtendedWorkItem[] => {
    const itemMap = new Map(items.map(item => [item.id, { ...item, children: [] as ExtendedWorkItem[] }]))
    const rootItems: ExtendedWorkItem[] = []
    
    items.forEach(item => {
      const itemWithChildren = itemMap.get(item.id)!
      if (item.parent_id && itemMap.has(item.parent_id)) {
        const parent = itemMap.get(item.parent_id)!
        if (!parent.children) parent.children = []
        parent.children.push(itemWithChildren)
      } else {
        rootItems.push(itemWithChildren)
      }
    })
    
    return rootItems
  }
  
  const hierarchyItems = buildHierarchy(workItems)
  
  const handleToggleExpanded = (id: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }
  
  const handleToggleSelected = (id: string) => {
    const newSet = new Set(selectedItems)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    onSelectionChange(newSet)
  }
  
  const renderWorkItem = (item: ExtendedWorkItem, level: number = 0): React.ReactNode => {
    const isExpanded = expandedItems.has(item.id)
    const isSelected = selectedItems.has(item.id)
    
    return (
      <WorkItemRow
        key={item.id}
        item={item}
        level={level}
        isSelected={isSelected}
        isExpanded={isExpanded}
        onToggleExpanded={handleToggleExpanded}
        onToggleSelected={handleToggleSelected}
        onEdit={onEdit}
        onDelete={onDelete}
        onCreate={onCreate}
        children={item.children}
      />
    )
  }
  
  if (hierarchyItems.length === 0) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <div className="text-muted-foreground mb-4">
            No work items found. Create your first epic to get started.
          </div>
          <Button onClick={() => onCreate('Epic')}>
            <Plus className="h-4 w-4 mr-2" />
            Create First Epic
          </Button>
        </CardContent>
      </Card>
    )
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Work Item Hierarchy</span>
          <div className="text-sm text-muted-foreground">
            {workItems.length} total items
          </div>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-0">
        {/* Header Row */}
        <div className="flex items-center p-4 border-b bg-muted/50 text-sm font-medium text-muted-foreground">
          <div className="w-12"></div> {/* Expand + Select columns */}
          <div className="flex-1 ml-3">Work Item</div>
          <div className="text-center min-w-[60px]">Points</div>
          <div className="text-center min-w-[80px]">QVF Score</div>
          <div className="text-center min-w-[80px]">Priority</div>
          <div className="min-w-[100px]">Business Value</div>
          <div className="w-24">Actions</div>
        </div>
        
        {/* Work Item Rows */}
        <div>
          {hierarchyItems.map(item => renderWorkItem(item))}
        </div>
      </CardContent>
    </Card>
  )
}