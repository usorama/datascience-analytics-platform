'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { qvfAPI, QVFCriteria } from '@/lib/api'
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Save, 
  CheckCircle2, 
  AlertTriangle,
  Info,
  ArrowLeft,
  ArrowRight
} from 'lucide-react'
import { PairwiseComparisonMatrix } from './pairwise-comparison-matrix'
import { ConsistencyIndicator } from './consistency-indicator'
import { ComparisonProgress } from './comparison-progress'

// AHP scale for pairwise comparisons
const AHP_SCALE = [
  { value: 1/9, label: '1/9', description: 'Extremely less important' },
  { value: 1/7, label: '1/7', description: 'Very strongly less important' },
  { value: 1/5, label: '1/5', description: 'Strongly less important' },
  { value: 1/3, label: '1/3', description: 'Moderately less important' },
  { value: 1, label: '1', description: 'Equally important' },
  { value: 3, label: '3', description: 'Moderately more important' },
  { value: 5, label: '5', description: 'Strongly more important' },
  { value: 7, label: '7', description: 'Very strongly more important' },
  { value: 9, label: '9', description: 'Extremely more important' }
]

interface ComparisonSession {
  id: string
  criteria: QVFCriteria[]
  comparisons: Record<string, number>
  currentPair: [number, number] | null
  completedPairs: Array<[number, number]>
  consistencyRatio: number
  weights: Record<string, number>
  createdAt: string
  updatedAt: string
}

