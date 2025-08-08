'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { CheckCircle2, AlertTriangle, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ConsistencyIndicatorProps {
  ratio: number
  isComplete: boolean
}

export function ConsistencyIndicator({ ratio, isComplete }: ConsistencyIndicatorProps) {
  const getConsistencyStatus = () => {
    if (!isComplete) {
      return {
        status: 'pending',
        label: 'Pending',
        description: 'Complete all comparisons to calculate consistency',
        color: 'text-muted-foreground',
        icon: <Clock className="h-4 w-4" />
      }
    }
    
    if (ratio <= 0.1) {
      return {
        status: 'consistent',
        label: 'Consistent',
        description: 'Your comparisons are logically consistent',
        color: 'text-green-600',
        icon: <CheckCircle2 className="h-4 w-4" />
      }
    }
    
    return {
      status: 'inconsistent', 
      label: 'Inconsistent',
      description: 'Your comparisons may have logical inconsistencies',
      color: 'text-red-600',
      icon: <AlertTriangle className="h-4 w-4" />
    }
  }

  const status = getConsistencyStatus()
  
  // Convert ratio to percentage for display (cap at 100%)
  const displayPercentage = Math.min((ratio / 0.2) * 100, 100) // 0.2 = very poor consistency
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Consistency Check</span>
          <div className={cn("flex items-center space-x-1", status.color)}>
            {status.icon}
            <Badge 
              variant={status.status === 'consistent' ? 'default' : 
                      status.status === 'inconsistent' ? 'destructive' : 'secondary'}
            >
              {status.label}
            </Badge>
          </div>
        </CardTitle>
        <CardDescription>
          {status.description}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Consistency Ratio Display */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <span>Consistency Ratio</span>
            <span className={cn("font-mono", status.color)}>
              {isComplete ? ratio.toFixed(3) : '---'}
            </span>
          </div>
          
          <div className="relative">
            <Progress 
              value={isComplete ? displayPercentage : 0} 
              className={cn(
                "h-3",
                status.status === 'consistent' && "[&>div]:bg-green-500",
                status.status === 'inconsistent' && "[&>div]:bg-red-500"
              )}
            />
            {/* Threshold marker at 10% */}
            <div 
              className="absolute top-0 bottom-0 w-0.5 bg-border"
              style={{ left: '50%' }} // 0.1/0.2 = 50%
            />
          </div>
          
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Excellent (≤0.10)</span>
            <span>Poor (≥0.20)</span>
          </div>
        </div>

        {/* Explanation */}
        <div className="text-sm space-y-2">
          <div className="font-medium">Consistency Guidelines:</div>
          <ul className="space-y-1 text-muted-foreground">
            <li className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>≤ 0.10: Acceptable consistency</span>
            </li>
            <li className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span>0.10 - 0.15: Marginal consistency</span>
            </li>
            <li className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span>&gt; 0.15: Poor consistency</span>
            </li>
          </ul>
        </div>
        
        {isComplete && ratio > 0.1 && (
          <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <div className="text-sm text-yellow-800 dark:text-yellow-200">
              <strong>Tip:</strong> If consistency is poor, review your comparisons. 
              Look for circular preferences (A &gt; B &gt; C &gt; A) and adjust accordingly.
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}