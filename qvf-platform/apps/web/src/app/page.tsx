'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/auth'

export default function HomePage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated && user) {
      // Redirect authenticated users to their appropriate dashboard
      switch (user.role) {
        case 'executive':
          router.push('/dashboard/executive')
          break
        case 'product_owner':
          router.push('/dashboard/product-owner')
          break
        case 'scrum_master':
          router.push('/dashboard/scrum-master')
          break
        default:
          router.push('/dashboard')
          break
      }
    } else {
      // Redirect unauthenticated users to login
      router.push('/login')
    }
  }, [isAuthenticated, user, router])

  // Show loading spinner while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
    </div>
  )
}