'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend
} from 'recharts'
import { 
  Users, 
  Clock, 
  Target, 
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Activity,
  Zap,
  Timer,
  BarChart3
} from 'lucide-react'

// Sample sprint and team data
const currentSprintData = {
  sprintNumber: 6,
  startDate: new Date('2025-08-05'),
  endDate: new Date('2025-08-18'),
  totalStoryPoints: 52,
  completedStoryPoints: 31,
  remainingStoryPoints: 21,
  totalStories: 12,
  completedStories: 7,
  inProgressStories: 3,
  todoStories: 2,
  daysElapsed: 5,
  daysTotal: 10,
  dailyVelocity: 6.2
}

const teamVelocityData = [
  { sprint: 'Sprint 1', planned: 42, completed: 38, commitment: 42 },
  { sprint: 'Sprint 2', planned: 45, completed: 41, commitment: 45 },
  { sprint: 'Sprint 3', planned: 48, completed: 44, commitment: 48 },
  { sprint: 'Sprint 4', planned: 50, completed: 46, commitment: 50 },
  { sprint: 'Sprint 5', planned: 52, completed: 48, commitment: 52 },
  { sprint: 'Sprint 6', planned: 52, completed: 31, commitment: 52 }, // Current
]

const impedimentData = [
  {
    id: "IMP-001",
    title: "Database performance issues",
    status: "Open",
    priority: "High",
    assignedTo: "DevOps Team",
    createdDate: new Date('2025-08-06'),
    impact: "2 stories blocked",
    category: "Technical"
  },
  {
    id: "IMP-002", 
    title: "Missing design assets",
    status: "In Progress",
    priority: "Medium",
    assignedTo: "Design Team",
    createdDate: new Date('2025-08-07'),
    impact: "1 story delayed",
    category: "Process"
  },
  {
    id: "IMP-003",
    title: "External API dependencies",
    status: "Resolved",
    priority: "High",
    assignedTo: "Architecture Team",
    createdDate: new Date('2025-08-04'),
    impact: "3 stories unblocked",
    category: "External"
  }
]

const teamMembersData = [
  {
    name: "Alice Johnson",
    role: "Senior Developer",
    capacity: 8,
    planned: 7,
    completed: 5,
    availability: "Available",
    currentTask: "User Authentication API"
  },
  {
    name: "Bob Chen",
    role: "Frontend Developer", 
    capacity: 8,
    planned: 6,
    completed: 6,
    availability: "Available",
    currentTask: "Dashboard Components"
  },
  {
    name: "Carol Davis",
    role: "Backend Developer",
    capacity: 8,
    planned: 8,
    completed: 6,
    availability: "Blocked",
    currentTask: "Database Migration"
  },
  {
    name: "David Wilson",
    role: "QA Engineer",
    capacity: 8,
    planned: 5,
    completed: 4,
    availability: "Available",
    currentTask: "Test Automation"
  }
]

const burndownData = Array.from({ length: 11 }, (_, i) => ({
  day: i,
  ideal: Math.max(0, 52 - (52 / 10) * i),
  actual: i <= 5 ? Math.max(0, 52 - (31 / 5) * i) : null,
  projected: i > 5 ? Math.max(0, 21 - (21 / 5) * (i - 5)) : null
}))

const teamHealthData = [
  { metric: 'Sprint Goal Achievement', current: 85, previous: 80, target: 90 },
  { metric: 'Velocity Consistency', current: 92, previous: 88, target: 85 },
  { metric: 'Code Quality', current: 78, previous: 75, target: 80 },
  { metric: 'Team Satisfaction', current: 88, previous: 85, target: 85 },
  { metric: 'Technical Debt', current: 65, previous: 70, target: 60 },
  { metric: 'Defect Rate', current: 72, previous: 68, target: 80 }
]

