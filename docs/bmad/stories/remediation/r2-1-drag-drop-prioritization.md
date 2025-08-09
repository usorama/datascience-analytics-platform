---
# Agent Targeting
target-agent: frontend-developer
tools: [Read, Write, MultiEdit, Bash, Grep]

# Project Context
epic: Remediation Sprint R2 - Missing Core Features
story: Story R2.1 - Drag-and-Drop Work Item Prioritization
priority: critical
estimated-effort: 1.3 days (20 SP)
dependencies: ["R1.1 Mobile-First Redesign", "Work Item API endpoints"]

# Acceptance Criteria
acceptance-criteria: |
  - [ ] 🖱️ Drag-and-Drop Interface: Smooth drag-and-drop for work items across hierarchy levels
  - [ ] 🔄 Real-time QVF Updates: Scores recalculate instantly as items are moved
  - [ ] 👀 Visual Feedback: Clear drag indicators, drop zones, and preview states
  - [ ] 📱 Touch Support: Full drag-and-drop functionality on mobile and tablet devices
  - [ ] ⚡ Performance: <100ms response time for drag operations
  - [ ] 🔙 Undo/Redo: Complete undo/redo system for all prioritization changes
  - [ ] 💾 Auto-save: Changes persist automatically with conflict resolution
  - [ ] 🎯 Accessibility: Full keyboard navigation and screen reader support
  - [ ] 🔀 Multi-select: Bulk drag operations for multiple work items
  - [ ] 🏗️ Hierarchy Respect: Maintains Epic > Feature > Story relationships during reordering

# Technical Constraints
constraints: |
  - Must use @dnd-kit/core for accessible drag-and-drop implementation
  - Cannot break existing work item data structure or API contracts
  - Must maintain real-time QVF score calculations during drag operations
  - Touch interactions must work on iOS Safari and Android Chrome
  - Keyboard navigation must support screen readers and power users
  - Performance must handle 1000+ work items without lag
  - Auto-save must handle concurrent user editing scenarios
  - Must integrate with existing authentication and permission systems

# Implementation Context
architectural-guidance: |
  FORENSIC FINDING: Drag-and-drop functionality completely absent despite claims.
  Current work item lists are static with no interactive prioritization capabilities.
  
  Current Problems:
  - Work items displayed in static lists only
  - No prioritization interface beyond basic sorting
  - QVF scores not recalculated when order changes
  - No visual feedback for user interactions
  - Mobile users cannot reorder items at all
  - No undo functionality for accidental changes
  
  Technical Architecture Required:
  1. Implement @dnd-kit/core for accessibility and performance
  2. Create drag-and-drop context with state management
  3. Integrate real-time QVF calculation API calls
  4. Implement optimistic updates with rollback capability
  5. Add comprehensive keyboard navigation support
  6. Create touch-friendly mobile drag interactions

  Key Integration Points:
  - QVF Scoring Engine API: /api/v1/qvf/score
  - Work Item Management API: /api/v1/work-items
  - Real-time WebSocket: For collaborative editing notifications
  - Undo/Redo System: Custom implementation with state snapshots

# Quality Gates
quality-gates: |
  MANDATORY GATES (Must pass before story completion):
  
  1. DRAG-DROP FUNCTIONALITY TESTS: 100% core functionality working
     - Drag items within same hierarchy level ✓
     - Drag items between different hierarchy levels ✓
     - Real-time QVF score updates during drag ✓
     - Visual feedback and drop zones working ✓
     - Performance <100ms response time ✓
  
  2. MOBILE/TOUCH COMPATIBILITY: 100% mobile functionality
     - Touch drag on iOS Safari ✓
     - Touch drag on Android Chrome ✓ 
     - Long-press to initiate drag on mobile ✓
     - Mobile drop zones clearly visible ✓
     - Touch scroll and drag don't conflict ✓
  
  3. ACCESSIBILITY COMPLIANCE: WCAG AA standards
     - Keyboard-only navigation functional ✓
     - Screen reader announcements for drag operations ✓
     - Focus indicators visible during keyboard navigation ✓
     - ARIA labels and live regions implemented ✓
     - High contrast mode compatibility ✓
  
  4. PERFORMANCE BENCHMARKS: Production-ready performance
     - 1000+ items dragable without lag ✓
     - Memory usage stable during extended operations ✓
     - QVF recalculation <100ms per drag ✓
     - Auto-save operations don't block UI ✓
     - Virtual scrolling for large datasets ✓
  
  5. DATA INTEGRITY: Zero data loss or corruption
     - Undo/redo system preserves all changes ✓
     - Concurrent editing handled gracefully ✓
     - Auto-save with conflict resolution working ✓
     - API error handling with rollback ✓
     - Offline capability with sync on reconnect ✓
