'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface KPICardProps {
  title: string
  value: string | number
  description?: string
  trend?: {
    direction: 'up' | 'down' | 'neutral'
    value: string
    label: string
  }
  icon?: React.ReactNode
  variant?: 'default' | 'glass' | 'glow'
  className?: string
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  description,
  trend,
  icon,
  variant = 'glass',
  className
}) => {
  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'up':
        return <TrendingUp className="h-4 w-4" />
      case 'down':
        return <TrendingDown className="h-4 w-4" />
      default:
        return <Minus className="h-4 w-4" />
    }
  }

  const getTrendStyles = (direction: string) => {
    switch (direction) {
      case 'up':
        return 'text-green-400 bg-green-400/10 border-green-400/20'
      case 'down':
        return 'text-red-400 bg-red-400/10 border-red-400/20'
      default:
        return 'text-muted-foreground bg-muted/10 border-muted/20'
    }
  }

  return (
    <Card variant={variant} className={cn('animate-slide-up', className)}>
      <CardHeader 
        variant="with-accent" 
        className="flex flex-row items-center justify-between space-y-0 pb-3"
      >
        <CardTitle variant="kpi" className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon && (
          <div className="text-muted-foreground">
            {icon}
          </div>
        )}
      </CardHeader>
      <CardContent className="pb-6">
        <div className="space-y-3">
          <div className="text-3xl font-bold text-primary tracking-tight">
            {value}
          </div>
          
          {description && (
            <p className="text-xs text-muted-foreground font-mono">
              {description}
            </p>
          )}
          
          {trend && (
            <div className={cn(
              "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border w-fit transition-all duration-300",
              getTrendStyles(trend.direction)
            )}>
              {getTrendIcon(trend.direction)}
              <span>{trend.value} {trend.label}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export { KPICard }