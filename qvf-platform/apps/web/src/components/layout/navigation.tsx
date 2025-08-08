'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/lib/auth'
import { 
  BarChart3, 
  Users, 
  Target, 
  Settings, 
  LogOut, 
  User,
  Home,
  GitBranch,
  Calendar,
  TrendingUp,
  Scale
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavigationItem {
  label: string
  href: string
  icon: React.ReactNode
  roles: string[]
}

const navigationItems: NavigationItem[] = [
  {
    label: 'Home',
    href: '/dashboard',
    icon: <Home className="h-4 w-4" />,
    roles: ['executive', 'product_owner', 'scrum_master', 'developer']
  },
  {
    label: 'Executive Dashboard',
    href: '/dashboard/executive',
    icon: <TrendingUp className="h-4 w-4" />,
    roles: ['executive']
  },
  {
    label: 'Product Owner Dashboard',
    href: '/dashboard/product-owner',
    icon: <Target className="h-4 w-4" />,
    roles: ['product_owner']
  },
  {
    label: 'Scrum Master Dashboard',
    href: '/dashboard/scrum-master',
    icon: <Users className="h-4 w-4" />,
    roles: ['scrum_master']
  },
  {
    label: 'Work Items',
    href: '/work-items',
    icon: <GitBranch className="h-4 w-4" />,
    roles: ['product_owner', 'scrum_master', 'developer']
  },
  {
    label: 'QVF Comparison',
    href: '/compare',
    icon: <Scale className="h-4 w-4" />,
    roles: ['executive', 'product_owner']
  },
  {
    label: 'Analytics',
    href: '/analytics',
    icon: <BarChart3 className="h-4 w-4" />,
    roles: ['executive', 'product_owner', 'scrum_master']
  },
  {
    label: 'Planning',
    href: '/planning',
    icon: <Calendar className="h-4 w-4" />,
    roles: ['product_owner', 'scrum_master']
  }
]

export function Navigation() {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()

  if (!user) return null

  const userNavItems = navigationItems.filter(item => 
    item.roles.includes(user.role)
  )

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  return (
    <nav className="border-b bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/dashboard" className="flex items-center">
              <div className="text-2xl font-bold text-primary mr-8">
                QVF Platform
              </div>
            </Link>
            
            <div className="hidden md:flex items-center space-x-4">
              {userNavItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    pathname === item.href
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  )}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              ))}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              <span>{user.full_name}</span>
              <span className="text-xs bg-secondary px-2 py-1 rounded">
                {user.role.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
            
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      <div className="md:hidden border-t bg-card">
        <div className="px-2 py-2 space-y-1">
          {userNavItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                pathname === item.href
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}