---

# User Story: Drag-and-Drop Work Item Prioritization

## Business Context
As a Product Owner managing complex backlogs, I need intuitive drag-and-drop prioritization with real-time QVF score updates so that I can efficiently reorder work items while immediately seeing the impact on business value optimization.

**CRITICAL ISSUE**: Despite claims of functional work item management, NO drag-and-drop capability exists. Current users must manually edit priority numbers, making prioritization extremely time-consuming and error-prone.

**Business Impact**:
- **Current State**: Static lists, manual priority editing, no visual prioritization
- **Target State**: Intuitive drag-and-drop with real-time QVF feedback
- **Time Savings**: 75% reduction in prioritization effort (from manual editing to drag-drop)
- **Decision Quality**: Real-time QVF updates enable better prioritization decisions
- **User Adoption**: Critical for stakeholder acceptance and daily usage

## Technical Requirements

### Current Implementation Gap
```typescript
interface CurrentLimitations {
  prioritization: "Manual number editing only";
  feedback: "No real-time QVF updates";
  mobile: "No mobile prioritization capability";
  accessibility: "No keyboard navigation for reordering";
  performance: "No optimization for large datasets";
  collaboration: "No concurrent editing support";
  undo: "No undo/redo functionality";
}
```

### Required Drag-and-Drop System
```typescript
interface DragDropSystem {
  library: '@dnd-kit/core';          // Accessible, performant library
  sensors: {
    pointer: 'PointerSensor';        // Mouse/touch hybrid
    keyboard: 'KeyboardSensor';      // Full keyboard navigation
    touch: 'TouchSensor';            // Mobile-optimized
  };
  
  features: {
    multiSelect: boolean;            // Bulk operations
    autoScroll: boolean;             // Scroll during drag
    virtualScrolling: boolean;       // Handle 1000+ items
    snapToGrid: boolean;             // Precise drop positioning
    ghostPreview: boolean;           // Drag preview
  };
  
  realTimeUpdates: {
    qvfRecalculation: '<100ms';      // Instant feedback
    optimisticUpdates: boolean;      // Immediate UI response
    rollbackCapability: boolean;     // Error recovery
    conflictResolution: 'merge' | 'last-write-wins';
  };
  
  accessibility: {
    screenReader: 'full-support';    // ARIA live regions
    keyboardNav: 'complete';         // Arrow keys, space, enter
    focusManagement: 'automatic';    // Smart focus handling
    announcements: 'contextual';     // Status updates
  };
}
```

### Drag-and-Drop State Management
```typescript
interface DragDropState {
  items: WorkItem[];                 // Current work item order
  draggedItem: WorkItem | null;      // Currently dragged item
  dropTarget: DropZone | null;       // Valid drop location
  isDragging: boolean;               // Global drag state
  
  preview: {
    position: { x: number, y: number };
    rotation: number;                // Slight rotation for realism
    scale: number;                   // Slightly smaller during drag
    opacity: number;                 // Semi-transparent
  };
  
  dropZones: DropZone[];             // Valid drop locations
  feedback: {
    validDrop: boolean;              // Visual feedback
    qvfImpact: number;               // Score change preview
    conflictWarning: string | null;   // Concurrent edit warning
  };
  
  history: {
    snapshots: StateSnapshot[];      // Undo/redo states
    currentIndex: number;            // Current history position
    maxHistory: 50;                  // Memory management
  };
}

interface WorkItem {
  id: string;
  title: string;
  type: 'epic' | 'feature' | 'story';
  priority: number;                  // Calculated from position
  qvfScore: number;                  // Current QVF score
  parentId?: string;                 // Hierarchy relationship
  estimatedEffort: number;
  businessValue: number;
  
  dragHandle: {
    accessible: boolean;             // Screen reader accessible
    touchFriendly: boolean;          // 44px minimum target
    keyboardFocusable: boolean;      // Tab navigation
  };
}
```

