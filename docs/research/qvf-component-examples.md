# QVF Platform Component Implementation Examples

## Work Item Card with Drag-and-Drop

### Basic Work Item Card Component
```tsx
// components/ui/work-item-card.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, Calendar, User, AlertCircle } from 'lucide-react'

interface WorkItem {
  id: string
  title: string
  description?: string
  status: 'todo' | 'in-progress' | 'done' | 'blocked'
  priority: 'low' | 'medium' | 'high' | 'critical'
  assignee?: {
    name: string
    avatar?: string
    initials: string
  }
  dueDate?: string
  storyPoints?: number
  tags?: string[]
}

interface WorkItemCardProps {
  item: WorkItem
  isDragging?: boolean
}

export function WorkItemCard({ item, isDragging }: WorkItemCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: sortableIsDragging,
  } = useSortable({ id: item.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const statusColors = {
    'todo': 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200',
    'in-progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'done': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'blocked': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }

  const priorityColors = {
    'low': 'text-slate-500',
    'medium': 'text-yellow-500',
    'high': 'text-orange-500',
    'critical': 'text-red-500'
  }

  return (
    <Card 
      ref={setNodeRef}
      style={style}
      className={`cursor-pointer transition-all hover:shadow-md ${
        sortableIsDragging ? 'opacity-50 rotate-3 shadow-lg' : ''
      }`}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-sm font-medium line-clamp-2">
            {item.title}
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0 cursor-grab"
            {...attributes}
            {...listeners}
          >
            <GripVertical className="h-3 w-3" />
          </Button>
        </div>
        {item.description && (
          <p className="text-xs text-muted-foreground line-clamp-2">
            {item.description}
          </p>
        )}
      </CardHeader>
      
      <CardContent className="pt-0 space-y-3">
        {/* Status and Priority */}
        <div className="flex items-center justify-between">
          <Badge 
            variant="secondary" 
            className={statusColors[item.status]}
          >
            {item.status.replace('-', ' ')}
          </Badge>
          <div className="flex items-center gap-1">
            <AlertCircle 
              className={`h-3 w-3 ${priorityColors[item.priority]}`} 
            />
            <span className="text-xs text-muted-foreground">
              {item.storyPoints}pt
            </span>
          </div>
        </div>

        {/* Tags */}
        {item.tags && item.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {item.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
            {item.tags.length > 3 && (
              <span className="text-xs text-muted-foreground">
                +{item.tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t">
          {item.assignee ? (
            <div className="flex items-center gap-2">
              <Avatar className="h-6 w-6">
                <AvatarImage src={item.assignee.avatar} />
                <AvatarFallback className="text-xs">
                  {item.assignee.initials}
                </AvatarFallback>
              </Avatar>
              <span className="text-xs text-muted-foreground">
                {item.assignee.name}
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-1 text-muted-foreground">
              <User className="h-3 w-3" />
              <span className="text-xs">Unassigned</span>
            </div>
          )}
          
          {item.dueDate && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span className="text-xs">
                {new Date(item.dueDate).toLocaleDateString()}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
```

