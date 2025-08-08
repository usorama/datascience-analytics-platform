'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { WorkItem, qvfAPI, workItemsAPI } from '@/lib/api'
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  RefreshCw,
  MoreHorizontal,
  Edit,
  Trash2,
  ChevronRight,
  ChevronDown,
  DragHandleDots2
} from 'lucide-react'
import { WorkItemHierarchy } from './work-item-hierarchy'
import { WorkItemEditor } from './work-item-editor'
import { QVFScoringInterface } from './qvf-scoring-interface'
import { BulkOperations } from './bulk-operations'
import { WorkItemFilters } from './work-item-filters'
import { ExportDialog } from './export-dialog'

interface ExtendedWorkItem extends WorkItem {
  qvf_score?: number
  priority_tier?: 'High' | 'Medium' | 'Low'
  children?: ExtendedWorkItem[]
  parent_id?: string
  work_item_type?: 'Epic' | 'Feature' | 'User Story' | 'Task'
  dependencies?: string[]
}

interface WorkItemFilters {
  search: string
  priority: string[]
  type: string[]
  assignee: string[]
  status: string[]
}

export function WorkItemManagement() {
  const [workItems, setWorkItems] = useState<ExtendedWorkItem[]>([])
  const [filteredItems, setFilteredItems] = useState<ExtendedWorkItem[]>([])
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [showExport, setShowExport] = useState(false)
  const [activeView, setActiveView] = useState<'hierarchy' | 'list' | 'scoring'>('hierarchy')
  
  const [filters, setFilters] = useState<WorkItemFilters>({
    search: '',
    priority: [],
    type: [],
    assignee: [],
    status: []
  })

  // Load work items
  useEffect(() => {
    loadWorkItems()
  }, [])

  // Apply filters
  useEffect(() => {
    applyFilters()
  }, [workItems, filters])

  const loadWorkItems = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Generate sample work items since backend might not have work-items endpoint yet
      const sampleWorkItems = generateSampleWorkItems()
      
      // Calculate QVF scores
      const qvfResponse = await qvfAPI.calculateScores({
        work_items: sampleWorkItems
      })
      
      // Merge QVF scores with work items
      const itemsWithScores = sampleWorkItems.map(item => {
        const scoreData = qvfResponse.scores.find(score => score.work_item_id === item.id)
        return {
          ...item,
          qvf_score: scoreData?.qvf_score,
          priority_tier: scoreData?.priority_tier
        }
      })
      
      setWorkItems(itemsWithScores)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load work items')
    } finally {
      setLoading(false)
    }
  }

  const generateSampleWorkItems = (): ExtendedWorkItem[] => {
    return [
      // Epics
      {
        id: 'epic-1',
        title: 'Customer Portal Enhancement',
        business_value: 85,
        technical_complexity: 65,
        story_points: 55,
        priority: 'High' as const,
        risk_level: 30,
        work_item_type: 'Epic',
        state: 'Active',
        assigned_to: 'Product Team',
        created_date: '2024-01-15',
        modified_date: '2024-08-01'
      },
      {
        id: 'epic-2', 
        title: 'API Security Improvements',
        business_value: 75,
        technical_complexity: 80,
        story_points: 34,
        priority: 'High' as const,
        risk_level: 45,
        work_item_type: 'Epic',
        state: 'Active',
        assigned_to: 'Security Team',
        created_date: '2024-01-20',
        modified_date: '2024-07-28'
      },
      {
        id: 'epic-3',
        title: 'Mobile App Development',
        business_value: 90,
        technical_complexity: 85,
        story_points: 89,
        priority: 'Medium' as const,
        risk_level: 60,
        work_item_type: 'Epic',
        state: 'New',
        assigned_to: 'Mobile Team',
        created_date: '2024-02-01',
        modified_date: '2024-08-05'
      },
      // Features  
      {
        id: 'feature-1',
        title: 'Single Sign-On Integration',
        business_value: 80,
        technical_complexity: 70,
        story_points: 21,
        priority: 'High' as const,
        risk_level: 35,
        work_item_type: 'Feature',
        parent_id: 'epic-1',
        state: 'Active',
        assigned_to: 'Auth Team',
        created_date: '2024-01-18',
        modified_date: '2024-07-30'
      },
      {
        id: 'feature-2',
        title: 'Advanced Dashboard Analytics',
        business_value: 70,
        technical_complexity: 60,
        story_points: 18,
        priority: 'Medium' as const,
        risk_level: 25,
        work_item_type: 'Feature',
        parent_id: 'epic-1',
        state: 'Active',
        assigned_to: 'Analytics Team',
        created_date: '2024-01-22',
        modified_date: '2024-08-02'
      },
      // User Stories
      {
        id: 'story-1',
        title: 'As a user I want to login with my corporate credentials',
        business_value: 85,
        technical_complexity: 55,
        story_points: 8,
        priority: 'High' as const,
        risk_level: 20,
        work_item_type: 'User Story',
        parent_id: 'feature-1',
        state: 'Active',
        assigned_to: 'John Doe',
        created_date: '2024-01-25',
        modified_date: '2024-08-01'
      },
      {
        id: 'story-2',
        title: 'As an admin I want to see user access patterns',
        business_value: 65,
        technical_complexity: 45,
        story_points: 5,
        priority: 'Medium' as const,
        risk_level: 15,
        work_item_type: 'User Story',
        parent_id: 'feature-2',
        state: 'New',
        assigned_to: 'Jane Smith',
        created_date: '2024-01-28',
        modified_date: '2024-07-25'
      }
    ]
  }

  const applyFilters = () => {
    let filtered = [...workItems]
    
    // Search filter
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase()
      filtered = filtered.filter(item => 
        item.title.toLowerCase().includes(searchTerm) ||
        item.assigned_to?.toLowerCase().includes(searchTerm) ||
        item.id.toLowerCase().includes(searchTerm)
      )
    }
    
    // Priority filter
    if (filters.priority.length > 0) {
      filtered = filtered.filter(item => filters.priority.includes(item.priority))
    }
    
    // Type filter
    if (filters.type.length > 0) {
      filtered = filtered.filter(item => 
        item.work_item_type && filters.type.includes(item.work_item_type)
      )
    }
    
    // Status filter
    if (filters.status.length > 0) {
      filtered = filtered.filter(item => 
        item.state && filters.status.includes(item.state)
      )
    }
    
    setFilteredItems(filtered)
  }

  const handleCreateWorkItem = (type: 'Epic' | 'Feature' | 'User Story', parentId?: string) => {
    // This would open a creation dialog
    setIsEditing('new')
  }

  const handleEditWorkItem = (id: string) => {
    setIsEditing(id)
  }

  const handleDeleteWorkItem = async (id: string) => {
    if (confirm('Are you sure you want to delete this work item?')) {
      try {
        // await workItemsAPI.delete(id)
        setWorkItems(prev => prev.filter(item => item.id !== id))
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete work item')
      }
    }
  }

  const handleBulkOperation = async (operation: string, itemIds: string[]) => {
    try {
      switch (operation) {
        case 'recalculate-qvf':
          const itemsToScore = workItems.filter(item => itemIds.includes(item.id))
          const qvfResponse = await qvfAPI.calculateScores({ work_items: itemsToScore })
          
          setWorkItems(prev => prev.map(item => {
            if (itemIds.includes(item.id)) {
              const scoreData = qvfResponse.scores.find(score => score.work_item_id === item.id)
              return {
                ...item,
                qvf_score: scoreData?.qvf_score,
                priority_tier: scoreData?.priority_tier
              }
            }
            return item
          }))
          break
          
        case 'bulk-edit':
          // Open bulk edit dialog
          break
          
        case 'export':
          setShowExport(true)
          break
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Bulk operation failed')
    }
  }

  const handleExport = (format: 'pdf' | 'excel', items: ExtendedWorkItem[]) => {
    // Export functionality would be implemented here
    console.log(`Exporting ${items.length} items as ${format}`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search work items..."
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                  className="pl-10"
                />
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </Button>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={loadWorkItems}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowExport(true)}
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              
              <Button size="sm" onClick={() => handleCreateWorkItem('Epic')}>
                <Plus className="h-4 w-4 mr-2" />
                New Epic
              </Button>
            </div>
          </div>
          
          {/* Selected Items Actions */}
          {selectedItems.size > 0 && (
            <div className="mt-4 p-3 bg-accent rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  {selectedItems.size} item{selectedItems.size === 1 ? '' : 's'} selected
                </span>
                <BulkOperations
                  selectedItems={Array.from(selectedItems)}
                  onOperation={handleBulkOperation}
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Filters Panel */}
      {showFilters && (
        <WorkItemFilters
          filters={filters}
          onFiltersChange={setFilters}
          workItems={workItems}
        />
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Tabs value={activeView} onValueChange={(value) => setActiveView(value as any)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="hierarchy">Hierarchy View</TabsTrigger>
          <TabsTrigger value="list">List View</TabsTrigger>
          <TabsTrigger value="scoring">QVF Scoring</TabsTrigger>
        </TabsList>
        
        <TabsContent value="hierarchy" className="space-y-4">
          <WorkItemHierarchy
            workItems={filteredItems}
            selectedItems={selectedItems}
            onSelectionChange={setSelectedItems}
            onEdit={handleEditWorkItem}
            onDelete={handleDeleteWorkItem}
            onCreate={handleCreateWorkItem}
          />
        </TabsContent>
        
        <TabsContent value="list" className="space-y-4">
          {/* List view implementation */}
          <Card>
            <CardHeader>
              <CardTitle>Work Items List</CardTitle>
              <CardDescription>
                Flat view of all work items with sorting and filtering
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center text-muted-foreground py-8">
                List view implementation coming soon...
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="scoring" className="space-y-4">
          <QVFScoringInterface
            workItems={filteredItems}
            onScoreUpdate={(itemId, scores) => {
              setWorkItems(prev => prev.map(item => 
                item.id === itemId ? { ...item, ...scores } : item
              ))
            }}
          />
        </TabsContent>
      </Tabs>

      {/* Dialogs */}
      {isEditing && (
        <WorkItemEditor
          workItemId={isEditing === 'new' ? undefined : isEditing}
          onSave={() => {
            setIsEditing(null)
            loadWorkItems()
          }}
          onCancel={() => setIsEditing(null)}
        />
      )}
      
      {showExport && (
        <ExportDialog
          workItems={selectedItems.size > 0 
            ? filteredItems.filter(item => selectedItems.has(item.id))
            : filteredItems
          }
          onExport={handleExport}
          onClose={() => setShowExport(false)}
        />
      )}
    </div>
  )
}