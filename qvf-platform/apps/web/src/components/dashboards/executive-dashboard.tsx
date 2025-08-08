'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { KPICard } from '@/components/ui/kpi-card'
import { PriorityMatrix } from '@/components/ui/priority-matrix'
import { InsightCard } from '@/components/ui/insight-card'
import { qvfAPI, workItemsAPI, type QVFScoreResponse } from '@/lib/api'
import { 
  LineChart,
  Line,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Users,
  Zap,
  RefreshCw,
  Sun,
  Moon
} from 'lucide-react'

// Sample data for the executive dashboard
const sampleWorkItems = [
  {
    id: "EPIC-001",
    title: "Customer Portal Redesign",
    business_value: 9,
    technical_complexity: 6,
    story_points: 21,
    priority: "High" as const,
    risk_level: 4,
    state: "Active",
    team: "Frontend Team",
    strategic_theme: "Customer Experience"
  },
  {
    id: "FEAT-002", 
    title: "Mobile App Performance Optimization",
    business_value: 8,
    technical_complexity: 7,
    story_points: 13,
    priority: "High" as const,
    risk_level: 3,
    state: "Active",
    team: "Mobile Team",
    strategic_theme: "Technical Excellence"
  },
  {
    id: "FEAT-003",
    title: "Advanced Analytics Dashboard",
    business_value: 7,
    technical_complexity: 8,
    story_points: 34,
    priority: "Medium" as const,
    risk_level: 6,
    state: "Planning",
    team: "Data Team",
    strategic_theme: "Innovation"
  },
  {
    id: "STORY-004",
    title: "User Onboarding Flow",
    business_value: 8,
    technical_complexity: 4,
    story_points: 8,
    priority: "High" as const,
    risk_level: 2,
    state: "Active",
    team: "UX Team",
    strategic_theme: "Customer Experience"
  },
  {
    id: "TECH-005",
    title: "Database Migration",
    business_value: 3,
    technical_complexity: 9,
    story_points: 55,
    priority: "Medium" as const,
    risk_level: 8,
    state: "Planning",
    team: "Platform Team",
    strategic_theme: "Technical Excellence"
  }
]

// Chart colors optimized for dark theme with cyan accents
const CHART_COLORS = {
  primary: '#00D9FF',
  secondary: '#10B981', 
  tertiary: '#F59E0B',
  quaternary: '#EF4444',
  grid: '#262626',
  text: '#A3A3A3'
}

