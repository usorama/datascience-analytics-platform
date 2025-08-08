'use client'

import { StakeholderComparisonInterface } from '@/components/comparison/stakeholder-comparison-interface'
import { ProtectedRoute } from '@/components/auth/protected-route'

export default function ComparePage() {
  return (
    <ProtectedRoute allowedRoles={['executive', 'product_owner']}>
      <div className="container mx-auto py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">QVF Stakeholder Comparison</h1>
          <p className="text-muted-foreground">
            Use pairwise comparisons to establish QVF criteria weights based on stakeholder preferences
          </p>
        </div>
        <StakeholderComparisonInterface />
      </div>
    </ProtectedRoute>
  )
}