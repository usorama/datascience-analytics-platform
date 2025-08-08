'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { X, Download, FileText, FileSpreadsheet } from 'lucide-react'

interface ExtendedWorkItem {
  id: string
  title: string
  business_value: number
  technical_complexity: number
  story_points: number
  priority: 'High' | 'Medium' | 'Low'
  risk_level: number
  qvf_score?: number
  priority_tier?: 'High' | 'Medium' | 'Low'
  children?: ExtendedWorkItem[]
  parent_id?: string
  work_item_type?: string
  dependencies?: string[]
  state?: string
  assigned_to?: string
  created_date?: string
  modified_date?: string
}

interface ExportDialogProps {
  workItems: ExtendedWorkItem[]
  onExport: (format: 'pdf' | 'excel', items: ExtendedWorkItem[]) => void
  onClose: () => void
}

export function ExportDialog({ workItems, onExport, onClose }: ExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'excel'>('excel')
  const [exporting, setExporting] = useState(false)
  
  const handleExport = async () => {
    setExporting(true)
    try {
      await onExport(selectedFormat, workItems)
      onClose()
    } catch (err) {
      console.error('Export failed:', err)
    } finally {
      setExporting(false)
    }
  }
  
  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <Card className="w-full max-w-lg mx-4">
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>Export Work Items</CardTitle>
            <CardDescription>
              Export {workItems.length} work item{workItems.length === 1 ? '' : 's'} to your preferred format
            </CardDescription>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Format Selection */}
          <div className="space-y-3">
            <h4 className="font-medium">Export Format</h4>
            <div className="grid grid-cols-2 gap-3">
              <Button
                variant={selectedFormat === 'excel' ? 'default' : 'outline'}
                className="h-auto p-4 flex flex-col space-y-2"
                onClick={() => setSelectedFormat('excel')}
              >
                <FileSpreadsheet className="h-6 w-6" />
                <span className="font-medium">Excel</span>
                <span className="text-xs text-muted-foreground text-center">
                  Spreadsheet format with all data columns
                </span>
              </Button>
              
              <Button
                variant={selectedFormat === 'pdf' ? 'default' : 'outline'}
                className="h-auto p-4 flex flex-col space-y-2"
                onClick={() => setSelectedFormat('pdf')}
              >
                <FileText className="h-6 w-6" />
                <span className="font-medium">PDF</span>
                <span className="text-xs text-muted-foreground text-center">
                  Professional report format
                </span>
              </Button>
            </div>
          </div>
          
          {/* Export Preview */}
          <div className="space-y-3">
            <h4 className="font-medium">Items to Export</h4>
            <div className="max-h-48 overflow-y-auto border rounded-lg">
              <div className="p-3 space-y-2">
                {workItems.slice(0, 10).map(item => (
                  <div key={item.id} className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <span className="truncate">{item.title}</span>
                      {item.work_item_type && (
                        <Badge variant="secondary" className="text-xs">
                          {item.work_item_type}
                        </Badge>
                      )}
                    </div>
                    <div className="text-muted-foreground">
                      {item.qvf_score ? item.qvf_score.toFixed(2) : 'No QVF'}
                    </div>
                  </div>
                ))}
                
                {workItems.length > 10 && (
                  <div className="text-sm text-muted-foreground text-center py-2">
                    ... and {workItems.length - 10} more items
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Export Actions */}
          <div className="flex justify-end space-x-3">
            <Button variant="outline" onClick={onClose} disabled={exporting}>
              Cancel
            </Button>
            <Button onClick={handleExport} disabled={exporting}>
              {exporting ? (
                'Exporting...'
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Export {selectedFormat.toUpperCase()}
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}