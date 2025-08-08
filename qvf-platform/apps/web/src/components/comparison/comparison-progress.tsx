'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { BarChart3, CheckCircle2 } from 'lucide-react'

interface ComparisonProgressProps {
  total: number
  completed: number
  percentage: number
}

export function ComparisonProgress({ total, completed, percentage }: ComparisonProgressProps) {
  const remaining = total - completed
  const isComplete = completed === total
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>Progress</span>
          </div>
          {isComplete && (
            <CheckCircle2 className="h-5 w-5 text-green-600" />
          )}
        </CardTitle>
        <CardDescription>
          Complete all pairwise comparisons to calculate final weights
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <span>Comparisons</span>
            <span className="font-mono">
              {completed} / {total}
            </span>
          </div>
          <Progress value={percentage} className="h-3" />
          <div className="text-right text-xs text-muted-foreground">
            {percentage.toFixed(1)}% complete
          </div>
        </div>

        {/* Status Badges */}
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline" className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Completed: {completed}</span>
          </Badge>
          
          {remaining > 0 && (
            <Badge variant="outline" className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Remaining: {remaining}</span>
            </Badge>
          )}
        </div>

        {/* Time Estimate */}
        {remaining > 0 && (
          <div className="text-sm text-muted-foreground">
            <div className="font-medium mb-1">Estimated time remaining:</div>
            <div className="flex items-center space-x-4">
              <span>~{Math.ceil(remaining * 0.5)} minutes</span>
              <span className="text-xs">(30 seconds per comparison)</span>
            </div>
          </div>
        )}
        
        {isComplete && (
          <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <div className="text-sm text-green-800 dark:text-green-200">
              <strong>Great!</strong> All comparisons completed. 
              Review the consistency check and save your weights when ready.
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}