### Real-time QVF Integration
```typescript
interface QVFDragIntegration {
  calculation: {
    trigger: 'onDragEnd' | 'onDragMove';  // When to recalculate
    debounceMs: 100;                       // Prevent excessive API calls
    batchUpdates: boolean;                 // Multiple items at once
  };
  
  api: {
    endpoint: '/api/v1/qvf/recalculate-batch';
    method: 'POST';
    payload: {
      items: Array<{
        id: string;
        newPosition: number;
        newParentId?: string;
      }>;
      context: 'drag-drop-reorder';
    };
    response: Array<{
      id: string;
      newQvfScore: number;
      scoreChange: number;
      confidence: number;
    }>;
  };
  
  optimisticUpdates: {
    enabled: boolean;                // Update UI immediately
    rollbackOnError: boolean;        // Revert on API failure
    conflictResolution: 'merge';     // Handle concurrent edits
  };
  
  visualFeedback: {
    scorePreview: boolean;           // Show predicted scores
    impactIndicator: 'color' | 'badge' | 'both';
    animatedChanges: boolean;        // Smooth score updates
  };
}
```

## Implementation Guidance

### Phase 1: Drag-and-Drop Foundation (8 SP)
```typescript
// DragDropProvider setup with @dnd-kit/core
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  KeyboardSensor,
  TouchSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragStartEvent,
  DragMoveEvent
} from '@dnd-kit/core';

const WorkItemDragProvider: React.FC = ({ children }) => {
  const [activeId, setActiveId] = useState<string | null>(null);
  const [items, setItems] = useState<WorkItem[]>([]);
  
  // Configure sensors for different input methods
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Prevent accidental drags
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 250,    // Long press on mobile
        tolerance: 5,
      },
    })
  );
  
  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id);
    // Announce drag start to screen readers
    announceToScreenReader(`Started dragging ${event.active.data.current.title}`);
  };
  
  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    
    if (over && active.id !== over.id) {
      // Optimistic update
      const newItems = reorderItems(items, active.id, over.id);
      setItems(newItems);
      
      // Real-time QVF recalculation
      await recalculateQVFScores(newItems);
      
      // Save to backend
      await saveItemOrder(newItems);
    }
    
    setActiveId(null);
  };
  
  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      accessibility={{
        screenReaderInstructions: {
          draggable: 'To pick up a work item, press the space or enter key.',
        },
      }}
    >
      {children}
      <DragOverlay>
        {activeId ? <WorkItemDragOverlay id={activeId} /> : null}
      </DragOverlay>
    </DndContext>
  );
};
```

**Key Files to Create**:
- `/qvf-platform/apps/web/src/components/work-items/DragDropProvider.tsx`
- `/qvf-platform/apps/web/src/components/work-items/DragDropWorkItem.tsx`
- `/qvf-platform/apps/web/src/components/work-items/WorkItemDragOverlay.tsx`

### Phase 2: Real-time QVF Integration (6 SP)
```typescript
// QVF recalculation service
interface QVFUpdateService {
  async recalculateOnDrag(
    items: WorkItem[],
    draggedId: string,
    newPosition: number
  ): Promise<QVFUpdateResult> {
    // Optimistic calculation for immediate feedback
    const optimisticScores = calculateOptimisticQVF(items, draggedId, newPosition);
    
    // Update UI immediately
    updateUIOptimistically(optimisticScores);
    
    try {
      // Call backend for accurate calculation
      const response = await fetch('/api/v1/qvf/recalculate-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: items.map(item => ({
            id: item.id,
            position: item.priority,
            parentId: item.parentId
          })),
          context: 'drag-drop-reorder'
        })
      });
      
      const actualScores = await response.json();
      
      // Replace optimistic updates with actual scores
      updateUIWithActualScores(actualScores);
      
      return actualScores;
    } catch (error) {
      // Rollback optimistic updates on error
      rollbackOptimisticUpdates();
      throw error;
    }
  }
}
```

