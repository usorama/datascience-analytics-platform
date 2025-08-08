'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface QuadrantData {
  label: string
  description?: string
  count: number
  color?: 'primary' | 'success' | 'warning' | 'error'
}

interface PriorityMatrixProps {
  title?: string
  description?: string
  quadrants: {
    topLeft: QuadrantData
    topRight: QuadrantData
    bottomLeft: QuadrantData
    bottomRight: QuadrantData
  }
  className?: string
}

const PriorityMatrix: React.FC<PriorityMatrixProps> = ({
  title = "Priority Distribution",
  description,
  quadrants,
  className
}) => {
  const getColorClasses = (color: string = 'primary') => {
    const colors = {
      primary: 'border-primary/30 hover:border-primary hover:glow-cyan',
      success: 'border-green-400/30 hover:border-green-400',
      warning: 'border-yellow-400/30 hover:border-yellow-400', 
      error: 'border-red-400/30 hover:border-red-400'
    }
    return colors[color as keyof typeof colors] || colors.primary
  }

  const QuadrantCard: React.FC<{ data: QuadrantData; className?: string }> = ({ 
    data, 
    className: quadrantClassName 
  }) => (
    <div className={cn(
      "glass-light rounded-lg md:rounded-xl p-2 md:p-4 transition-all duration-300 hover:scale-[1.02] cursor-pointer border-2",
      getColorClasses(data.color),
      quadrantClassName
    )}>
      <div className="flex flex-col justify-between h-full">
        <div>
          <div className="text-xs font-semibold text-muted-foreground mb-1 font-mono leading-tight">
            {data.label}
          </div>
          {data.description && (
            <div className="text-xs text-muted-foreground/70 mb-3">
              {data.description}
            </div>
          )}
        </div>
        <div className="text-xl md:text-2xl font-bold text-primary">
          {data.count}
        </div>
      </div>
    </div>
  )

  return (
    <Card variant="glass" className={cn('animate-slide-up', className)}>
      <CardHeader variant="with-accent">
        <CardTitle variant="chart">{title}</CardTitle>
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-2 md:gap-3 h-48 md:h-64">
          <QuadrantCard 
            data={quadrants.topLeft} 
            className="row-start-1 col-start-1"
          />
          <QuadrantCard 
            data={quadrants.topRight} 
            className="row-start-1 col-start-2"
          />
          <QuadrantCard 
            data={quadrants.bottomLeft} 
            className="row-start-2 col-start-1"
          />
          <QuadrantCard 
            data={quadrants.bottomRight} 
            className="row-start-2 col-start-2"
          />
        </div>
        
        {/* Axis Labels - Hidden on mobile for cleaner look */}
        <div className="relative mt-4 hidden md:block">
          <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 text-xs text-muted-foreground font-mono">
            High Value ↑
          </div>
          <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 text-xs text-muted-foreground font-mono">
            ↓ Low Value
          </div>
          <div className="absolute top-1/2 -left-16 transform -translate-y-1/2 -rotate-90 text-xs text-muted-foreground font-mono whitespace-nowrap">
            Low Urgency ←
          </div>
          <div className="absolute top-1/2 -right-16 transform -translate-y-1/2 rotate-90 text-xs text-muted-foreground font-mono whitespace-nowrap">
            → High Urgency
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export { PriorityMatrix }