export function StakeholderComparisonInterface() {
  const [criteria, setCriteria] = useState<QVFCriteria[]>([])
  const [session, setSession] = useState<ComparisonSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isActive, setIsActive] = useState(false)

  // Load criteria and existing session
  useEffect(() => {
    loadCriteriaAndSession()
  }, [])

  const loadCriteriaAndSession = async () => {
    try {
      setLoading(true)
      const criteriaData = await qvfAPI.getCriteria()
      setCriteria(criteriaData)
      
      // Try to load existing session from localStorage
      const savedSession = localStorage.getItem('qvf-comparison-session')
      if (savedSession) {
        const parsedSession = JSON.parse(savedSession)
        setSession(parsedSession)
      } else {
        // Create new session
        createNewSession(criteriaData)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load criteria')
    } finally {
      setLoading(false)
    }
  }

  const createNewSession = (criteriaData: QVFCriteria[]) => {
    const pairs = generatePairs(criteriaData.length)
    const newSession: ComparisonSession = {
      id: `session-${Date.now()}`,
      criteria: criteriaData,
      comparisons: {},
      currentPair: pairs.length > 0 ? pairs[0] : null,
      completedPairs: [],
      consistencyRatio: 0,
      weights: {},
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    setSession(newSession)
    saveSession(newSession)
  }

  const generatePairs = (n: number): Array<[number, number]> => {
    const pairs: Array<[number, number]> = []
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        pairs.push([i, j])
      }
    }
    return pairs
  }

  const saveSession = (sessionData: ComparisonSession) => {
    localStorage.setItem('qvf-comparison-session', JSON.stringify(sessionData))
  }

  const handleComparisonSubmit = async (criteriaA: string, criteriaB: string, value: number) => {
    if (!session) return

    const comparisonKey = `${criteriaA}-${criteriaB}`
    const updatedComparisons = {
      ...session.comparisons,
      [comparisonKey]: value
    }

    // Update completed pairs
    const currentPairIndex = session.currentPair ? 
      session.criteria.findIndex(c => c.criterion_id === criteriaA) : -1
    const currentPairJIndex = session.currentPair ?
      session.criteria.findIndex(c => c.criterion_id === criteriaB) : -1
    
    const updatedCompletedPairs = session.currentPair ?
      [...session.completedPairs, session.currentPair] : session.completedPairs

    // Find next pair
    const allPairs = generatePairs(session.criteria.length)
    const remainingPairs = allPairs.filter(pair => 
      !updatedCompletedPairs.some(completed => 
        (completed[0] === pair[0] && completed[1] === pair[1])
      )
    )
    const nextPair = remainingPairs.length > 0 ? remainingPairs[0] : null

    // Calculate consistency ratio and weights
    const { consistencyRatio, weights } = calculateConsistencyAndWeights(updatedComparisons, session.criteria)

    const updatedSession: ComparisonSession = {
      ...session,
      comparisons: updatedComparisons,
      currentPair: nextPair,
      completedPairs: updatedCompletedPairs,
      consistencyRatio,
      weights,
      updatedAt: new Date().toISOString()
    }

    setSession(updatedSession)
    saveSession(updatedSession)
  }

  const calculateConsistencyAndWeights = (comparisons: Record<string, number>, criteriaList: QVFCriteria[]) => {
    const n = criteriaList.length
    const matrix = Array(n).fill(0).map(() => Array(n).fill(1))

    // Fill the matrix with comparisons
    criteriaList.forEach((criteriaA, i) => {
      criteriaList.forEach((criteriaB, j) => {
        if (i !== j) {
          const keyAB = `${criteriaA.criterion_id}-${criteriaB.criterion_id}`
          const keyBA = `${criteriaB.criterion_id}-${criteriaA.criterion_id}`
          
          if (comparisons[keyAB]) {
            matrix[i][j] = comparisons[keyAB]
            matrix[j][i] = 1 / comparisons[keyAB]
          } else if (comparisons[keyBA]) {
            matrix[i][j] = 1 / comparisons[keyBA]
            matrix[j][i] = comparisons[keyBA]
          }
        }
      })
    })

    // Calculate eigenvector (simplified method - geometric mean)
    const weights: Record<string, number> = {}
    const geometricMeans: number[] = []
    
    for (let i = 0; i < n; i++) {
      let product = 1
      for (let j = 0; j < n; j++) {
        product *= matrix[i][j]
      }
      geometricMeans[i] = Math.pow(product, 1/n)
    }

    const sum = geometricMeans.reduce((acc, val) => acc + val, 0)
    criteriaList.forEach((criteria, i) => {
      weights[criteria.criterion_id] = geometricMeans[i] / sum
    })

    // Calculate consistency ratio (simplified)
    let lambdaMax = 0
    for (let i = 0; i < n; i++) {
      let sum = 0
      for (let j = 0; j < n; j++) {
        sum += matrix[i][j] * (geometricMeans[j] / geometricMeans.reduce((acc, val) => acc + val, 0))
      }
      lambdaMax += sum * (geometricMeans[i] / geometricMeans.reduce((acc, val) => acc + val, 0))
    }

    const consistencyIndex = (lambdaMax - n) / (n - 1)
    const randomIndex = [0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49][n] || 1.49
    const consistencyRatio = consistencyIndex / randomIndex

    return { consistencyRatio: isNaN(consistencyRatio) ? 0 : consistencyRatio, weights }
  }

  const resetSession = () => {
    if (criteria.length > 0) {
      createNewSession(criteria)
      setIsActive(false)
    }
  }

  const saveWeights = async () => {
    if (!session) return
    
    try {
      setSaving(true)
      // Here you would save the weights to your backend
      // await api.post('/api/v1/qvf/weights', { weights: session.weights })
      
      // For now, just save to localStorage
      localStorage.setItem('qvf-stakeholder-weights', JSON.stringify(session.weights))
      
      // Show success message
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save weights')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!session) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-muted-foreground">No comparison session available</p>
        </CardContent>
      </Card>
    )
  }

  const totalPairs = generatePairs(session.criteria.length).length
  const completedPairs = session.completedPairs.length
  const progressPercentage = totalPairs > 0 ? (completedPairs / totalPairs) * 100 : 0
  const isComplete = completedPairs === totalPairs
  const isConsistent = session.consistencyRatio <= 0.1

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-semibold">Comparison Session</h2>
                {isComplete && (
                  <Badge variant={isConsistent ? "default" : "destructive"}>
                    {isConsistent ? "Complete" : "Inconsistent"}
                  </Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground">
                {completedPairs} of {totalPairs} comparisons completed
              </p>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={resetSession}
                disabled={saving}
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset
              </Button>
              
              {isComplete && (
                <Button
                  onClick={saveWeights}
                  disabled={saving || !isConsistent}
                  size="sm"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? "Saving..." : "Save Weights"}
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Progress and Consistency */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ComparisonProgress 
          total={totalPairs}
          completed={completedPairs}
          percentage={progressPercentage}
        />
        
        <ConsistencyIndicator 
          ratio={session.consistencyRatio}
          isComplete={isComplete}
        />
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Comparison Interface */}
      {!isComplete && session.currentPair && (
        <PairwiseComparisonMatrix
          criteriaA={session.criteria[session.currentPair[0]]}
          criteriaB={session.criteria[session.currentPair[1]]}
          onSubmit={handleComparisonSubmit}
          scale={AHP_SCALE}
        />
      )}

      {/* Results */}
      {isComplete && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <CheckCircle2 className="h-5 w-5 mr-2 text-green-600" />
              Final Weights
            </CardTitle>
            <CardDescription>
              Calculated QVF criteria weights based on your pairwise comparisons
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {session.criteria.map((criteria) => {
                const weight = session.weights[criteria.criterion_id] || 0
                return (
                  <div key={criteria.criterion_id} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{criteria.name}</span>
                      <span className="text-sm text-muted-foreground">
                        {(weight * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={weight * 100} className="h-2" />
                  </div>
                )
              })}
            </div>
            
            {!isConsistent && (
              <Alert className="mt-4">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  The consistency ratio ({session.consistencyRatio.toFixed(3)}) exceeds the recommended threshold of 0.1. 
                  Consider reviewing your comparisons for logical consistency.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}