### Phase 3: Mobile Touch Optimization (3 SP)
```typescript
// Mobile-specific drag handling
const MobileDragEnhancements = {
  touchSensor: {
    activationConstraint: {
      delay: 250,        // Long press to start drag
      tolerance: 5,      // Allow small finger movement
    },
  },
  
  visualFeedback: {
    haptic: true,        // Vibration feedback on start/end
    ghostOpacity: 0.7,   // Semi-transparent drag preview
    dropZoneHighlight: true, // Clear drop zone indicators
  },
  
  scrollBehavior: {
    autoScroll: true,    // Auto-scroll when dragging near edges
    scrollSpeed: 'smooth', // Smooth scroll animation
    edgeThreshold: 50,   // Distance from edge to trigger scroll
  },
  
  accessibility: {
    largerTouchTargets: '44px', // Minimum touch target size
    clearDropZones: true,       // High contrast drop indicators  
    voiceoverSupport: true,     // iOS VoiceOver compatibility
  }
};

// Touch-optimized WorkItem component
const TouchOptimizedWorkItem: React.FC<WorkItemProps> = ({ item }) => {
  return (
    <div
      className="
        touch-manipulation           // Prevent zoom on double-tap
        select-none                 // Prevent text selection during drag
        min-h-[44px]               // Minimum touch target
        active:scale-95            // Touch feedback
        transition-transform       // Smooth interactions
      "
      {...dragHandleProps}
    >
      <div className="flex items-center p-4 bg-white border rounded-lg shadow-sm">
        {/* Drag handle - prominent on mobile */}
        <div 
          className="
            w-6 h-6 mr-3          // Touch-friendly size
            cursor-grab           // Visual drag indicator
            touch-action-none     // Prevent default touch behaviors
          "
          aria-label={`Drag handle for ${item.title}`}
        >
          <DragHandleIcon className="w-full h-full text-gray-400" />
        </div>
        
        {/* Work item content */}
        <div className="flex-1">
          <h3 className="text-base font-medium">{item.title}</h3>
          <div className="flex items-center mt-1 space-x-2">
            <QVFScoreBadge 
              score={item.qvfScore} 
              change={item.scoreChange}
              animated={true}
            />
            <EffortBadge effort={item.estimatedEffort} />
          </div>
        </div>
      </div>
    </div>
  );
};
```

### Phase 4: Accessibility & Keyboard Navigation (3 SP)
```typescript
// Comprehensive keyboard navigation
const KeyboardDragSupport = {
  keyBindings: {
    'Space': 'Pick up item',
    'Enter': 'Pick up item',
    'Escape': 'Cancel drag',
    'ArrowUp': 'Move item up',
    'ArrowDown': 'Move item down',
    'ArrowLeft': 'Move item left (decrease hierarchy)',
    'ArrowRight': 'Move item right (increase hierarchy)',
    'Home': 'Move to beginning',
    'End': 'Move to end'
  },
  
  screenReaderAnnouncements: {
    onDragStart: (item: WorkItem) => 
      `Picked up ${item.title}. Use arrow keys to move, space or enter to drop.`,
    onDragMove: (item: WorkItem, position: number) => 
      `${item.title} moved to position ${position}`,
    onDragEnd: (item: WorkItem, qvfChange: number) => 
      `${item.title} dropped. QVF score changed by ${qvfChange} points.`,
    onDragCancel: (item: WorkItem) => 
      `Drag cancelled. ${item.title} returned to original position.`
  },
  
  focusManagement: {
    retainFocus: true,      // Keep focus on dragged item
    announceDropZones: true, // Announce valid drop locations
    skipToContent: true,     // Skip navigation during drag
  }
};
```

## E2E Test Requirements