### Kanban Board Container
```tsx
// components/ui/kanban-board.tsx
import { useState } from 'react'
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners
} from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy
} from '@dnd-kit/sortable'
import { WorkItemCard } from './work-item-card'

interface KanbanColumn {
  id: string
  title: string
  items: WorkItem[]
}

interface KanbanBoardProps {
  columns: KanbanColumn[]
  onItemMove: (itemId: string, sourceColumn: string, targetColumn: string, newIndex: number) => void
}

export function KanbanBoard({ columns, onItemMove }: KanbanBoardProps) {
  const [activeItem, setActiveItem] = useState<WorkItem | null>(null)
  
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  )

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event
    const activeItem = columns
      .flatMap(col => col.items)
      .find(item => item.id === active.id)
    setActiveItem(activeItem || null)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    setActiveItem(null)

    if (!over) return

    const activeId = active.id as string
    const overId = over.id as string

    // Find source and target columns
    const sourceColumn = columns.find(col => 
      col.items.some(item => item.id === activeId)
    )
    const targetColumn = columns.find(col => 
      col.id === overId || col.items.some(item => item.id === overId)
    )

    if (!sourceColumn || !targetColumn) return

    // Calculate new index
    const targetItems = targetColumn.items
    const overIndex = targetItems.findIndex(item => item.id === overId)
    const newIndex = overIndex === -1 ? targetItems.length : overIndex

    onItemMove(activeId, sourceColumn.id, targetColumn.id, newIndex)
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-6 overflow-x-auto p-6">
        {columns.map((column) => (
          <KanbanColumn key={column.id} column={column} />
        ))}
      </div>
      
      <DragOverlay>
        {activeItem && (
          <WorkItemCard item={activeItem} isDragging />
        )}
      </DragOverlay>
    </DndContext>
  )
}

function KanbanColumn({ column }: { column: KanbanColumn }) {
  return (
    <div className="flex flex-col min-w-80 max-w-80">
      <div className="flex items-center justify-between mb-4 p-3 bg-muted rounded-lg">
        <h3 className="font-semibold">{column.title}</h3>
        <Badge variant="secondary">{column.items.length}</Badge>
      </div>
      
      <SortableContext 
        items={column.items.map(item => item.id)} 
        strategy={verticalListSortingStrategy}
      >
        <div className="flex-1 space-y-3">
          {column.items.map((item) => (
            <WorkItemCard key={item.id} item={item} />
          ))}
        </div>
      </SortableContext>
    </div>
  )
}
```

## Hierarchical Tree View for Work Items

```tsx
// components/ui/work-item-tree.tsx
import { useState } from 'react'
import { ChevronDown, ChevronRight, Folder, FileText } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface TreeItem {
  id: string
  title: string
  type: 'epic' | 'feature' | 'story' | 'task' | 'bug'
  status: 'todo' | 'in-progress' | 'done' | 'blocked'
  children?: TreeItem[]
  storyPoints?: number
}

interface WorkItemTreeProps {
  items: TreeItem[]
  onItemSelect?: (item: TreeItem) => void
  selectedId?: string
}

export function WorkItemTree({ items, onItemSelect, selectedId }: WorkItemTreeProps) {
  return (
    <div className="space-y-1">
      {items.map((item) => (
        <TreeNode
          key={item.id}
          item={item}
          onSelect={onItemSelect}
          selectedId={selectedId}
          level={0}
        />
      ))}
    </div>
  )
}

interface TreeNodeProps {
  item: TreeItem
  onSelect?: (item: TreeItem) => void
  selectedId?: string
  level: number
}

function TreeNode({ item, onSelect, selectedId, level }: TreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const hasChildren = item.children && item.children.length > 0

  const typeIcons = {
    'epic': Folder,
    'feature': Folder,
    'story': FileText,
    'task': FileText,
    'bug': FileText
  }

  const typeColors = {
    'epic': 'text-purple-600 dark:text-purple-400',
    'feature': 'text-blue-600 dark:text-blue-400',
    'story': 'text-green-600 dark:text-green-400',
    'task': 'text-orange-600 dark:text-orange-400',
    'bug': 'text-red-600 dark:text-red-400'
  }

  const statusColors = {
    'todo': 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200',
    'in-progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'done': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'blocked': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }

  const Icon = typeIcons[item.type]
  const indent = level * 24

  return (
    <div>
      <div
        className={cn(
          "flex items-center gap-2 p-2 rounded-md hover:bg-accent cursor-pointer group transition-colors",
          selectedId === item.id && "bg-accent"
        )}
        style={{ paddingLeft: `${indent + 8}px` }}
        onClick={() => onSelect?.(item)}
      >
        {hasChildren ? (
          <Button
            variant="ghost"
            size="sm"
            className="h-4 w-4 p-0"
            onClick={(e) => {
              e.stopPropagation()
              setIsExpanded(!isExpanded)
            }}
          >
            {isExpanded ? (
              <ChevronDown className="h-3 w-3" />
            ) : (
              <ChevronRight className="h-3 w-3" />
            )}
          </Button>
        ) : (
          <div className="w-4" />
        )}
        
        <Icon className={cn("h-4 w-4", typeColors[item.type])} />
        
        <span className="flex-1 text-sm font-medium truncate">
          {item.title}
        </span>
        
        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Badge variant="outline" className={cn("text-xs", statusColors[item.status])}>
            {item.status}
          </Badge>
          {item.storyPoints && (
            <span className="text-xs text-muted-foreground">
              {item.storyPoints}pt
            </span>
          )}
        </div>
      </div>

      {hasChildren && isExpanded && (
        <div className="ml-3">
          {item.children!.map((child) => (
            <TreeNode
              key={child.id}
              item={child}
              onSelect={onSelect}
              selectedId={selectedId}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}
```

