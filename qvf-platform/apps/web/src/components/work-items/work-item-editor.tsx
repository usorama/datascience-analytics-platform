'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { X, Save, Loader2 } from 'lucide-react'

interface WorkItem {
  id?: string
  title: string
  business_value: number
  technical_complexity: number
  story_points: number
  priority: 'High' | 'Medium' | 'Low'
  risk_level: number
  work_item_type?: 'Epic' | 'Feature' | 'User Story' | 'Task'
  parent_id?: string
  state?: string
  assigned_to?: string
  description?: string
}

interface WorkItemEditorProps {
  workItemId?: string
  onSave: (workItem: WorkItem) => void
  onCancel: () => void
}

export function WorkItemEditor({ workItemId, onSave, onCancel }: WorkItemEditorProps) {
  const [workItem, setWorkItem] = useState<WorkItem>({
    title: '',
    business_value: 50,
    technical_complexity: 50,
    story_points: 5,
    priority: 'Medium',
    risk_level: 25,
    work_item_type: 'User Story',
    state: 'New',
    assigned_to: '',
    description: ''
  })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  
  const isEditing = !!workItemId
  
  useEffect(() => {
    if (isEditing) {
      // Load existing work item
      loadWorkItem(workItemId!)
    }
  }, [workItemId, isEditing])
  
  const loadWorkItem = async (id: string) => {
    setLoading(true)
    try {
      // In a real app, this would fetch from API
      // const item = await workItemsAPI.getById(id)
      // setWorkItem(item)
    } catch (err) {
      console.error('Failed to load work item:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSave = async () => {
    setSaving(true)
    try {
      // Validate required fields
      if (!workItem.title.trim()) {
        alert('Title is required')
        return
      }
      
      await onSave(workItem)
    } catch (err) {
      console.error('Failed to save work item:', err)
    } finally {
      setSaving(false)
    }
  }
  
  const updateField = <K extends keyof WorkItem>(field: K, value: WorkItem[K]) => {
    setWorkItem(prev => ({ ...prev, [field]: value }))
  }
  
  if (loading) {
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
        <Card className="w-full max-w-2xl mx-4">
          <CardContent className="p-6 text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
            <div>Loading work item...</div>
          </CardContent>
        </Card>
      </div>
    )
  }
  
  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <Card className="w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6">
          <div>
            <CardTitle className="text-xl">
              {isEditing ? 'Edit Work Item' : 'Create New Work Item'}
            </CardTitle>
            <CardDescription>
              {isEditing ? 'Update work item details and QVF criteria' : 'Add a new work item to the backlog'}
            </CardDescription>
          </div>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2 space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={workItem.title}
                onChange={(e) => updateField('title', e.target.value)}
                placeholder="Enter work item title..."
                className="text-base"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="type">Type</Label>
              <select
                id="type"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                value={workItem.work_item_type}
                onChange={(e) => updateField('work_item_type', e.target.value as any)}
              >
                <option value="Epic">Epic</option>
                <option value="Feature">Feature</option>
                <option value="User Story">User Story</option>
                <option value="Task">Task</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <select
                id="priority"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                value={workItem.priority}
                onChange={(e) => updateField('priority', e.target.value as any)}
              >
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="state">State</Label>
              <select
                id="state"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                value={workItem.state}
                onChange={(e) => updateField('state', e.target.value)}
              >
                <option value="New">New</option>
                <option value="Active">Active</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
                <option value="Blocked">Blocked</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="assigned_to">Assigned To</Label>
              <Input
                id="assigned_to"
                value={workItem.assigned_to}
                onChange={(e) => updateField('assigned_to', e.target.value)}
                placeholder="Enter assignee name..."
              />
            </div>
          </div>
          
          {/* QVF Criteria */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-medium">QVF Criteria</h3>
              <Badge variant="secondary">Quality Value Framework</Badge>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="business_value">Business Value</Label>
                <div className="space-y-2">
                  <Input
                    type="range"
                    id="business_value"
                    min="0"
                    max="100"
                    value={workItem.business_value}
                    onChange={(e) => updateField('business_value', parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>0</span>
                    <span className="font-medium">{workItem.business_value}</span>
                    <span>100</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="technical_complexity">Technical Complexity</Label>
                <div className="space-y-2">
                  <Input
                    type="range"
                    id="technical_complexity"
                    min="0"
                    max="100"
                    value={workItem.technical_complexity}
                    onChange={(e) => updateField('technical_complexity', parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>0</span>
                    <span className="font-medium">{workItem.technical_complexity}</span>
                    <span>100</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="risk_level">Risk Level</Label>
                <div className="space-y-2">
                  <Input
                    type="range"
                    id="risk_level"
                    min="0"
                    max="100"
                    value={workItem.risk_level}
                    onChange={(e) => updateField('risk_level', parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>0</span>
                    <span className="font-medium">{workItem.risk_level}</span>
                    <span>100</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2 md:col-span-2 lg:col-span-1">
                <Label htmlFor="story_points">Story Points</Label>
                <Input
                  type="number"
                  id="story_points"
                  min="0"
                  max="100"
                  value={workItem.story_points}
                  onChange={(e) => updateField('story_points', parseInt(e.target.value) || 0)}
                  placeholder="Enter story points..."
                />
              </div>
            </div>
          </div>
          
          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={workItem.description}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Enter detailed description of the work item..."
            />
          </div>
          
          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-6">
            <Button variant="outline" onClick={onCancel} disabled={saving}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {isEditing ? 'Update' : 'Create'}
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}