### Comprehensive Drag-Drop Test Suite
```typescript
// tests/work-items/drag-drop.spec.ts - CRITICAL TESTS
test.describe('Drag-Drop Work Item Prioritization - MANDATORY', () => {
  
  test('Basic drag and drop functionality', async ({ page }) => {
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/work-items');
    
    // Wait for work items to load
    await expect(page.locator('[data-testid="work-item"]').first()).toBeVisible();
    
    const firstItem = page.locator('[data-testid="work-item"]').first();
    const secondItem = page.locator('[data-testid="work-item"]').nth(1);
    
    // Get initial QVF scores
    const initialScore = await firstItem.locator('[data-testid="qvf-score"]').textContent();
    
    // Perform drag and drop
    await firstItem.dragTo(secondItem);
    
    // MUST PASS: Item order changed
    await expect(page.locator('[data-testid="work-item"]').first()).not.toHaveText(initialScore);
    
    // MUST PASS: QVF scores updated
    await expect(page.locator('[data-testid="qvf-score"]')).toBeVisible();
    
    // MUST PASS: Changes auto-saved
    await page.reload();
    // Verify order persists after reload
  });
  
  test('Mobile touch drag functionality', async ({ page }) => {
    await page.emulate(devices['iPhone 12']);
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/work-items');
    
    const firstItem = page.locator('[data-testid="work-item"]').first();
    const thirdItem = page.locator('[data-testid="work-item"]').nth(2);
    
    // MUST PASS: Long press initiates drag
    await firstItem.locator('[data-testid="drag-handle"]').tap({ timeout: 1000 });
    
    // MUST PASS: Touch drag works
    const firstBox = await firstItem.boundingBox();
    const thirdBox = await thirdItem.boundingBox();
    
    await page.touchscreen.tap(firstBox.x + firstBox.width/2, firstBox.y + firstBox.height/2);
    await page.touchscreen.tap(thirdBox.x + thirdBox.width/2, thirdBox.y + thirdBox.height/2);
    
    // MUST PASS: Drop zones visible during touch drag
    await expect(page.locator('[data-testid="drop-zone"]')).toBeVisible();
  });
  
  test('Keyboard navigation drag and drop', async ({ page }) => {
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/work-items');
    
    // Focus first work item
    await page.keyboard.press('Tab');
    const focusedItem = page.locator(':focus');
    await expect(focusedItem).toHaveAttribute('data-testid', 'work-item');
    
    // MUST PASS: Space key picks up item
    await page.keyboard.press('Space');
    await expect(page.locator('[aria-live="polite"]')).toContainText('Picked up');
    
    // MUST PASS: Arrow keys move item
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowDown');
    
    // MUST PASS: Space key drops item
    await page.keyboard.press('Space');
    await expect(page.locator('[aria-live="polite"]')).toContainText('dropped');
    
    // MUST PASS: Screen reader announcements
    const announcements = await page.locator('[aria-live="polite"]').textContent();
    expect(announcements).toContain('QVF score changed');
  });
  
  test('Real-time QVF score updates', async ({ page }) => {
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/work-items');
    
    const firstItem = page.locator('[data-testid="work-item"]').first();
    const lastItem = page.locator('[data-testid="work-item"]').last();
    
    // Get initial QVF score
    const initialScore = await firstItem.locator('[data-testid="qvf-score"]').textContent();
    
    // Drag to significantly different position
    await firstItem.dragTo(lastItem);
    
    // MUST PASS: QVF score recalculated within 100ms
    await expect(async () => {
      const newScore = await firstItem.locator('[data-testid="qvf-score"]').textContent();
      expect(newScore).not.toBe(initialScore);
    }).toPass({ timeout: 100 });
    
    // MUST PASS: Visual feedback shows score change
    const scoreChange = page.locator('[data-testid="score-change-indicator"]');
    await expect(scoreChange).toBeVisible();
  });
  
  test('Undo/Redo functionality', async ({ page }) => {
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/work-items');
    
    // Get initial state
    const initialOrder = await page.locator('[data-testid="work-item-title"]').allTextContents();
    
    // Perform drag operation
    await page.locator('[data-testid="work-item"]').first().dragTo(
      page.locator('[data-testid="work-item"]').last()
    );
    
    // MUST PASS: Undo button available and functional
    const undoButton = page.locator('[data-testid="undo-button"]');
    await expect(undoButton).toBeEnabled();
    await undoButton.click();
    
    // MUST PASS: State reverted to original
    const undoneOrder = await page.locator('[data-testid="work-item-title"]').allTextContents();
    expect(undoneOrder).toEqual(initialOrder);
    
    // MUST PASS: Redo button functional
    const redoButton = page.locator('[data-testid="redo-button"]');
    await expect(redoButton).toBeEnabled();
    await redoButton.click();
    
    // Verify redo worked
    const redoneOrder = await page.locator('[data-testid="work-item-title"]').allTextContents();
    expect(redoneOrder).not.toEqual(initialOrder);
  });
  
  test('Performance with large datasets', async ({ page }) => {
    // Load test data with 1000+ items
    await setupLargeDataset(page, 1000);
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/work-items');
    
    // MUST PASS: Page loads with virtual scrolling
    await expect(page.locator('[data-testid="virtual-list"]')).toBeVisible();
    
    const startTime = Date.now();
    
    // Drag item in large dataset
    await page.locator('[data-testid="work-item"]').first().dragTo(
      page.locator('[data-testid="work-item"]').nth(10)
    );
    
    const dragTime = Date.now() - startTime;
    
    // MUST PASS: Drag operation completes in <100ms
    expect(dragTime).toBeLessThan(100);
    
    // MUST PASS: UI remains responsive
    await expect(page.locator('[data-testid="loading-indicator"]')).not.toBeVisible();
  });
});
```

