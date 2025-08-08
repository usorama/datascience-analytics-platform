'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore, canAccessRoute } from '@/lib/auth'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: string
  allowedRoutes?: string[]
  allowedRoles?: string[]
}

export function ProtectedRoute({ 
  children, 
  requiredRole, 
  allowedRoutes,
  allowedRoles
}: ProtectedRouteProps) {
  const router = useRouter()
  const { user, isAuthenticated, isLoading } = useAuthStore()

  useEffect(() => {
    // If not authenticated, redirect to login
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
      return
    }

    // If authenticated, check role-based permissions
    if (user) {
      // Check specific role requirement
      if (requiredRole && user.role !== requiredRole) {
        router.push('/unauthorized')
        return
      }

      // Check allowed roles
      if (allowedRoles && !allowedRoles.includes(user.role)) {
        router.push('/unauthorized')
        return
      }

      // Check route-based permissions
      if (allowedRoutes) {
        const currentPath = window.location.pathname
        const hasAccess = allowedRoutes.some(route => 
          canAccessRoute(user.role, currentPath)
        )
        
        if (!hasAccess) {
          router.push('/unauthorized')
          return
        }
      }
    }
  }, [user, isAuthenticated, isLoading, router, requiredRole, allowedRoutes, allowedRoles])

  // Show loading spinner while checking authentication
  if (isLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}