const PIE_COLORS = ['#00D9FF', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

export function ExecutiveDashboard() {
  const [qvfScores, setQvfScores] = useState<QVFScoreResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Fetch QVF scores on component mount
  useEffect(() => {
    fetchQVFScores()
  }, [])

  const fetchQVFScores = async () => {
    try {
      setIsLoading(true)
      const response = await qvfAPI.calculateScores({
        work_items: sampleWorkItems
      })
      setQvfScores(response)
    } catch (error) {
      console.error('Failed to fetch QVF scores:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await fetchQVFScores()
    // Add a small delay for visual feedback
    setTimeout(() => setIsRefreshing(false), 500)
  }

  // Strategic value trends data (historical)
  const strategicValueTrends = [
    { period: 'Q1 2023', value: 72.3, confidence: 85 },
    { period: 'Q2 2023', value: 78.1, confidence: 88 },
    { period: 'Q3 2023', value: 65.8, confidence: 82 },
    { period: 'Q4 2023', value: 84.2, confidence: 91 },
    { period: 'Q1 2024', value: 75.6, confidence: 87 },
    { period: 'Q2 2024', value: 88.4, confidence: 93 },
    { period: 'Q3 2024', value: 92.1, confidence: 95 },
    { period: 'Q4 2024', value: qvfScores?.avg_score ? (qvfScores.avg_score * 100) : 87.3, confidence: 94 },
  ]

  // Transform data for charts
  const portfolioHealthData = qvfScores?.scores.map(score => ({
    name: score.work_item_id,
    qvfScore: score.qvf_score,
    priority: score.priority_tier,
    confidence: score.calculation_metadata.confidence_score,
  })) || []

  const strategicThemeData = sampleWorkItems.reduce((acc, item) => {
    const theme = item.strategic_theme
    const existing = acc.find(t => t.name === theme)
    if (existing) {
      existing.count += 1
      existing.totalValue += item.business_value
    } else {
      acc.push({
        name: theme,
        count: 1,
        totalValue: item.business_value,
        avgScore: 0
      })
    }
    return acc
  }, [] as Array<{name: string, count: number, totalValue: number, avgScore: number}>)

  // Calculate average QVF scores by theme
  strategicThemeData.forEach(theme => {
    const themeItems = qvfScores?.scores.filter(score => {
      const workItem = sampleWorkItems.find(item => item.id === score.work_item_id)
      return workItem?.strategic_theme === theme.name
    }) || []
    
    theme.avgScore = themeItems.length > 0 
      ? themeItems.reduce((sum, score) => sum + score.qvf_score, 0) / themeItems.length
      : 0
  })

  const riskAnalysisData = qvfScores?.scores.map(score => {
    const workItem = sampleWorkItems.find(item => item.id === score.work_item_id)
    return {
      name: score.work_item_id.split('-')[0],
      risk: workItem?.risk_level || 0,
      qvfScore: score.qvf_score,
      complexity: workItem?.technical_complexity || 0
    }
  }) || []

  const topInitiatives = qvfScores?.scores
    .sort((a, b) => b.qvf_score - a.qvf_score)
    .slice(0, 10)
    .map(score => {
      const workItem = sampleWorkItems.find(item => item.id === score.work_item_id)
      return {
        id: score.work_item_id,
        title: workItem?.title || 'Unknown',
        qvfScore: score.qvf_score,
        priority: score.priority_tier,
        team: workItem?.team || 'Unknown',
        businessValue: workItem?.business_value || 0,
        storyPoints: workItem?.story_points || 0
      }
    }) || []

  if (isLoading) {
    return (
      <div className="p-6 space-y-6 animate-fade-in">
        <div className="space-y-6">
          {/* Header Skeleton */}
          <div className="glass rounded-2xl p-8">
            <div className="h-8 bg-muted/20 rounded-lg w-80 mb-2"></div>
            <div className="h-4 bg-muted/10 rounded-lg w-96"></div>
          </div>

          {/* KPI Cards Skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="glass rounded-xl p-6">
                <div className="space-y-4">
                  <div className="h-4 bg-muted/10 rounded w-32"></div>
                  <div className="h-8 bg-primary/20 rounded w-20"></div>
                  <div className="h-3 bg-muted/10 rounded w-24"></div>
                </div>
              </div>
            ))}
          </div>

          {/* Charts Skeleton */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 glass rounded-xl p-6">
              <div className="h-6 bg-muted/10 rounded w-48 mb-6"></div>
              <div className="h-64 bg-muted/5 rounded-lg"></div>
            </div>
            <div className="glass rounded-xl p-6">
              <div className="h-6 bg-muted/10 rounded w-40 mb-6"></div>
              <div className="h-64 bg-muted/5 rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-3 md:p-6 space-y-6 md:space-y-8 animate-fade-in">
      {/* Executive Header with Technical Aesthetic */}
      <div className="glass rounded-2xl p-4 md:p-8 relative overflow-hidden mobile-card-padding">
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary to-accent-hover"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-4xl font-bold tracking-tight text-primary mb-2">
              QVF Executive Dashboard
            </h1>
            <p className="text-muted-foreground font-mono text-xs md:text-sm">
              $ quantified-value-framework --mode=strategic --real-time
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="w-full md:w-auto"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span className="md:inline">Refresh</span>
            </Button>
          </div>
        </div>
      </div>

      {/* KPI Grid with Cyan Accents */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <KPICard
          title="Portfolio Alignment Score"
          value={`${((qvfScores?.avg_score || 0) * 100).toFixed(1)}%`}
          description="Average QVF Score"
          trend={{
            direction: 'up',
            value: '+5.2%',
            label: 'from last quarter'
          }}
          icon={<TrendingUp className="h-4 w-4 md:h-5 md:w-5" />}
          className="mobile-card-padding"
        />
        
        <KPICard
          title="Prioritized Value Pipeline"
          value="$2.4M"
          description="Expected ROI"
          trend={{
            direction: 'up',
            value: '+12.1%',
            label: 'expected ROI'
          }}
          icon={<DollarSign className="h-4 w-4 md:h-5 md:w-5" />}
          className="mobile-card-padding"
        />
        
        <KPICard
          title="Stakeholder Consensus"
          value="94.7%"
          description="Alignment Score"
          trend={{
            direction: 'up',
            value: '8.3%',
            label: 'improvement'
          }}
          icon={<Target className="h-4 w-4 md:h-5 md:w-5" />}
          className="mobile-card-padding"
        />
        
        <KPICard
          title="Active Work Items"
          value={qvfScores?.total_items || 142}
          description="Total items in portfolio"
          trend={{
            direction: 'down',
            value: '-18',
            label: 'optimized out'
          }}
          icon={<CheckCircle className="h-4 w-4 md:h-5 md:w-5" />}
          className="mobile-card-padding"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 md:gap-6">
        {/* Strategic Value Trends Chart */}
        <Card variant="glass" className="xl:col-span-2 mobile-card-padding">
          <CardHeader variant="with-accent" className="mobile-compact">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <CardTitle variant="chart" className="text-lg md:text-xl">Strategic Value Trends</CardTitle>
                <p className="text-xs md:text-sm text-muted-foreground font-mono">last_8_quarters.json</p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="mobile-compact">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={strategicValueTrends} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
                <XAxis 
                  dataKey="period" 
                  axisLine={false}
                  tickLine={false}
                  tick={{ 
                    fill: CHART_COLORS.text, 
                    fontSize: 10,
                    fontFamily: 'JetBrains Mono, monospace'
                  }}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis 
                  domain={[60, 100]}
                  axisLine={false}
                  tickLine={false}
                  tick={{ 
                    fill: CHART_COLORS.text, 
                    fontSize: 10,
                    fontFamily: 'JetBrains Mono, monospace'
                  }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1A1A1A', 
                    border: '1px solid #262626',
                    borderRadius: '8px',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
                    fontSize: '12px'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke={CHART_COLORS.primary}
                  strokeWidth={2}
                  dot={{ 
                    fill: CHART_COLORS.primary, 
                    stroke: '#0A0A0A', 
                    strokeWidth: 1,
                    r: 4
                  }}
                  activeDot={{ 
                    r: 6, 
                    fill: '#33E5FF',
                    stroke: CHART_COLORS.primary,
                    strokeWidth: 2
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Priority Matrix */}
        <PriorityMatrix
          className="mobile-card-padding"
          quadrants={{
            topLeft: {
              label: "High Value\nHigh Urgency",
              count: qvfScores?.summary.high_priority_count || 23,
              color: 'error'
            },
            topRight: {
              label: "High Value\nLow Urgency", 
              count: qvfScores?.summary.medium_priority_count || 47,
              color: 'success'
            },
            bottomLeft: {
              label: "Low Value\nHigh Urgency",
              count: 12,
              color: 'warning'
            },
            bottomRight: {
              label: "Low Value\nLow Urgency",
              count: qvfScores?.summary.low_priority_count || 8,
              color: 'primary'
            }
          }}
        />
      </div>

      {/* Executive Insights Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-6">
        <InsightCard
          title="OKR Alignment"
          description="89% of high-priority items directly contribute to Q4 objectives. Strategic focus is excellent."
          icon={<Target className="h-4 w-4 md:h-5 md:w-5" />}
          className="mobile-card-padding"
        />
        
        <InsightCard
          title="Risk Mitigation"
          description="3 critical dependencies identified. Automated alerts sent to stakeholders for resolution."
          icon={<AlertTriangle className="h-4 w-4 md:h-5 md:w-5" />}
          variant="warning"
          className="mobile-card-padding"
        />
        
        <InsightCard
          title="Value Acceleration"
          description="Portfolio optimization suggests 15% faster value delivery with current resource allocation."
          icon={<Zap className="h-4 w-4 md:h-5 md:w-5" />}
          variant="success"
          className="mobile-card-padding sm:col-span-2 xl:col-span-1"
        />
      </div>

      {/* Top Strategic Initiatives Table */}
      <Card variant="glass" className="mobile-card-padding">
        <CardHeader variant="with-accent" className="mobile-compact">
          <CardTitle variant="chart" className="text-lg md:text-xl">Top Strategic Initiatives</CardTitle>
          <CardDescription className="mobile-text-sm">Highest QVF scoring initiatives driving business value</CardDescription>
        </CardHeader>
        <CardContent className="mobile-compact">
          <div className="overflow-x-auto -mx-2 md:mx-0">
            <table className="w-full min-w-[600px] md:min-w-0">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-2 md:p-3 text-muted-foreground font-semibold text-xs md:text-sm">Initiative</th>
                  <th className="text-left p-2 md:p-3 text-muted-foreground font-semibold text-xs md:text-sm">QVF Score</th>
                  <th className="text-left p-2 md:p-3 text-muted-foreground font-semibold text-xs md:text-sm">Priority</th>
                  <th className="text-left p-2 md:p-3 text-muted-foreground font-semibold text-xs md:text-sm hidden sm:table-cell">Team</th>
                  <th className="text-left p-2 md:p-3 text-muted-foreground font-semibold text-xs md:text-sm hidden md:table-cell">Value</th>
                  <th className="text-left p-2 md:p-3 text-muted-foreground font-semibold text-xs md:text-sm hidden lg:table-cell">Points</th>
                </tr>
              </thead>
              <tbody>
                {topInitiatives.slice(0, 5).map((initiative, index) => (
                  <tr key={initiative.id} className="border-b border-border/50 hover:bg-accent/5 transition-colors">
                    <td className="p-2 md:p-3">
                      <div>
                        <div className="font-semibold text-primary text-sm md:text-base mobile-text-sm">{initiative.title}</div>
                        <div className="text-xs text-muted-foreground font-mono mobile-text-xs">{initiative.id}</div>
                      </div>
                    </td>
                    <td className="p-2 md:p-3">
                      <span className="font-mono text-base md:text-lg font-bold text-primary mobile-text-sm">
                        {initiative.qvfScore.toFixed(3)}
                      </span>
                    </td>
                    <td className="p-2 md:p-3">
                      <span className={`px-2 md:px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${
                        initiative.priority === 'High' 
                          ? 'bg-red-400/20 text-red-400 border border-red-400/30' 
                          : initiative.priority === 'Medium'
                          ? 'bg-yellow-400/20 text-yellow-400 border border-yellow-400/30'
                          : 'bg-green-400/20 text-green-400 border border-green-400/30'
                      }`}>
                        {initiative.priority}
                      </span>
                    </td>
                    <td className="p-2 md:p-3 text-xs md:text-sm text-muted-foreground hidden sm:table-cell">{initiative.team}</td>
                    <td className="p-2 md:p-3 text-center font-semibold hidden md:table-cell">{initiative.businessValue}</td>
                    <td className="p-2 md:p-3 text-center font-semibold hidden lg:table-cell">{initiative.storyPoints}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Floating Action Button with responsive sizing */}
      <Button
        variant="floating"
        size="floating"
        className="fixed bottom-4 right-4 md:bottom-8 md:right-8 z-50 h-12 w-12 md:h-14 md:w-14"
        onClick={handleRefresh}
        disabled={isRefreshing}
        aria-label="Refresh dashboard"
      >
        <RefreshCw className={`h-5 w-5 md:h-6 md:w-6 ${isRefreshing ? 'animate-spin' : ''}`} />
      </Button>
    </div>
  )
}