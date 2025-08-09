'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Play, 
  RotateCcw, 
  Shuffle, 
  CheckCircle2,
  TrendingUp,
  Zap
} from 'lucide-react'
import { DraggableWorkItemList } from './draggable-work-item-list'
import { useUndoRedoKeyboardShortcuts } from '@/lib/stores/undo-redo-store'

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
  order_index?: number
}

export function DragDropDemo() {
  // Enable keyboard shortcuts
  useUndoRedoKeyboardShortcuts()

  const [demoWorkItems, setDemoWorkItems] = useState<ExtendedWorkItem[]>([
    {
      id: 'demo-epic-1',
      title: 'Customer Experience Transformation',
      business_value: 95,
      technical_complexity: 75,
      story_points: 89,
      priority: 'High',
      risk_level: 45,
      qvf_score: 89.2,
      priority_tier: 'High',
      work_item_type: 'Epic',
      state: 'Active',
      assigned_to: 'Product Leadership',
      order_index: 0,
      created_date: '2024-01-10',
      modified_date: '2024-08-08'
    },
    {
      id: 'demo-feature-1',
      title: 'AI-Powered Recommendation Engine',
      business_value: 88,
      technical_complexity: 85,
      story_points: 55,
      priority: 'High',
      risk_level: 60,
      qvf_score: 84.7,
      priority_tier: 'High',
      work_item_type: 'Feature',
      state: 'Active',
      assigned_to: 'ML Team',
      order_index: 1,
      created_date: '2024-01-15',
      modified_date: '2024-08-07'
    },
    {
      id: 'demo-feature-2',
      title: 'Real-time Analytics Dashboard',
      business_value: 82,
      technical_complexity: 70,
      story_points: 34,
      priority: 'High',
      risk_level: 35,
      qvf_score: 81.3,
      priority_tier: 'High',
      work_item_type: 'Feature',
      state: 'New',
      assigned_to: 'Analytics Team',
      order_index: 2,
      created_date: '2024-01-20',
      modified_date: '2024-08-06'
    },
    {
      id: 'demo-story-1',
      title: 'As a user I want personalized product recommendations',
      business_value: 75,
      technical_complexity: 55,
      story_points: 21,
      priority: 'Medium',
      risk_level: 25,
      qvf_score: 76.8,
      priority_tier: 'Medium',
      work_item_type: 'User Story',
      state: 'Active',
      assigned_to: 'Sarah Chen',
      order_index: 3,
      created_date: '2024-01-25',
      modified_date: '2024-08-05'
    },
    {
      id: 'demo-story-2',
      title: 'As an admin I want to configure dashboard widgets',
      business_value: 65,
      technical_complexity: 45,
      story_points: 13,
      priority: 'Medium',
      risk_level: 20,
      qvf_score: 71.5,
      priority_tier: 'Medium',
      work_item_type: 'User Story',
      state: 'New',
      assigned_to: 'Alex Rodriguez',
      order_index: 4,
      created_date: '2024-01-30',
      modified_date: '2024-08-04'
    },
    {
      id: 'demo-task-1',
      title: 'Implement recommendation API endpoints',
      business_value: 70,
      technical_complexity: 60,
      story_points: 8,
      priority: 'Medium',
      risk_level: 30,
      qvf_score: 69.2,
      priority_tier: 'Medium',
      work_item_type: 'Task',
      state: 'Active',
      assigned_to: 'Mike Johnson',
      order_index: 5,
      created_date: '2024-02-01',
      modified_date: '2024-08-03'
    }
  ])

  const [isShuffling, setIsShuffling] = useState(false)
  const [completedActions, setCompletedActions] = useState<string[]>([])

  const handleItemsReorder = (newItems: ExtendedWorkItem[]) => {
    setDemoWorkItems(newItems)
    if (!completedActions.includes('drag-reorder')) {
      setCompletedActions(prev => [...prev, 'drag-reorder'])
    }
  }

  const handleQvfScoreUpdate = (itemId: string, newScore: number) => {
    setDemoWorkItems(prev => prev.map(item => 
      item.id === itemId 
        ? { ...item, qvf_score: newScore }
        : item
    ))
    if (!completedActions.includes('qvf-update')) {
      setCompletedActions(prev => [...prev, 'qvf-update'])
    }
  }

  const shuffleItems = async () => {
    setIsShuffling(true)
    
    // Create a shuffled copy
    const shuffled = [...demoWorkItems]
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
    }
    
    // Update order indices
    const shuffledWithOrder = shuffled.map((item, index) => ({
      ...item,
      order_index: index
    }))
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    setDemoWorkItems(shuffledWithOrder)
    setIsShuffling(false)
    
    if (!completedActions.includes('shuffle')) {
      setCompletedActions(prev => [...prev, 'shuffle'])
    }
  }

  const resetDemo = () => {
    setDemoWorkItems(demoWorkItems.map((item, index) => ({
      ...item,
      order_index: index
    })))
    setCompletedActions([])
  }

  const getDemoProgress = () => {
    const totalActions = ['drag-reorder', 'qvf-update', 'shuffle']
    return Math.round((completedActions.length / totalActions.length) * 100)
  }

  return (
    <div className="space-y-6">
      {/* Demo Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-6 w-6 text-yellow-500" />
            <span>Drag & Drop Prioritization Demo</span>
            <Badge variant="outline" className="ml-auto">
              {getDemoProgress()}% Complete
            </Badge>
          </CardTitle>
          <CardDescription>
            Interactive demonstration of the QVF Platform&apos;s drag-and-drop work item prioritization feature.
            Try dragging items, using keyboard shortcuts (Ctrl+Z, Ctrl+Y), and watch QVF scores update in real-time.
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          {/* Demo Controls */}
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <Button
              onClick={shuffleItems}
              disabled={isShuffling}
              variant="outline"
              size="sm"
            >
              <Shuffle className={`h-4 w-4 mr-2 ${isShuffling ? 'animate-spin' : ''}`} />
              {isShuffling ? 'Shuffling...' : 'Shuffle Items'}
            </Button>
            
            <Button
              onClick={resetDemo}
              variant="outline" 
              size="sm"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset Demo
            </Button>
            
            <div className="ml-auto text-sm text-muted-foreground">
              Keyboard: Ctrl+Z (Undo) • Ctrl+Y (Redo)
            </div>
          </div>

          {/* Progress Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className={`p-3 rounded-lg border ${
              completedActions.includes('drag-reorder') 
                ? 'bg-green-50 border-green-200' 
                : 'bg-gray-50 border-gray-200'
            }`}>
              <div className="flex items-center space-x-2">
                {completedActions.includes('drag-reorder') ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <div className="h-4 w-4 rounded-full border-2 border-gray-400" />
                )}
                <span className="text-sm font-medium">Drag & Reorder Items</span>
              </div>
            </div>
            
            <div className={`p-3 rounded-lg border ${
              completedActions.includes('qvf-update') 
                ? 'bg-green-50 border-green-200' 
                : 'bg-gray-50 border-gray-200'
            }`}>
              <div className="flex items-center space-x-2">
                {completedActions.includes('qvf-update') ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <div className="h-4 w-4 rounded-full border-2 border-gray-400" />
                )}
                <span className="text-sm font-medium">QVF Score Updates</span>
              </div>
            </div>
            
            <div className={`p-3 rounded-lg border ${
              completedActions.includes('shuffle') 
                ? 'bg-green-50 border-green-200' 
                : 'bg-gray-50 border-gray-200'
            }`}>
              <div className="flex items-center space-x-2">
                {completedActions.includes('shuffle') ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <div className="h-4 w-4 rounded-full border-2 border-gray-400" />
                )}
                <span className="text-sm font-medium">Use Shuffle Feature</span>
              </div>
            </div>
          </div>

          {/* Demo Tips */}
          <Alert className="mb-6">
            <TrendingUp className="h-4 w-4" />
            <AlertDescription>
              <strong>Demo Tips:</strong>
              <ul className="mt-2 space-y-1 text-sm">
                <li>• <strong>Drag items</strong> up/down to change priority ranking</li>
                <li>• <strong>Watch QVF scores</strong> update automatically after reordering</li>
                <li>• <strong>Use undo/redo</strong> buttons or keyboard shortcuts (Ctrl+Z, Ctrl+Y)</li>
                <li>• <strong>Notice priority rankings</strong> with gold (#1), silver (#2), bronze (#3) indicators</li>
                <li>• <strong>Shuffle button</strong> randomizes order to test reordering</li>
              </ul>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Demo Component */}
      <DraggableWorkItemList
        workItems={demoWorkItems}
        onItemsReorder={handleItemsReorder}
        onQvfScoreUpdate={handleQvfScoreUpdate}
        disabled={isShuffling}
      />

      {/* Demo Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Demo Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{demoWorkItems.length}</div>
              <div className="text-sm text-muted-foreground">Work Items</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{completedActions.length}/3</div>
              <div className="text-sm text-muted-foreground">Actions Completed</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {demoWorkItems.filter(item => item.qvf_score && item.qvf_score > 80).length}
              </div>
              <div className="text-sm text-muted-foreground">High Priority Items</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {Math.round(demoWorkItems.reduce((sum, item) => sum + (item.qvf_score || 0), 0) / demoWorkItems.length)}
              </div>
              <div className="text-sm text-muted-foreground">Avg QVF Score</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}