## Data Table with Filtering

```tsx
// components/ui/work-items-table.tsx
import { useState, useMemo } from 'react'
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState
} from '@tanstack/react-table'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ArrowUpDown, Search, Filter } from 'lucide-react'

interface WorkItemsTableProps {
  data: WorkItem[]
  onRowClick?: (item: WorkItem) => void
}

export function WorkItemsTable({ data, onRowClick }: WorkItemsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')

  const columns: ColumnDef<WorkItem>[] = useMemo(() => [
    {
      accessorKey: 'title',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="h-8 px-2 lg:px-3"
        >
          Title
          <ArrowUpDown className="ml-2 h-3 w-3" />
        </Button>
      ),
      cell: ({ row }) => (
        <div className="max-w-[300px]">
          <div className="font-medium truncate">{row.original.title}</div>
          {row.original.description && (
            <div className="text-xs text-muted-foreground truncate">
              {row.original.description}
            </div>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => {
        const status = row.original.status
        const statusColors = {
          'todo': 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200',
          'in-progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
          'done': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
          'blocked': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }
        return (
          <Badge className={statusColors[status]}>
            {status.replace('-', ' ')}
          </Badge>
        )
      },
      filterFn: (row, id, value) => {
        return value.includes(row.getValue(id))
      },
    },
    {
      accessorKey: 'priority',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          Priority
          <ArrowUpDown className="ml-2 h-3 w-3" />
        </Button>
      ),
      cell: ({ row }) => {
        const priority = row.original.priority
        const priorityColors = {
          'low': 'text-slate-500',
          'medium': 'text-yellow-500',
          'high': 'text-orange-500',
          'critical': 'text-red-500'
        }
        return (
          <span className={`font-medium ${priorityColors[priority]}`}>
            {priority.charAt(0).toUpperCase() + priority.slice(1)}
          </span>
        )
      },
    },
    {
      accessorKey: 'assignee',
      header: 'Assignee',
      cell: ({ row }) => {
        const assignee = row.original.assignee
        if (!assignee) {
          return <span className="text-muted-foreground">Unassigned</span>
        }
        return (
          <div className="flex items-center gap-2">
            <Avatar className="h-6 w-6">
              <AvatarImage src={assignee.avatar} />
              <AvatarFallback className="text-xs">
                {assignee.initials}
              </AvatarFallback>
            </Avatar>
            <span className="text-sm">{assignee.name}</span>
          </div>
        )
      },
    },
    {
      accessorKey: 'storyPoints',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          Points
          <ArrowUpDown className="ml-2 h-3 w-3" />
        </Button>
      ),
      cell: ({ row }) => {
        const points = row.original.storyPoints
        return points ? (
          <Badge variant="outline">{points}</Badge>
        ) : (
          <span className="text-muted-foreground">-</span>
        )
      },
    },
    {
      accessorKey: 'dueDate',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          Due Date
          <ArrowUpDown className="ml-2 h-3 w-3" />
        </Button>
      ),
      cell: ({ row }) => {
        const dueDate = row.original.dueDate
        if (!dueDate) return <span className="text-muted-foreground">-</span>
        
        const date = new Date(dueDate)
        const isOverdue = date < new Date() && row.original.status !== 'done'
        
        return (
          <span className={isOverdue ? 'text-red-600 dark:text-red-400' : ''}>
            {date.toLocaleDateString()}
          </span>
        )
      },
    },
  ], [])

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: 'includesString',
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
  })

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search work items..."
            value={globalFilter ?? ''}
            onChange={(e) => setGlobalFilter(String(e.target.value))}
            className="pl-8"
          />
        </div>
        <Button variant="outline" size="sm">
          <Filter className="mr-2 h-4 w-4" />
          Filters
        </Button>
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => onRowClick?.(row.original)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
```

