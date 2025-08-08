import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="px-4">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground mb-4">
          Welcome to QVF Platform
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl">
          Quality Value Framework for Agile teams. Analyze work items, 
          calculate QVF scores, and optimize your development process.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Work Items Analysis</CardTitle>
            <CardDescription>
              View and analyze work items from Azure DevOps with QVF scoring
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/work-items">View Work Items</Link>
            </Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>QVF Dashboard</CardTitle>
            <CardDescription>
              Interactive dashboards showing quality and value metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/dashboard">Open Dashboard</Link>
            </Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Team Performance</CardTitle>
            <CardDescription>
              Team-level insights and performance analytics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/analytics">View Analytics</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
      
      <div className="mt-12">
        <Card>
          <CardHeader>
            <CardTitle>Quick Stats</CardTitle>
            <CardDescription>Overview of your current work items</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">24</div>
                <div className="text-sm text-muted-foreground">Active Items</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-chart-1">0.78</div>
                <div className="text-sm text-muted-foreground">Avg QVF Score</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-chart-2">8</div>
                <div className="text-sm text-muted-foreground">High Priority</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-chart-3">3</div>
                <div className="text-sm text-muted-foreground">Teams</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}