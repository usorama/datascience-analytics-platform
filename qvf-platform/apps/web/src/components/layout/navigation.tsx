'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
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
  Scale,
  Menu,
  X
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { ThemeToggle } from '@/components/ui/theme-toggle'

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
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [touchStart, setTouchStart] = useState<number | null>(null)
  const [touchEnd, setTouchEnd] = useState<number | null>(null)

  if (!user) return null

  const userNavItems = navigationItems.filter(item => 
    item.roles.includes(user.role)
  )

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  const closeMobileMenu = () => setIsMobileMenuOpen(false)
  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen)

  // Handle swipe gestures to close menu
  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null)
    setTouchStart(e.targetTouches[0].clientX)
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX)
  }

  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return
    
    const distance = touchStart - touchEnd
    const isLeftSwipe = distance > 50
    
    if (isLeftSwipe && isMobileMenuOpen) {
      closeMobileMenu()
    }
  }

  // Close menu when route changes
  useEffect(() => {
    closeMobileMenu()
  }, [pathname])

  // Close menu on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeMobileMenu()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [])

  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'auto'
    }
    
    return () => {
      document.body.style.overflow = 'auto'
    }
  }, [isMobileMenuOpen])

  return (
    <>
      <nav className="border-b bg-card relative z-40" role="navigation" aria-label="Main navigation">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/dashboard" className="flex items-center">
                <div className="text-2xl font-bold text-primary mr-8">
                  QVF Platform
                </div>
              </Link>
              
              {/* Desktop Navigation */}
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
            
            {/* Desktop User Actions */}
            <div className="hidden md:flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <User className="h-4 w-4" />
                <span className="hidden lg:inline">{user.full_name}</span>
                <span className="text-xs bg-secondary px-2 py-1 rounded">
                  {user.role.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              
              <ThemeToggle size="default" variant="ghost" />
              
              <Button variant="ghost" size="sm" aria-label="Settings">
                <Settings className="h-4 w-4" />
              </Button>
              
              <Button variant="ghost" size="sm" onClick={handleLogout} aria-label="Logout">
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Mobile Header Actions */}
            <div className="md:hidden flex items-center space-x-2">
              <div className="text-xs bg-secondary px-2 py-1 rounded text-secondary-foreground">
                {user.role.replace('_', ' ').toUpperCase()}
              </div>
              
              <ThemeToggle size="default" variant="ghost" />
              
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={toggleMobileMenu}
                aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
                aria-expanded={isMobileMenuOpen}
                className="p-2 min-h-[44px] min-w-[44px]"
              >
                {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/50 z-40 md:hidden"
              onClick={closeMobileMenu}
              aria-hidden="true"
            />
            
            {/* Mobile Drawer */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ 
                type: 'tween',
                duration: 0.3,
                ease: 'easeInOut'
              }}
              className="fixed top-0 left-0 h-full w-80 max-w-[85vw] bg-card border-r z-50 md:hidden overflow-y-auto"
              onTouchStart={handleTouchStart}
              onTouchMove={handleTouchMove}
              onTouchEnd={handleTouchEnd}
              role="dialog"
              aria-modal="true"
              aria-label="Mobile navigation menu"
            >
              <div className="flex flex-col h-full">
                {/* Mobile Header */}
                <div className="flex items-center justify-between p-4 border-b">
                  <div className="text-xl font-bold text-primary">
                    QVF Platform
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={closeMobileMenu}
                    aria-label="Close menu"
                    className="p-2 min-h-[44px] min-w-[44px]"
                  >
                    <X className="h-5 w-5" />
                  </Button>
                </div>
                
                {/* User Info */}
                <div className="p-4 border-b bg-secondary/20">
                  <div className="flex items-center space-x-3">
                    <div className="bg-primary/10 p-2 rounded-full">
                      <User className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-foreground truncate">
                        {user.full_name}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {user.role.replace('_', ' ').toUpperCase()}
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Navigation Items */}
                <nav className="flex-1 p-4" aria-label="Mobile navigation links">
                  <div className="space-y-2">
                    {userNavItems.map((item) => (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={closeMobileMenu}
                        className={cn(
                          'flex items-center space-x-3 px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200',
                          'min-h-[44px] touch-manipulation', // Touch-friendly target
                          pathname === item.href
                            ? 'bg-primary text-primary-foreground shadow-sm'
                            : 'text-muted-foreground hover:text-foreground hover:bg-accent active:bg-accent/80'
                        )}
                      >
                        <div className="flex-shrink-0">
                          {item.icon}
                        </div>
                        <span className="flex-1">{item.label}</span>
                      </Link>
                    ))}
                  </div>
                </nav>
                
                {/* Mobile Actions */}
                <div className="p-4 border-t bg-secondary/10">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between py-2 px-3">
                      <span className="text-sm font-medium text-foreground">Theme</span>
                      <ThemeToggle size="default" variant="ghost" />
                    </div>
                    
                    <Button 
                      variant="ghost" 
                      className="w-full justify-start space-x-3 min-h-[44px] px-3"
                      aria-label="Settings"
                    >
                      <Settings className="h-4 w-4" />
                      <span>Settings</span>
                    </Button>
                    
                    <Button 
                      variant="ghost" 
                      onClick={handleLogout}
                      className="w-full justify-start space-x-3 min-h-[44px] px-3 text-destructive hover:text-destructive hover:bg-destructive/10"
                      aria-label="Logout"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Logout</span>
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}