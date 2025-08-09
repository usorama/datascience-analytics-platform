'use client'

import { DragDropDemo } from '@/components/work-items/drag-drop-demo'

export default function DragDropDemoPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Drag & Drop Demo</h1>
        <p className="text-muted-foreground">
          Interactive demonstration of the QVF Platform&apos;s drag-and-drop prioritization feature
        </p>
      </div>
      <DragDropDemo />
    </div>
  )
}