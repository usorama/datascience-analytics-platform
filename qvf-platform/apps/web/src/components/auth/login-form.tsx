'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'
import { useAuthStore } from '@/lib/auth'
import { ThemeToggle } from '@/components/ui/theme-toggle'

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

export function LoginForm() {
  const router = useRouter()
  const { login, isLoading, error, clearError } = useAuthStore()
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      setSubmitError(null)
      clearError()
      
      await login(data)
      
      // Redirect based on user role
      const user = useAuthStore.getState().user
      if (user) {
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
      }
    } catch (err) {
      setSubmitError('Login failed. Please check your credentials.')
    }
  }

  const testUsers = [
    { username: 'executive', password: 'executive123', role: 'Executive' },
    { username: 'product_owner', password: 'po123', role: 'Product Owner' },
    { username: 'scrum_master', password: 'sm123', role: 'Scrum Master' },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      {/* Theme Toggle - Positioned in top right */}
      <div className="fixed top-4 right-4 z-10">
        <ThemeToggle size="default" variant="outline" />
      </div>
      
      <div className="max-w-md w-full space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-center">QVF Platform</CardTitle>
            <CardDescription className="text-center">
              Sign in to access your dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div>
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  autoComplete="username"
                  className="mt-1"
                  {...register('username')}
                />
                {errors.username && (
                  <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  className="mt-1"
                  {...register('password')}
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>

              {(error || submitError) && (
                <Alert variant="destructive">
                  <AlertDescription>
                    {error || submitError}
                  </AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign in'
                )}
              </Button>
            </form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-background text-muted-foreground">Test Users</span>
                </div>
              </div>
              <div className="mt-4 space-y-2">
                {testUsers.map((user) => (
                  <Button
                    key={user.username}
                    variant="outline"
                    className="w-full text-sm"
                    onClick={() => onSubmit(user)}
                    disabled={isLoading}
                  >
                    {user.role} - {user.username}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}