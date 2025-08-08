'use client'

import React from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface InsightCardProps {
  title: string
  description: string
  icon: React.ReactNode
  variant?: 'default' | 'glass' | 'success' | 'warning' | 'error'
  className?: string
}

const InsightCard: React.FC<InsightCardProps> = ({
  title,
  description,
  icon,
  variant = 'glass',
  className
}) => {
  const getIconBackgroundColor = (variant: string) => {
    switch (variant) {
      case 'success':
        return 'bg-gradient-to-br from-green-400 to-green-500'
      case 'warning':
        return 'bg-gradient-to-br from-yellow-400 to-yellow-500'
      case 'error':
        return 'bg-gradient-to-br from-red-400 to-red-500'
      default:
        return 'bg-gradient-to-br from-primary to-accent-hover'
    }
  }

  const cardVariant = variant === 'success' || variant === 'warning' || variant === 'error' ? 'glass' : variant

  return (
    <Card variant={cardVariant} className={cn('animate-slide-up', className)}>
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <div className={cn(
            "flex items-center justify-center w-12 h-12 rounded-xl shadow-lg",
            getIconBackgroundColor(variant)
          )}>
            <div className="text-black">
              {icon}
            </div>
          </div>
          
          <div className="flex-1 space-y-2">
            <h3 className="font-semibold text-primary text-lg leading-tight">
              {title}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {description}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export { InsightCard }