## Charts with Tremor

```tsx
// components/ui/qvf-metrics-dashboard.tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  AreaChart,
  BarChart,
  DonutChart,
  LineChart,
  Title,
  Text,
} from '@tremor/react'

interface QVFMetricsDashboardProps {
  velocityData: Array<{
    sprint: string
    planned: number
    completed: number
    date: string
  }>
  burndownData: Array<{
    day: number
    ideal: number
    actual: number
  }>
  statusDistribution: Array<{
    status: string
    count: number
  }>
  priorityBreakdown: Array<{
    priority: string
    storyPoints: number
  }>
}

export function QVFMetricsDashboard({
  velocityData,
  burndownData,
  statusDistribution,
  priorityBreakdown
}: QVFMetricsDashboardProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Sprint Velocity */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Sprint Velocity</CardTitle>
          <CardDescription>
            Planned vs Completed Story Points
          </CardDescription>
        </CardHeader>
        <CardContent>
          <BarChart
            data={velocityData}
            index="sprint"
            categories={["planned", "completed"]}
            colors={["blue", "green"]}
            valueFormatter={(value) => `${value} pts`}
            className="h-72"
          />
        </CardContent>
      </Card>

      {/* Burndown Chart */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Sprint Burndown</CardTitle>
          <CardDescription>
            Remaining work over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LineChart
            data={burndownData}
            index="day"
            categories={["ideal", "actual"]}
            colors={["gray", "blue"]}
            valueFormatter={(value) => `${value} pts`}
            className="h-72"
          />
        </CardContent>
      </Card>

      {/* Status Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Work Item Status</CardTitle>
          <CardDescription>
            Current distribution of work items
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DonutChart
            data={statusDistribution}
            category="count"
            index="status"
            colors={["slate", "blue", "green", "red"]}
            className="h-48"
          />
        </CardContent>
      </Card>

      {/* Priority Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Priority Breakdown</CardTitle>
          <CardDescription>
            Story points by priority
          </CardDescription>
        </CardHeader>
        <CardContent>
          <BarChart
            data={priorityBreakdown}
            index="priority"
            categories={["storyPoints"]}
            colors={["orange"]}
            layout="vertical"
            className="h-48"
          />
        </CardContent>
      </Card>
    </div>
  )
}
```

## Installation Commands

```bash
# Core shadcn/ui setup
npx shadcn-ui@latest init
npx shadcn-ui@latest add card button badge avatar input form table

# Drag and drop functionality
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities

# Data table functionality
npm install @tanstack/react-table

# Charts and visualization
npm install @tremor/react recharts

# Icons
npm install lucide-react

# OriginUI components (add as needed)
npx shadcn-ui@latest add https://originui.com/r/tree-01.json
npx shadcn-ui@latest add https://originui.com/r/calendar-01.json
```

These examples provide production-ready components that can be directly integrated into the QVF platform, demonstrating the power of combining shadcn/ui with complementary libraries for a complete enterprise solution.