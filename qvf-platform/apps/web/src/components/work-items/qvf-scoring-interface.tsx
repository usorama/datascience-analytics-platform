'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { qvfAPI } from '@/lib/api'
import { Calculator, RefreshCw, TrendingUp } from 'lucide-react'

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
}

interface QVFScoringInterfaceProps {
  workItems: ExtendedWorkItem[]
  onScoreUpdate: (itemId: string, scores: Partial<ExtendedWorkItem>) => void
}

export function QVFScoringInterface({ workItems, onScoreUpdate }: QVFScoringInterfaceProps) {
  const [calculating, setCalculating] = useState(false)
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  
  const handleRecalculateAll = async () => {
    setCalculating(true)
    try {
      const qvfResponse = await qvfAPI.calculateScores({
        work_items: workItems
      })
      
      // Update each item with new scores
      qvfResponse.scores.forEach(scoreData => {
        onScoreUpdate(scoreData.work_item_id, {
          qvf_score: scoreData.qvf_score,
          priority_tier: scoreData.priority_tier
        })
      })
    } catch (err) {
      console.error('Failed to recalculate QVF scores:', err)
    } finally {
      setCalculating(false)
    }
  }
  
  const handleRecalculateSelected = async () => {
    if (selectedItems.size === 0) return
    
    setCalculating(true)
    try {
      const itemsToScore = workItems.filter(item => selectedItems.has(item.id))
      const qvfResponse = await qvfAPI.calculateScores({
        work_items: itemsToScore
      })
      
      qvfResponse.scores.forEach(scoreData => {
        onScoreUpdate(scoreData.work_item_id, {
          qvf_score: scoreData.qvf_score,
          priority_tier: scoreData.priority_tier
        })
      })
      
      setSelectedItems(new Set())
    } catch (err) {
      console.error('Failed to recalculate selected scores:', err)
    } finally {
      setCalculating(false)
    }
  }
  
  const scoredItems = workItems.filter(item => item.qvf_score !== undefined)
  const unscoredItems = workItems.filter(item => item.qvf_score === undefined)
  
  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <div>
                <div className="text-2xl font-bold">{scoredItems.length}</div>
                <div className="text-sm text-muted-foreground">Items Scored</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Calculator className="h-5 w-5 text-blue-600" />
              <div>
                <div className="text-2xl font-bold">{unscoredItems.length}</div>
                <div className="text-sm text-muted-foreground">Pending Scoring</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div>
              <div className="text-2xl font-bold">
                {scoredItems.length > 0 
                  ? (scoredItems.reduce((acc, item) => acc + (item.qvf_score || 0), 0) / scoredItems.length).toFixed(2)
                  : '0.00'
                }
              </div>
              <div className="text-sm text-muted-foreground">Average QVF Score</div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle>QVF Score Management</CardTitle>
          <CardDescription>
            Calculate and update QVF scores for your work items based on quality value framework criteria
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <Button 
              onClick={handleRecalculateAll}
              disabled={calculating}
              size="lg"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${calculating ? 'animate-spin' : ''}`} />
              {calculating ? 'Calculating...' : 'Recalculate All Scores'}
            </Button>
            
            {selectedItems.size > 0 && (
              <Button 
                variant="outline"
                onClick={handleRecalculateSelected}
                disabled={calculating}
              >
                <Calculator className="h-4 w-4 mr-2" />
                Recalculate Selected ({selectedItems.size})
              </Button>
            )}
          </div>
          
          {unscoredItems.length > 0 && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="text-sm text-yellow-800">
                <strong>Note:</strong> {unscoredItems.length} work item{unscoredItems.length === 1 ? '' : 's'} 
                {unscoredItems.length === 1 ? ' has' : ' have'} no QVF scores. 
                Click "Recalculate All Scores" to generate scores for all items.
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Work Items List */}
      <Card>
        <CardHeader>
          <CardTitle>Work Items QVF Scores</CardTitle>
          <CardDescription>
            Review and manage QVF scores for individual work items
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {workItems.map(item => (
              <div
                key={item.id}
                className={`p-4 border rounded-lg hover:bg-accent/50 transition-colors ${
                  selectedItems.has(item.id) ? 'bg-accent border-primary' : 'border-border'
                }`}
                onClick={() => {
                  const newSelected = new Set(selectedItems)
                  if (newSelected.has(item.id)) {
                    newSelected.delete(item.id)
                  } else {
                    newSelected.add(item.id)
                  }
                  setSelectedItems(newSelected)
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-medium text-sm truncate">{item.title}</span>
                      <Badge variant="outline" className="text-xs">{item.id}</Badge>
                      {item.work_item_type && (
                        <Badge variant="secondary" className="text-xs">{item.work_item_type}</Badge>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Business Value</div>
                        <div className="font-medium">{item.business_value}%</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Complexity</div>
                        <div className="font-medium">{item.technical_complexity}%</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Story Points</div>
                        <div className="font-medium">{item.story_points}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Risk Level</div>
                        <div className="font-medium">{item.risk_level}%</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="ml-4 text-right">
                    {item.qvf_score ? (
                      <>
                        <div className="text-2xl font-bold text-primary">
                          {item.qvf_score.toFixed(2)}
                        </div>
                        <Badge 
                          className={`text-xs ${
                            item.priority_tier === 'High' ? 'bg-red-100 text-red-800' :
                            item.priority_tier === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}
                        >
                          {item.priority_tier} Priority
                        </Badge>
                      </>
                    ) : (
                      <div className="text-sm text-muted-foreground">
                        No QVF Score
                      </div>
                    )}
                  </div>
                </div>
                
                {/* QVF Score Visualization */}
                {item.qvf_score && (
                  <div className="mt-3 pt-3 border-t border-border">
                    <div className="text-xs text-muted-foreground mb-1">QVF Score: {item.qvf_score.toFixed(2)}</div>
                    <Progress value={item.qvf_score * 100} className="h-2" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}