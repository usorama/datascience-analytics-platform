'use client'

import React from 'react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  GripVertical, 
  RefreshCw, 
  TrendingUp, 
  TrendingDown,
  Minus,
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
  order_index?: number
}

interface SortableWorkItemProps {
  item: ExtendedWorkItem
  index: number
  disabled?: boolean
  isDraggedOver?: boolean
  isRecalculating?: boolean
  isDragging?: boolean
}

export function SortableWorkItem({
  item,
  index,
  disabled = false,
  isDraggedOver = false,
  isRecalculating = false,
  isDragging = false
}: SortableWorkItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging
  } = useSortable({ id: item.id, disabled })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'bg-red-100 text-red-800 border-red-200'
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'  
      case 'Low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getQvfTrendIcon = (score?: number, previousScore?: number) => {
    if (!score || !previousScore) return <Minus className="h-3 w-3 text-gray-400" />
    
    if (score > previousScore) return <TrendingUp className="h-3 w-3 text-green-500" />
    if (score < previousScore) return <TrendingDown className="h-3 w-3 text-red-500" />
    return <Minus className="h-3 w-3 text-gray-400" />
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

  const getComplexityLevel = (complexity: number) => {
    if (complexity >= 80) return { label: 'Very High', color: 'text-red-600' }
    if (complexity >= 60) return { label: 'High', color: 'text-orange-600' }
    if (complexity >= 40) return { label: 'Medium', color: 'text-yellow-600' }
    if (complexity >= 20) return { label: 'Low', color: 'text-green-600' }
    return { label: 'Very Low', color: 'text-green-500' }
  }

  const complexityInfo = getComplexityLevel(item.technical_complexity)

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        'group relative transition-all duration-200',
        isDragging && 'z-50',
        isSortableDragging && 'opacity-50',
        isDraggedOver && 'transform scale-105'
      )}
    >
      {/* Priority Rank Indicator */}
      <div className="absolute -left-8 top-1/2 transform -translate-y-1/2 z-10">
        <div className={cn(
          'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
          index === 0 && 'bg-yellow-400 text-yellow-900', // Gold for #1
          index === 1 && 'bg-gray-300 text-gray-700',     // Silver for #2
          index === 2 && 'bg-orange-300 text-orange-800', // Bronze for #3
          index > 2 && 'bg-gray-100 text-gray-600'        // Regular for others
        )}>
          {index + 1}
        </div>
      </div>

      <Card className={cn(
        'hover:shadow-md transition-all duration-200 cursor-grab active:cursor-grabbing',
        disabled && 'cursor-not-allowed opacity-60',
        isDraggedOver && 'ring-2 ring-blue-400 shadow-lg',
        isSortableDragging && 'shadow-2xl ring-2 ring-blue-500',
        'ml-4' // Margin for rank indicator
      )}>
        <CardContent className="p-4">
          <div className="flex items-start space-x-4">
            {/* Drag Handle */}
            <div 
              {...attributes}
              {...listeners}
              className={cn(
                'flex flex-col items-center justify-center p-2 rounded hover:bg-gray-100',
                disabled ? 'cursor-not-allowed opacity-50' : 'cursor-grab active:cursor-grabbing'
              )}
            >
              <GripVertical className="h-5 w-5 text-gray-400" />
              <div className="text-xs text-gray-400 font-mono">
                {String(index + 1).padStart(2, '0')}
              </div>
            </div>

            {/* Work Item Content */}
            <div className="flex-1 min-w-0 space-y-3">
              {/* Header Row */}
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="font-medium text-sm truncate">{item.title}</h3>
                    <Badge variant="outline" className="text-xs">
                      {item.id}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                    {getStateIcon(item.state)}
                    {item.assigned_to && (
                      <span>👤 {item.assigned_to}</span>
                    )}
                    {item.work_item_type && (
                      <Badge className={cn("text-xs", getTypeColor(item.work_item_type))}>
                        {item.work_item_type}
                      </Badge>
                    )}
                  </div>
                </div>
                
                <Badge className={cn("text-xs", getPriorityColor(item.priority))}>
                  {item.priority}
                </Badge>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                {/* Story Points */}
                <div className="text-center">
                  <div className="font-semibold text-lg">{item.story_points}</div>
                  <div className="text-xs text-muted-foreground">Story Points</div>
                </div>

                {/* QVF Score */}
                <div className="text-center">
                  <div className="flex items-center justify-center space-x-1">
                    {isRecalculating ? (
                      <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />
                    ) : item.qvf_score ? (
                      <>
                        <span className="font-semibold text-lg">
                          {item.qvf_score.toFixed(2)}
                        </span>
                        {getQvfTrendIcon(item.qvf_score)}
                      </>
                    ) : (
                      <span className="text-gray-400">--</span>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground">QVF Score</div>
                </div>

                {/* Business Value */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-muted-foreground">Business Value</span>
                    <span className="font-medium">{item.business_value}%</span>
                  </div>
                  <Progress value={item.business_value} className="h-2" />
                </div>

                {/* Technical Complexity */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-muted-foreground">Complexity</span>
                    <span className={cn("font-medium text-xs", complexityInfo.color)}>
                      {complexityInfo.label}
                    </span>
                  </div>
                  <Progress value={item.technical_complexity} className="h-2" />
                  <div className="text-right text-xs text-muted-foreground mt-1">
                    {item.technical_complexity}%
                  </div>
                </div>
              </div>

              {/* Risk Level Indicator */}
              {item.risk_level > 50 && (
                <div className="flex items-center space-x-2 p-2 bg-red-50 border border-red-200 rounded">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-xs text-red-700">
                    High Risk: {item.risk_level}% risk level
                  </span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}