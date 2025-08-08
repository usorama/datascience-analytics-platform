'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { QVFCriteria } from '@/lib/api'
import { ArrowRight, Info } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AHPScaleItem {
  value: number
  label: string
  description: string
}

interface PairwiseComparisonMatrixProps {
  criteriaA: QVFCriteria
  criteriaB: QVFCriteria
  onSubmit: (criteriaAId: string, criteriaBId: string, value: number) => void
  scale: AHPScaleItem[]
}

export function PairwiseComparisonMatrix({
  criteriaA,
  criteriaB,
  onSubmit,
  scale
}: PairwiseComparisonMatrixProps) {
  const [selectedValue, setSelectedValue] = useState<number | null>(null)
  const [hoveredValue, setHoveredValue] = useState<number | null>(null)

  const handleSubmit = () => {
    if (selectedValue !== null) {
      onSubmit(criteriaA.criterion_id, criteriaB.criterion_id, selectedValue)
      setSelectedValue(null)
    }
  }

  const getScaleDescription = (value: number) => {
    const scaleItem = scale.find(item => item.value === value)
    return scaleItem ? scaleItem.description : ''
  }

  const getScaleLabel = (value: number) => {
    const scaleItem = scale.find(item => item.value === value)
    return scaleItem ? scaleItem.label : value.toString()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center text-lg">
          <span className="font-medium text-primary">{criteriaA.name}</span>
          <ArrowRight className="h-4 w-4 mx-2 text-muted-foreground" />
          <span className="font-medium text-primary">{criteriaB.name}</span>
        </CardTitle>
        <CardDescription>
          How important is <strong>{criteriaA.name}</strong> compared to <strong>{criteriaB.name}</strong>?
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Criteria Descriptions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Badge variant="outline">{criteriaA.category}</Badge>
              <span className="text-sm font-medium">{criteriaA.name}</span>
            </div>
            <p className="text-sm text-muted-foreground">{criteriaA.description}</p>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Badge variant="outline">{criteriaB.category}</Badge>
              <span className="text-sm font-medium">{criteriaB.name}</span>
            </div>
            <p className="text-sm text-muted-foreground">{criteriaB.description}</p>
          </div>
        </div>

        {/* Comparison Scale */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Info className="h-4 w-4" />
            <span>Select how much more important the first criterion is compared to the second</span>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {scale.map((scaleItem) => {
              const isSelected = selectedValue === scaleItem.value
              const isHovered = hoveredValue === scaleItem.value
              
              return (
                <Button
                  key={scaleItem.value}
                  variant={isSelected ? "default" : "outline"}
                  size="sm"
                  className={cn(
                    "h-auto p-3 flex flex-col items-center space-y-1 transition-all",
                    isHovered && !isSelected && "bg-accent",
                    isSelected && "ring-2 ring-primary"
                  )}
                  onClick={() => setSelectedValue(scaleItem.value)}
                  onMouseEnter={() => setHoveredValue(scaleItem.value)}
                  onMouseLeave={() => setHoveredValue(null)}
                >
                  <span className="text-lg font-bold">{scaleItem.label}</span>
                  <span className="text-xs text-center leading-tight">
                    {scaleItem.description}
                  </span>
                </Button>
              )
            })}
          </div>
          
          {/* Selected Value Description */}
          {(selectedValue !== null || hoveredValue !== null) && (
            <div className="p-4 bg-accent rounded-lg">
              <div className="flex items-center space-x-2">
                <span className="font-medium">Selection:</span>
                <Badge variant="default">
                  {getScaleLabel(hoveredValue || selectedValue!)}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                <strong>{criteriaA.name}</strong> is{" "}
                <em>{getScaleDescription(hoveredValue || selectedValue!)}</em>{" "}
                compared to <strong>{criteriaB.name}</strong>
              </p>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <Button
            onClick={handleSubmit}
            disabled={selectedValue === null}
            size="lg"
            className="min-w-[120px]"
          >
            Next Comparison
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}