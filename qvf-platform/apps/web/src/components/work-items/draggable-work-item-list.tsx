'use client'

import React, { useState, useCallback, useEffect } from 'react'
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  DragOverEvent,
  UniqueIdentifier,
  closestCenter,
  KeyboardSensor
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy
} from '@dnd-kit/sortable'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Undo2, 
  Redo2, 
  RefreshCw,
  GripVertical,
  AlertTriangle 
} from 'lucide-react'
import { SortableWorkItem } from './sortable-work-item'
import { useUndoRedoStore } from '@/lib/stores/undo-redo-store'
import { qvfAPI } from '@/lib/api'
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
  order_index?: number
}

interface DraggableWorkItemListProps {
  workItems: ExtendedWorkItem[]
  onItemsReorder: (newItems: ExtendedWorkItem[]) => void
  onQvfScoreUpdate: (itemId: string, newScore: number) => void
  className?: string
  disabled?: boolean
}

export function DraggableWorkItemList({
  workItems,
  onItemsReorder,
  onQvfScoreUpdate,
  className,
  disabled = false
}: DraggableWorkItemListProps) {
  const [activeItem, setActiveItem] = useState<ExtendedWorkItem | null>(null)
  const [isRecalculating, setIsRecalculating] = useState(false)
  const [recalculationError, setRecalculationError] = useState<string | null>(null)
  const [draggedOverIndex, setDraggedOverIndex] = useState<number | null>(null)
  
  const {
    canUndo,
    canRedo,
    undo,
    redo,
    saveState,
    clearHistory
  } = useUndoRedoStore()

  // Setup sensors for drag and drop - optimized for both mouse and touch
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Minimum 8px movement to start drag
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 250, // 250ms delay for touch to distinguish from scrolling
        tolerance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  // Sort items by order_index or fallback to original order
  const sortedItems = React.useMemo(() => {
    return [...workItems].sort((a, b) => {
      const aIndex = a.order_index ?? workItems.indexOf(a)
      const bIndex = b.order_index ?? workItems.indexOf(b)
      return aIndex - bIndex
    })
  }, [workItems])

  // Save initial state when component mounts
  useEffect(() => {
    if (workItems.length > 0) {
      saveState({
        workItems: sortedItems,
        timestamp: Date.now(),
        action: 'initial'
      })
    }
  }, []) // Only run once on mount

  const handleDragStart = useCallback((event: DragStartEvent) => {
    const { active } = event
    const item = sortedItems.find(item => item.id === active.id)
    setActiveItem(item || null)
    setRecalculationError(null)
  }, [sortedItems])

  const handleDragOver = useCallback((event: DragOverEvent) => {
    const { active, over } = event
    
    if (over && active.id !== over.id) {
      const activeIndex = sortedItems.findIndex(item => item.id === active.id)
      const overIndex = sortedItems.findIndex(item => item.id === over.id)
      
      setDraggedOverIndex(overIndex)
    }
  }, [sortedItems])

  const handleDragEnd = useCallback(async (event: DragEndEvent) => {
    const { active, over } = event
    
    setActiveItem(null)
    setDraggedOverIndex(null)
    
    if (!over || active.id === over.id) {
      return
    }

    const activeIndex = sortedItems.findIndex(item => item.id === active.id)
    const overIndex = sortedItems.findIndex(item => item.id === over.id)
    
    if (activeIndex === -1 || overIndex === -1) {
      return
    }

    // Save current state before making changes
    saveState({
      workItems: sortedItems,
      timestamp: Date.now(),
      action: 'drag_reorder'
    })

    // Create new order
    const newItems = [...sortedItems]
    const [reorderedItem] = newItems.splice(activeIndex, 1)
    newItems.splice(overIndex, 0, reorderedItem)
    
    // Update order indices
    const itemsWithNewOrder = newItems.map((item, index) => ({
      ...item,
      order_index: index
    }))

    // Update the parent state immediately for responsive UI
    onItemsReorder(itemsWithNewOrder)

    // Recalculate QVF scores in background
    await recalculateQvfScores(itemsWithNewOrder)
  }, [sortedItems, onItemsReorder, saveState])

  const recalculateQvfScores = async (reorderedItems: ExtendedWorkItem[]) => {
    try {
      setIsRecalculating(true)
      setRecalculationError(null)

      // Call QVF API to recalculate scores based on new order
      const response = await qvfAPI.calculateScores({
        work_items: reorderedItems.map(item => ({
          id: item.id,
          title: item.title,
          business_value: item.business_value,
          technical_complexity: item.technical_complexity,
          story_points: item.story_points,
          priority: item.priority,
          risk_level: item.risk_level,
          state: item.state,
          assigned_to: item.assigned_to,
          created_date: item.created_date,
          modified_date: item.modified_date
        }))
      })

      // Update QVF scores
      response.scores.forEach(scoreData => {
        onQvfScoreUpdate(scoreData.work_item_id, scoreData.qvf_score)
      })

    } catch (error) {
      console.error('Failed to recalculate QVF scores:', error)
      setRecalculationError(
        error instanceof Error 
          ? `Failed to update QVF scores: ${error.message}` 
          : 'Failed to update QVF scores after reordering'
      )
    } finally {
      setIsRecalculating(false)
    }
  }

  const handleUndo = useCallback(() => {
    const previousState = undo()
    if (previousState) {
      onItemsReorder(previousState.workItems)
    }
  }, [undo, onItemsReorder])

  const handleRedo = useCallback(() => {
    const nextState = redo()
    if (nextState) {
      onItemsReorder(nextState.workItems)
    }
  }, [redo, onItemsReorder])

  const getItemIds = () => sortedItems.map(item => item.id as UniqueIdentifier)

  if (sortedItems.length === 0) {
    return (
      <Card className={className}>
        <CardContent className="p-8 text-center text-muted-foreground">
          No work items available for prioritization
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span>Priority Queue</span>
            {isRecalculating && (
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Updating QVF scores...</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleUndo}
              disabled={!canUndo || disabled}
            >
              <Undo2 className="h-4 w-4" />
            </Button>
            <Button
              variant="outline" 
              size="sm"
              onClick={handleRedo}
              disabled={!canRedo || disabled}
            >
              <Redo2 className="h-4 w-4" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent>
        {recalculationError && (
          <Alert variant="destructive" className="mb-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{recalculationError}</AlertDescription>
          </Alert>
        )}

        {!disabled && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-sm text-blue-800">
              <strong>Drag and Drop Instructions:</strong>
              <ul className="mt-1 space-y-1">
                <li>• Drag work items to reorder by priority</li>
                <li>• Higher position = higher priority</li>
                <li>• QVF scores will update automatically</li>
                <li>• Use undo/redo buttons to revert changes</li>
              </ul>
            </div>
          </div>
        )}

        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={getItemIds()}
            strategy={verticalListSortingStrategy}
          >
            <div className="space-y-2">
              {sortedItems.map((item, index) => (
                <SortableWorkItem
                  key={item.id}
                  item={item}
                  index={index}
                  disabled={disabled}
                  isDraggedOver={draggedOverIndex === index}
                  isRecalculating={isRecalculating}
                />
              ))}
            </div>
          </SortableContext>

          <DragOverlay>
            {activeItem ? (
              <div className="transform rotate-3 opacity-95">
                <SortableWorkItem
                  item={activeItem}
                  index={0}
                  disabled={false}
                  isDraggedOver={false}
                  isRecalculating={false}
                  isDragging={true}
                />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>

        <div className="mt-4 text-xs text-muted-foreground text-center">
          {sortedItems.length} items • Drag to reorder by priority
        </div>
      </CardContent>
    </Card>
  )
}