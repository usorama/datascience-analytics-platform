'use client'

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { useAuthStore } from '@/lib/auth'
import { Navigation } from '@/components/layout/navigation'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { user, isAuthenticated } = useAuthStore()

  // Initialize auth state from localStorage on client side
  useEffect(() => {
    const token = localStorage.getItem('qvf-token')
    const userData = localStorage.getItem('qvf-user')
    
    if (token && userData && !isAuthenticated) {
      try {
        const parsedUser = JSON.parse(userData)
        useAuthStore.setState({
          user: parsedUser,
          token,
          isAuthenticated: true,
        })
      } catch (error) {
        // Clear invalid data
        localStorage.removeItem('qvf-token')
        localStorage.removeItem('qvf-user')
      }
    }
  }, [isAuthenticated])

  // Don't show navigation on login page
  const isLoginPage = pathname === '/login'
  const showNavigation = isAuthenticated && !isLoginPage

  return (
    <>
      {showNavigation && <Navigation />}
      <main className={showNavigation ? 'max-w-7xl mx-auto py-6 sm:px-6 lg:px-8' : ''}>
        {children}
      </main>
    </>
  )
}