export function ScrumMasterDashboard() {
  const [selectedView, setSelectedView] = useState<'overview' | 'impediments' | 'team'>('overview')
  
  const sprintProgress = (currentSprintData.completedStoryPoints / currentSprintData.totalStoryPoints) * 100
  const timeProgress = (currentSprintData.daysElapsed / currentSprintData.daysTotal) * 100
  const isOnTrack = sprintProgress >= timeProgress - 10

  const getImpedimentColor = (priority: string, status: string) => {
    if (status === 'Resolved') return 'bg-green-100 text-green-800 border-green-200'
    if (priority === 'High') return 'bg-red-100 text-red-800 border-red-200'
    if (priority === 'Medium') return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-gray-100 text-gray-800 border-gray-200'
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Scrum Master Dashboard</h1>
          <p className="text-muted-foreground">
            Sprint progress, team health, and impediment management
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant={selectedView === 'overview' ? 'default' : 'outline'}
            onClick={() => setSelectedView('overview')}
          >
            Overview
          </Button>
          <Button 
            variant={selectedView === 'impediments' ? 'default' : 'outline'}
            onClick={() => setSelectedView('impediments')}
          >
            Impediments
          </Button>
          <Button 
            variant={selectedView === 'team' ? 'default' : 'outline'}
            onClick={() => setSelectedView('team')}
          >
            Team Health
          </Button>
        </div>
      </div>

      {/* Current Sprint KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sprint Progress</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sprintProgress.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {currentSprintData.completedStoryPoints}/{currentSprintData.totalStoryPoints} story points
            </p>
            <Progress value={sprintProgress} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sprint Health</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${isOnTrack ? 'text-green-600' : 'text-orange-600'}`}>
              {isOnTrack ? 'On Track' : 'Behind'}
            </div>
            <p className="text-xs text-muted-foreground">
              Day {currentSprintData.daysElapsed} of {currentSprintData.daysTotal}
            </p>
            <Progress value={timeProgress} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Impediments</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {impedimentData.filter(imp => imp.status !== 'Resolved').length}
            </div>
            <p className="text-xs text-muted-foreground">
              {impedimentData.filter(imp => imp.priority === 'High' && imp.status !== 'Resolved').length} high priority
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Velocity</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {teamVelocityData[teamVelocityData.length - 2]?.completed || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Points per sprint (avg)
            </p>
          </CardContent>
        </Card>
      </div>

      {selectedView === 'overview' && (
        <>
          {/* Sprint Burndown and Velocity Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Sprint Burndown Chart</CardTitle>
                <CardDescription>Current sprint progress vs ideal burndown</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={burndownData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Sprint Days', position: 'insideBottom', offset: -10 }} />
                    <YAxis label={{ value: 'Story Points', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="ideal" 
                      stroke="#ccc" 
                      strokeDasharray="5 5"
                      name="Ideal Burndown"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="actual" 
                      stroke="#8884d8" 
                      strokeWidth={3}
                      name="Actual Progress"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="projected" 
                      stroke="#ff7300" 
                      strokeDasharray="3 3"
                      name="Projected"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Velocity Trend</CardTitle>
                <CardDescription>Team velocity over recent sprints</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={teamVelocityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="sprint" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="commitment" fill="#e0e0e0" name="Commitment" />
                    <Bar dataKey="completed" fill="#82ca9d" name="Completed" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Team Capacity */}
          <Card>
            <CardHeader>
              <CardTitle>Team Capacity & Workload</CardTitle>
              <CardDescription>Individual team member capacity and current assignments</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {teamMembersData.map((member) => (
                  <div key={member.name} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h4 className="font-medium">{member.name}</h4>
                        <p className="text-sm text-gray-600">{member.role}</p>
                      </div>
                      <Badge 
                        variant={member.availability === 'Available' ? 'default' : 'secondary'}
                        className={member.availability === 'Blocked' ? 'bg-red-100 text-red-800' : ''}
                      >
                        {member.availability}
                      </Badge>
                    </div>
                    
                    <div className="mb-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Capacity</span>
                        <span>{member.completed}/{member.planned} points</span>
                      </div>
                      <Progress value={(member.completed / member.planned) * 100} />
                    </div>
                    
                    <p className="text-sm text-gray-600">
                      <strong>Current:</strong> {member.currentTask}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {selectedView === 'impediments' && (
        <Card>
          <CardHeader>
            <CardTitle>Impediment Management</CardTitle>
            <CardDescription>Track and resolve team impediments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {impedimentData.map((impediment) => (
                <div 
                  key={impediment.id}
                  className={`border rounded-lg p-4 ${getImpedimentColor(impediment.priority, impediment.status)}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{impediment.id}</Badge>
                      <Badge 
                        variant={impediment.status === 'Resolved' ? 'default' : 'secondary'}
                        className={
                          impediment.status === 'Resolved' 
                            ? 'bg-green-100 text-green-800'
                            : impediment.status === 'Open'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }
                      >
                        {impediment.status}
                      </Badge>
                      <Badge variant="outline">{impediment.category}</Badge>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Clock className="h-3 w-3" />
                      {Math.ceil((new Date().getTime() - impediment.createdDate.getTime()) / (1000 * 60 * 60 * 24))} days
                    </div>
                  </div>
                  
                  <h4 className="font-medium mb-1">{impediment.title}</h4>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Assigned to:</span> {impediment.assignedTo}
                    </div>
                    <div>
                      <span className="font-medium">Impact:</span> {impediment.impact}
                    </div>
                    <div>
                      <span className="font-medium">Priority:</span> {impediment.priority}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {selectedView === 'team' && (
        <Card>
          <CardHeader>
            <CardTitle>Team Health Radar</CardTitle>
            <CardDescription>Comprehensive team performance metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={teamHealthData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis 
                  angle={90} 
                  domain={[0, 100]}
                  tickCount={5}
                />
                <Radar
                  name="Current"
                  dataKey="current"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                  strokeWidth={2}
                />
                <Radar
                  name="Previous"
                  dataKey="previous"
                  stroke="#82ca9d"
                  fill="#82ca9d"
                  fillOpacity={0.3}
                  strokeWidth={1}
                />
                <Radar
                  name="Target"
                  dataKey="target"
                  stroke="#ff7300"
                  fill="none"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                />
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  )
}