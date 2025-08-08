'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Calculator, Edit, Download, Trash2 } from 'lucide-react'

interface BulkOperationsProps {
  selectedItems: string[]
  onOperation: (operation: string, itemIds: string[]) => void
}

export function BulkOperations({ selectedItems, onOperation }: BulkOperationsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={() => onOperation('recalculate-qvf', selectedItems)}
      >
        <Calculator className="h-4 w-4 mr-2" />
        Recalculate QVF
      </Button>
      
      <Button
        variant="outline"
        size="sm"
        onClick={() => onOperation('bulk-edit', selectedItems)}
      >
        <Edit className="h-4 w-4 mr-2" />
        Bulk Edit
      </Button>
      
      <Button
        variant="outline"
        size="sm"
        onClick={() => onOperation('export', selectedItems)}
      >
        <Download className="h-4 w-4 mr-2" />
        Export
      </Button>
      
      <Button
        variant="outline"
        size="sm"
        className="text-red-600 hover:text-red-800"
        onClick={() => {
          if (confirm(`Delete ${selectedItems.length} selected items?`)) {
            onOperation('bulk-delete', selectedItems)
          }
        }}
      >
        <Trash2 className="h-4 w-4 mr-2" />
        Delete
      </Button>
    </div>
  )
}