## Performance Requirements

### Drag-Drop Performance Targets
```typescript
interface DragDropPerformance {
  dragInitiation: '<50ms';           // Time to start drag
  dragResponse: '<16ms';             // 60fps during drag
  dropConfirmation: '<100ms';        // Time to complete drop
  qvfRecalculation: '<100ms';        // Score update time
  autoSave: '<500ms';               // Background save time
  
  scalability: {
    maxItems: 10000;                // Virtual scrolling threshold
    memoryUsage: '<50MB';           // Memory efficiency
    cpuUsage: '<25%';               // CPU efficiency during drag
  };
  
  responsiveness: {
    touchResponse: '<100ms';         // Mobile touch feedback
    keyboardResponse: '<50ms';       // Keyboard navigation
    visualFeedback: '<16ms';         // Animation frame rate
  };
}
```

## Definition of Done

### Technical Completion Criteria
- [ ] **Core Functionality**: Drag-drop works for all work item types (Epic, Feature, Story)
- [ ] **Real-time Updates**: QVF scores recalculate within 100ms of drop
- [ ] **Mobile Support**: Full touch functionality on iOS Safari and Android Chrome
- [ ] **Accessibility**: WCAG AA compliant keyboard navigation and screen reader support
- [ ] **Performance**: Handles 1000+ items with <100ms drag response time
- [ ] **Data Integrity**: Undo/redo system with conflict resolution
- [ ] **Auto-save**: Automatic persistence with offline capability

### Quality Gate Verification
- [ ] **E2E Tests**: 100% critical drag-drop test scenarios passing
- [ ] **Performance Tests**: All performance benchmarks met under load
- [ ] **Accessibility Audit**: Screen reader and keyboard navigation verified
- [ ] **Mobile Testing**: Verified on 5 real devices by QA team
- [ ] **Load Testing**: 1000+ item dataset performance verified
- [ ] **Integration Testing**: QVF API integration working correctly

### Business Value Delivered
- [ ] **Productivity**: 75% reduction in prioritization time
- [ ] **Decision Quality**: Real-time QVF feedback improves prioritization accuracy  
- [ ] **User Satisfaction**: Intuitive drag-drop interface increases daily usage
- [ ] **Mobile Access**: Product owners can prioritize on mobile devices
- [ ] **Collaboration**: Multiple users can safely edit priorities simultaneously

This story transforms static work item lists into an interactive, intuitive prioritization tool that makes QVF-driven decision-making fast and engaging for all stakeholders.