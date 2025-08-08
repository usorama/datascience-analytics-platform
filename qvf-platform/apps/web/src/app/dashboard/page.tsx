'use client'

import { ProtectedRoute } from '@/components/auth/protected-route'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/lib/auth'
import Link from 'next/link'
import { 
  TrendingUp, 
  Users, 
  Target, 
  BarChart3,
  GitBranch,
  Calendar
} from 'lucide-react'

function GeneralDashboard() {
  const { user } = useAuthStore()

  const getDashboardCards = () => {
    const cards = []

    if (user?.role === 'executive' || user?.role === 'product_owner') {
      cards.push({
        title: 'Executive Dashboard',
        description: 'Portfolio health, strategic alignment, and value delivery insights',
        href: '/dashboard/executive',
        icon: <TrendingUp className="h-8 w-8" />,
        color: 'border-blue-200 bg-blue-50'
      })
    }

    if (user?.role === 'product_owner') {
      cards.push({
        title: 'Product Owner Dashboard',
        description: 'Epic management, release planning, and capacity insights',
        href: '/dashboard/product-owner',
        icon: <Target className="h-8 w-8" />,
        color: 'border-green-200 bg-green-50'
      })
    }

    if (user?.role === 'scrum_master') {
      cards.push({
        title: 'Scrum Master Dashboard',
        description: 'Sprint progress, team health, and impediment management',
        href: '/dashboard/scrum-master',
        icon: <Users className="h-8 w-8" />,
        color: 'border-purple-200 bg-purple-50'
      })
    }

    // Common cards for all roles
    cards.push(
      {
        title: 'Work Items',
        description: 'View and manage work items with QVF scoring',
        href: '/work-items',
        icon: <GitBranch className="h-8 w-8" />,
        color: 'border-orange-200 bg-orange-50'
      },
      {
        title: 'Analytics',
        description: 'Advanced analytics and performance metrics',
        href: '/analytics',
        icon: <BarChart3 className="h-8 w-8" />,
        color: 'border-indigo-200 bg-indigo-50'
      }
    )

    if (user?.role === 'product_owner' || user?.role === 'scrum_master') {
      cards.push({
        title: 'Planning',
        description: 'Sprint and release planning tools',
        href: '/planning',
        icon: <Calendar className="h-8 w-8" />,
        color: 'border-teal-200 bg-teal-50'
      })
    }

    return cards
  }

  const dashboardCards = getDashboardCards()

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          Welcome back, {user?.full_name}!
        </h1>
        <p className="text-muted-foreground">
          Choose a dashboard to get started with the QVF Platform
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboardCards.map((card) => (
          <Card 
            key={card.href}
            className={`hover:shadow-md transition-shadow cursor-pointer ${card.color}`}
          >
            <CardHeader>
              <div className="flex items-center gap-3">
                {card.icon}
                <CardTitle className="text-xl">{card.title}</CardTitle>
              </div>
              <CardDescription className="text-base">
                {card.description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild className="w-full">
                <Link href={card.href}>
                  Open Dashboard
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Stats */}
      <div className="mt-12">
        <Card>
          <CardHeader>
            <CardTitle>Quick Stats</CardTitle>
            <CardDescription>Your current work overview</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">12</div>
                <div className="text-sm text-muted-foreground">Active Items</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">0.78</div>
                <div className="text-sm text-muted-foreground">Avg QVF Score</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">5</div>
                <div className="text-sm text-muted-foreground">High Priority</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">2</div>
                <div className="text-sm text-muted-foreground">Active Sprints</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <GeneralDashboard />
    </ProtectedRoute>
  )
}