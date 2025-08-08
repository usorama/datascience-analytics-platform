'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { qvfAPI, type QVFScoreResponse } from '@/lib/api'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  ReferenceLine
} from 'recharts'
import { 
  Calendar, 
  GitBranch, 
  Clock, 
  Users, 
  Target,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  PlayCircle,
  Pause
} from 'lucide-react'
import { format, addDays, startOfWeek, endOfWeek } from 'date-fns'

// Sample epic and release data
const sampleEpics = [
  {
    id: "EPIC-001",
    title: "Customer Portal Redesign",
    description: "Complete redesign of customer portal with modern UX",
    status: "In Progress",
    priority: "High",
    business_value: 9,
    story_points: 89,
    completed_points: 34,
    start_date: new Date('2025-08-01'),
    target_date: new Date('2025-09-15'),
    team: "Frontend Team",
    owner: "Sarah Johnson",
    stories: [
      { id: "US-001", title: "User Authentication", status: "Done", points: 8 },
      { id: "US-002", title: "Dashboard Layout", status: "In Progress", points: 13 },
      { id: "US-003", title: "Profile Management", status: "To Do", points: 21 },
      { id: "US-004", title: "Notification System", status: "To Do", points: 34 },
    ]
  },
  {
    id: "EPIC-002", 
    title: "Mobile Performance Optimization",
    description: "Optimize mobile app performance and user experience",
    status: "Planning",
    priority: "High",
    business_value: 8,
    story_points: 55,
    completed_points: 0,
    start_date: new Date('2025-08-15'),
    target_date: new Date('2025-10-01'),
    team: "Mobile Team",
    owner: "Mike Chen",
    stories: [
      { id: "US-005", title: "Bundle Size Optimization", status: "To Do", points: 13 },
      { id: "US-006", title: "Image Lazy Loading", status: "To Do", points: 8 },
      { id: "US-007", title: "Caching Strategy", status: "To Do", points: 21 },
      { id: "US-008", title: "Performance Monitoring", status: "To Do", points: 13 },
    ]
  },
  {
    id: "EPIC-003",
    title: "Analytics Dashboard Enhancement",
    description: "Advanced analytics with real-time data visualization",
    status: "In Progress",
    priority: "Medium",
    business_value: 7,
    story_points: 144,
    completed_points: 55,
    start_date: new Date('2025-07-15'),
    target_date: new Date('2025-10-30'),
    team: "Data Team",
    owner: "Alex Rivera",
    stories: [
      { id: "US-009", title: "Real-time Data Pipeline", status: "Done", points: 34 },
      { id: "US-010", title: "Interactive Charts", status: "In Progress", points: 21 },
      { id: "US-011", title: "Export Functionality", status: "To Do", points: 13 },
      { id: "US-012", title: "Custom Dashboards", status: "To Do", points: 55 },
    ]
  }
]

// Sample capacity and velocity data
const teamCapacityData = [
  { team: "Frontend Team", capacity: 40, planned: 34, available: 6 },
  { team: "Mobile Team", capacity: 32, planned: 28, available: 4 },
  { team: "Data Team", capacity: 36, planned: 36, available: 0 },
  { team: "Platform Team", capacity: 44, planned: 40, available: 4 },
]

const velocityData = [
  { sprint: "Sprint 1", planned: 42, completed: 38, velocity: 38 },
  { sprint: "Sprint 2", planned: 45, completed: 41, velocity: 39.5 },
  { sprint: "Sprint 3", planned: 48, completed: 44, velocity: 41 },
  { sprint: "Sprint 4", planned: 50, completed: 46, velocity: 42.25 },
  { sprint: "Sprint 5", planned: 52, completed: 48, velocity: 43.4 },
  { sprint: "Sprint 6", planned: 55, completed: 0, velocity: 0 }, // Current sprint
]

