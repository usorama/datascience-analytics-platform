'use client'

import { ProtectedRoute } from '@/components/auth/protected-route'
import { ScrumMasterDashboard } from '@/components/dashboards/scrum-master-dashboard'

export default function ScrumMasterPage() {
  return (
    <ProtectedRoute requiredRole="scrum_master">
      <ScrumMasterDashboard />
    </ProtectedRoute>
  )
}