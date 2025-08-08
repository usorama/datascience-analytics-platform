'use client'

import { WorkItemManagement } from '@/components/work-items/work-item-management'
import { ProtectedRoute } from '@/components/auth/protected-route'

export default function WorkItemsPage() {
  return (
    <ProtectedRoute allowedRoles={['product_owner', 'scrum_master', 'developer']}>
      <div className="container mx-auto py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">Work Item Management</h1>
          <p className="text-muted-foreground">
            Manage your work items hierarchy with QVF scoring and prioritization
          </p>
        </div>
        <WorkItemManagement />
      </div>
    </ProtectedRoute>
  )
}