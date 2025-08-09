'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/auth'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Sun, Moon, Monitor } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()
  const [showDemo, setShowDemo] = useState(false)

  useEffect(() => {
    // Small delay to show theme demo before redirecting
    const timer = setTimeout(() => {
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
        // Show demo momentarily, then redirect to login
        setShowDemo(true)
        setTimeout(() => {
          router.push('/login')
        }, 3000) // Show demo for 3 seconds
      }
    }, 500)

    return () => clearTimeout(timer)
  }, [isAuthenticated, user, router])

  // Show theme demo for unauthenticated users
  if (showDemo && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        {/* Theme Toggle - Positioned in top right */}
        <div className="fixed top-4 right-4 z-10">
          <ThemeToggle size="lg" variant="outline" />
        </div>
        
        <div className="max-w-2xl w-full space-y-8">
          <Card className="border-2">
            <CardHeader className="text-center">
              <CardTitle className="text-4xl bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                QVF Platform
              </CardTitle>
              <CardDescription className="text-lg mt-2">
                Quality Value Framework - Try the theme toggle!
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-secondary/30">
                  <CardContent className="p-4 text-center">
                    <Sun className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
                    <p className="text-sm text-muted-foreground">Light Theme</p>
                  </CardContent>
                </Card>
                <Card className="bg-secondary/30">
                  <CardContent className="p-4 text-center">
                    <Moon className="h-8 w-8 mx-auto mb-2 text-blue-400" />
                    <p className="text-sm text-muted-foreground">Dark Theme</p>
                  </CardContent>
                </Card>
                <Card className="bg-secondary/30">
                  <CardContent className="p-4 text-center">
                    <Monitor className="h-8 w-8 mx-auto mb-2 text-green-500" />
                    <p className="text-sm text-muted-foreground">System</p>
                  </CardContent>
                </Card>
              </div>
              
              <div className="text-center">
                <p className="text-muted-foreground mb-4">
                  Redirecting to login in a few seconds...
                </p>
                <Button 
                  onClick={() => router.push('/login')}
                  className="bg-primary hover:bg-primary/90"
                >
                  Go to Login Now
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Show loading spinner while processing redirect
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto"></div>
        <p className="text-muted-foreground">Initializing QVF Platform...</p>
      </div>
    </div>
  )
}