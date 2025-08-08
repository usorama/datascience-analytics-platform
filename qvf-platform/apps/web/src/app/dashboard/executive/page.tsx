'use client'

import { ProtectedRoute } from '@/components/auth/protected-route'
import { ExecutiveDashboard } from '@/components/dashboards/executive-dashboard'

export default function ExecutivePage() {
  return (
    <ProtectedRoute requiredRole="executive">
      <ExecutiveDashboard />
    </ProtectedRoute>
  )
}