export function ProductOwnerDashboard() {
  const [selectedEpic, setSelectedEpic] = useState<string | null>(null)
  const [qvfScores, setQvfScores] = useState<QVFScoreResponse | null>(null)
  const [viewMode, setViewMode] = useState<'list' | 'gantt'>('list')

  // Calculate epic progress and health metrics
  const epicMetrics = sampleEpics.map(epic => {
    const progress = (epic.completed_points / epic.story_points) * 100
    const daysTotal = Math.ceil((epic.target_date.getTime() - epic.start_date.getTime()) / (1000 * 60 * 60 * 24))
    const daysElapsed = Math.ceil((new Date().getTime() - epic.start_date.getTime()) / (1000 * 60 * 60 * 24))
    const timeProgress = Math.max(0, Math.min(100, (daysElapsed / daysTotal) * 100))
    
    const isOnTrack = progress >= timeProgress - 10 // 10% tolerance
    const isAtRisk = timeProgress > progress + 20
    
    return {
      ...epic,
      progress,
      timeProgress,
      daysTotal,
      daysElapsed,
      daysRemaining: Math.max(0, daysTotal - daysElapsed),
      isOnTrack,
      isAtRisk,
      health: isAtRisk ? 'At Risk' : isOnTrack ? 'On Track' : 'Behind'
    }
  })

  // Generate Gantt chart data
  const ganttData = epicMetrics.map(epic => {
    const startWeek = startOfWeek(epic.start_date)
    const endWeek = endOfWeek(epic.target_date)
    const totalWeeks = Math.ceil((endWeek.getTime() - startWeek.getTime()) / (1000 * 60 * 60 * 24 * 7))
    
    return {
      id: epic.id,
      title: epic.title,
      startDate: epic.start_date,
      endDate: epic.target_date,
      progress: epic.progress,
      status: epic.status,
      team: epic.team,
      weeks: Array.from({ length: totalWeeks }, (_, i) => ({
        week: i + 1,
        date: addDays(startWeek, i * 7),
        progress: Math.min(100, Math.max(0, (epic.progress * totalWeeks) / 100 - i * (100 / totalWeeks)))
      }))
    }
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Done': return 'bg-green-500'
      case 'In Progress': return 'bg-blue-500'
      case 'Planning': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'On Track': return 'text-green-600 bg-green-50'
      case 'Behind': return 'text-yellow-600 bg-yellow-50'
      case 'At Risk': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Product Owner Dashboard</h1>
          <p className="text-muted-foreground">
            Epic management, release planning, and team capacity insights
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant={viewMode === 'list' ? 'default' : 'outline'}
            onClick={() => setViewMode('list')}
          >
            List View
          </Button>
          <Button 
            variant={viewMode === 'gantt' ? 'default' : 'outline'}
            onClick={() => setViewMode('gantt')}
          >
            Timeline View
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Epics</CardTitle>
            <GitBranch className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sampleEpics.filter(epic => epic.status === 'In Progress').length}
            </div>
            <p className="text-xs text-muted-foreground">
              of {sampleEpics.length} total epics
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Story Points Delivered</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {sampleEpics.reduce((sum, epic) => sum + epic.completed_points, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              of {sampleEpics.reduce((sum, epic) => sum + epic.story_points, 0)} planned
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Velocity</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {velocityData[velocityData.length - 2]?.velocity.toFixed(1) || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              Points per sprint
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">At Risk Epics</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {epicMetrics.filter(epic => epic.isAtRisk).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Need attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      {viewMode === 'list' ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Epic Management */}
          <Card>
            <CardHeader>
              <CardTitle>Epic Portfolio</CardTitle>
              <CardDescription>Manage epics and track progress</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {epicMetrics.map((epic) => (
                  <div 
                    key={epic.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedEpic(selectedEpic === epic.id ? null : epic.id)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{epic.id}</Badge>
                        <span className={`px-2 py-1 rounded-full text-xs ${getHealthColor(epic.health)}`}>
                          {epic.health}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-sm text-gray-500">
                        <Clock className="h-3 w-3" />
                        {epic.daysRemaining} days
                      </div>
                    </div>
                    
                    <h4 className="font-medium mb-2">{epic.title}</h4>
                    
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">{epic.team}</span>
                      <span className="text-sm font-medium">
                        {epic.completed_points}/{epic.story_points} pts
                      </span>
                    </div>
                    
                    <Progress value={epic.progress} className="mb-2" />
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Progress: {epic.progress.toFixed(1)}%</span>
                      <span>Time: {epic.timeProgress.toFixed(1)}%</span>
                    </div>

                    {selectedEpic === epic.id && (
                      <div className="mt-4 pt-4 border-t">
                        <h5 className="font-medium mb-2">User Stories</h5>
                        <div className="space-y-2">
                          {epic.stories.map((story) => (
                            <div key={story.id} className="flex items-center justify-between text-sm">
                              <div className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${getStatusColor(story.status)}`} />
                                <span>{story.title}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge variant="secondary" className="text-xs">
                                  {story.points} pts
                                </Badge>
                                <span className="text-gray-500">{story.status}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Team Capacity Planning */}
          <Card>
            <CardHeader>
              <CardTitle>Team Capacity Planning</CardTitle>
              <CardDescription>Current sprint capacity and allocation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {teamCapacityData.map((team) => (
                  <div key={team.team}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{team.team}</span>
                      <span className="text-sm text-gray-600">
                        {team.planned}/{team.capacity} pts
                      </span>
                    </div>
                    <Progress 
                      value={(team.planned / team.capacity) * 100} 
                      className="mb-1"
                    />
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Utilization: {((team.planned / team.capacity) * 100).toFixed(1)}%</span>
                      <span className={`font-medium ${team.available > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {team.available > 0 ? `${team.available} pts available` : 'Fully allocated'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        /* Gantt Chart View */
        <Card>
          <CardHeader>
            <CardTitle>Epic Timeline (Gantt Chart)</CardTitle>
            <CardDescription>Visual timeline of epic progress and dependencies</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <div className="min-w-[800px]">
                {ganttData.map((epic) => (
                  <div key={epic.id} className="mb-6 border-b pb-4">
                    <div className="flex items-center gap-4 mb-2">
                      <div className="w-48">
                        <h4 className="font-medium">{epic.title}</h4>
                        <p className="text-sm text-gray-500">{epic.team}</p>
                      </div>
                      <div className="flex-1">
                        <div className="relative h-8 bg-gray-200 rounded">
                          <div 
                            className={`absolute top-0 left-0 h-full rounded ${getStatusColor(epic.status)}`}
                            style={{ width: `${epic.progress}%` }}
                          />
                          <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
                            {epic.progress.toFixed(1)}%
                          </div>
                        </div>
                      </div>
                      <div className="text-sm text-gray-500 w-32">
                        {format(epic.startDate, 'MMM dd')} - {format(epic.endDate, 'MMM dd')}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Velocity Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Team Velocity Trend</CardTitle>
          <CardDescription>Sprint velocity and planning accuracy</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={velocityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="sprint" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="planned" 
                stroke="#8884d8" 
                strokeDasharray="5 5"
                name="Planned Points"
              />
              <Line 
                type="monotone" 
                dataKey="completed" 
                stroke="#82ca9d" 
                strokeWidth={2}
                name="Completed Points"
              />
              <Line 
                type="monotone" 
                dataKey="velocity" 
                stroke="#ff7300" 
                strokeWidth={2}
                name="Rolling Average"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}