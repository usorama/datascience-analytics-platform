'use client'

import { ProtectedRoute } from '@/components/auth/protected-route'
import { ProductOwnerDashboard } from '@/components/dashboards/product-owner-dashboard'

export default function ProductOwnerPage() {
  return (
    <ProtectedRoute requiredRole="product_owner">
      <ProductOwnerDashboard />
    </ProtectedRoute>
  )
}