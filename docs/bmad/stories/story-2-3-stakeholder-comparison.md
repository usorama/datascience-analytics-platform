---
# Agent Targeting
target-agent: frontend-developer
tools: [Read, Write, MultiEdit, Bash]
coordinate-with:
  - agent: backend-developer
    deliverable: Real-time AHP calculation and consistency validation
    timing: parallel-development
    priority: critical

# Project Context
epic: QVF Frontend Application  
story: Story 2.3 - Stakeholder Comparison Interface
priority: high
estimated-effort: 0.5 days (15 SP)
dependencies: ["QVF AHP Engine Complete", "Real-time WebSocket Infrastructure"]

# Acceptance Criteria
acceptance-criteria: |
  - [ ] Intuitive pairwise comparison matrix with clear visual controls
  - [ ] Real-time consistency ratio calculation with live feedback (<1 second)
  - [ ] Visual highlighting of inconsistent judgment pairs with guidance
  - [ ] Progress tracking showing completion status through comparison process
  - [ ] Collaborative features for group stakeholder sessions with multi-user support  
  - [ ] Save and resume capability for lengthy comparison sessions
  - [ ] Mobile-optimized interface for various stakeholder device preferences
  - [ ] Integration with QVF calculation engine for immediate priority updates
  - [ ] Export capabilities for comparison matrices and results
  - [ ] Accessibility compliance for inclusive stakeholder participation

# Technical Constraints
constraints: |
  - Must integrate directly with existing AHP engine at /src/datascience_platform/ado/ahp.py
  - Real-time consistency validation with <1 second response time
  - Support for up to 9 QVF criteria in pairwise comparison matrix (AHP limit)
  - WebSocket integration for collaborative sessions and real-time updates
  - Touch-friendly interface optimized for tablet and mobile use
  - Session persistence for comparison resumption across browser sessions
  - Graceful handling of network interruptions during comparison sessions
  - Integration with QVF orchestrator for immediate priority recalculation

# Implementation Context
architectural-guidance: |
  The Stakeholder Comparison Interface is the critical user-facing component
  where business stakeholders input their judgments that drive the entire QVF
  prioritization system. This interface must be intuitive, responsive, and
  seamlessly integrated with the mathematical AHP engine.
  
  Key integration points:
  - /src/datascience_platform/ado/ahp.py - Core AHP calculation engine
  - /src/datascience_platform/qvf/orchestration/orchestrator.py - QVF orchestration
  - /src/datascience_platform/qvf/core/criteria.py - QVF criteria configuration
  - /src/datascience_platform/qvf/api/main.py - API endpoints for comparison data
  
  Create stakeholder-specific components:
  - /src/datascience_platform/qvf/ui/stakeholder/ - Stakeholder interface module
  - Real-time comparison matrix component
  - Consistency validation feedback system
  - Collaborative session management

technical-specifications: |
  ```typescript
  interface StakeholderComparisonInterface {
    session: ComparisonSession;
    matrix: PairwiseComparisonMatrix;
    consistency: ConsistencyAnalysis;
    progress: ComparisonProgress;
    collaboration: CollaborationState;
  }
  
  interface ComparisonSession {
    id: string;
    stakeholderId: string;
    stakeholderRole: string;
    criteria: QVFCriterion[];
    startTime: Date;
    lastSaveTime?: Date;
    isComplete: boolean;
    isCollaborative: boolean;
    participants?: SessionParticipant[];
  }
  
  interface PairwiseComparisonMatrix {
    size: number;                        // Number of criteria (max 9 for AHP)
    comparisons: PairwiseComparison[];
    completedComparisons: number;
    totalComparisons: number;            // n*(n-1)/2 for n criteria
    currentComparison: PairwiseComparison;
  }
  
  interface PairwiseComparison {
    id: string;
    criterionA: QVFCriterion;
    criterionB: QVFCriterion;
    value: number;                       // 1/9 to 9 (Saaty scale)
    confidence: number;                  // 1-5 stakeholder confidence
    reasoning?: string;                  // Optional justification
    timestamp: Date;
    stakeholderId: string;
  }
  
  interface ConsistencyAnalysis {
    consistencyRatio: number;            // 0-1, <0.1 is acceptable
    isConsistent: boolean;               // CR < 0.1
    inconsistentPairs: InconsistentPair[];
    suggestions: ConsistencySuggestion[];
    maxEigenvalue: number;
    consistencyIndex: number;
  }
  
  interface InconsistentPair {
    comparisonIds: [string, string, string]; // Three related comparisons
    suggestedValues: [number, number, number];
    currentInconsistency: number;
    recommendedAction: 'review_first' | 'review_second' | 'review_third';
  }
  ```

performance-requirements: |
  - Matrix rendering: <200ms for 9x9 comparison matrix
  - Consistency calculation: <1 second for real-time validation
  - Comparison input response: <100ms for immediate user feedback
  - Session save: <500ms for comparison data persistence
  - Collaborative sync: <300ms for multi-user comparison updates
  - Mobile responsiveness: Touch targets >44px for accessibility
  - Network resilience: Graceful handling of 10-second network outages

testing-requirements: |
  Unit Tests:
  - Pairwise comparison matrix rendering and interaction
  - Real-time consistency ratio calculation and validation
  - Comparison value input validation and Saaty scale enforcement
  - Session save/resume functionality across browser refreshes
  - Inconsistent pair identification and suggestion generation
  - Mobile touch interaction and responsive layout
  
  Integration Tests:  
  - AHP engine integration for consistency calculation
  - WebSocket real-time collaboration functionality
  - QVF orchestrator integration for priority recalculation
  - Session persistence and restoration
  - Export functionality for comparison matrices
  
  E2E Tests:
  - Complete stakeholder comparison workflow from start to finish
  - Collaborative multi-stakeholder session with conflict resolution
  - Mobile stakeholder experience on tablet devices
  - Comparison session interruption and successful resume
---

# User Story: Stakeholder Comparison Interface

## Business Context
As a business stakeholder participating in QVF prioritization sessions, I need an intuitive and efficient interface for conducting pairwise comparisons between QVF criteria so that I can provide accurate judgments about relative importance that will drive optimal work item prioritization across our organization.

This interface is the critical input mechanism for the entire QVF system, where stakeholder expertise and business judgment are captured and transformed into mathematical weights that optimize value delivery. The interface must be accessible to non-technical stakeholders while maintaining the mathematical rigor required for valid AHP analysis.

The stakeholder comparison interface is essential for:
- **Business Judgment Capture**: Converting stakeholder expertise into quantitative criteria weights
- **Collaborative Decision Making**: Enabling group stakeholder sessions for consensus building
- **Transparency**: Providing clear visibility into how prioritization decisions are made
- **Consistency Validation**: Ensuring stakeholder judgments are mathematically consistent
- **Accessibility**: Accommodating diverse stakeholder roles and technical comfort levels

## Detailed Functional Requirements

### 1. Intuitive Pairwise Comparison Matrix

The core interface presents stakeholder comparisons in an easy-to-understand format:

**Matrix Presentation**:
- **Clear Criteria Labels**: Each QVF criterion clearly labeled with name and brief description
- **Comparison Question Format**: "How much more important is [Criterion A] compared to [Criterion B]?"
- **Visual Comparison Scale**: Clear visual representation of the 1-9 Saaty scale with descriptive labels
- **Progress Indicator**: Visual progress bar showing completion status (e.g., "5 of 36 comparisons complete")
- **Current Comparison Highlight**: Clear indication of which comparison is currently being made

**Comparison Input Methods**:
- **Slider Control**: Intuitive slider for selecting comparison values with Saaty scale markers
- **Click-to-Select**: Discrete buttons for exact Saaty scale values (1, 3, 5, 7, 9 and reciprocals)
- **Quick Selection**: One-click options for "Equal Importance" (1) and common values
- **Keyboard Navigation**: Full keyboard accessibility for comparison input
- **Voice Input**: Optional voice input for accessibility ("Criterion A is moderately more important")

**Comparison Context**:
- **Criterion Descriptions**: Expandable descriptions for each QVF criterion with examples
- **Historical Context**: Reference to previous comparison sessions or organizational precedent
- **Impact Examples**: Concrete examples of how each criterion affects business outcomes
- **Reciprocal Understanding**: Clear indication that selecting "A > B" automatically sets "B < A"

### 2. Real-Time Consistency Validation

Immediate feedback on judgment consistency using AHP mathematical validation:

**Live Consistency Calculation**:
- **Real-Time CR Display**: Consistency ratio updated after each comparison input
- **Visual Consistency Indicator**: Color-coded indicator (green: consistent, yellow: borderline, red: inconsistent)
- **Consistency Trend**: How consistency is changing as more comparisons are completed
- **Mathematical Transparency**: Option to view detailed consistency calculations for interested stakeholders

**Inconsistency Identification**:
- **Problem Pair Highlighting**: Visual highlighting of comparison pairs contributing to inconsistency
- **Inconsistency Explanation**: Plain-language explanation of what inconsistency means
- **Severity Indication**: Relative severity of different inconsistent judgments
- **Resolution Guidance**: Step-by-step guidance for resolving consistency issues

**Consistency Improvement Suggestions**:
- **Suggested Adjustments**: Specific suggestions for improving consistency (e.g., "Consider changing NPV vs. Risk from 7 to 5")
- **Multiple Options**: Several different paths to achieve consistency
- **Impact Preview**: How each suggested change would affect overall consistency
- **Minimal Change Approach**: Suggestions that require the fewest judgment modifications

### 3. Collaborative Session Management

Support for group stakeholder sessions with real-time collaboration:

**Multi-User Session Setup**:
- **Session Creation**: Simple setup for collaborative comparison sessions
- **Participant Invitation**: Easy invitation system for relevant stakeholders
- **Role Assignment**: Different roles (facilitator, participant, observer) with appropriate permissions
- **Session Scheduling**: Integration with calendar systems for session planning

**Real-Time Collaboration Features**:
- **Live Comparison Sharing**: All participants see comparisons as they're made
- **Discussion Integration**: Built-in chat or comment system for comparison discussion
- **Voting Mechanism**: When stakeholders disagree, voting system for consensus building
- **Conflict Resolution**: Process for resolving disagreements between stakeholders
- **Session Recording**: Optional recording of comparison rationale and discussion

**Facilitation Tools**:
- **Facilitator Controls**: Special controls for session facilitators to guide the process
- **Comparison Ownership**: Track which stakeholder provided each comparison
- **Group Consensus View**: Visual representation of group agreement/disagreement
- **Decision Tracking**: Record of final decisions and rationale for future reference

### 4. Session Persistence and Resume Capability

Robust session management for lengthy comparison processes:

**Automatic Session Saving**:
- **Continuous Auto-Save**: Comparisons saved automatically after each input
- **Session State Persistence**: Complete session state preserved across browser sessions
- **Multi-Device Support**: Start session on one device, continue on another
- **Offline Capability**: Limited offline functionality with sync when connection restored

**Session Management**:
- **Session History**: List of previous comparison sessions with timestamps
- **Session Templates**: Save comparison sessions as templates for similar future exercises
- **Session Sharing**: Share session links with stakeholders for asynchronous completion
- **Session Archiving**: Archive completed sessions for historical reference

**Resume and Continuation**:
- **Smart Resume**: Resume exactly where previous session was left off
- **Progress Recovery**: Recover progress even after browser crashes or network issues
- **Change Tracking**: Track changes made since last session for review
- **Version Control**: Maintain versions of comparison sessions for comparison

### 5. Mobile and Accessibility Optimization

Comprehensive support for diverse stakeholder needs and devices:

**Mobile-First Design**:
- **Touch-Optimized Controls**: Large touch targets optimized for finger interaction
- **Responsive Layout**: Optimal layout for phones, tablets, and desktop devices
- **Gesture Support**: Intuitive gestures for comparison input (swipe, pinch, tap)
- **Orientation Support**: Works effectively in both portrait and landscape modes

**Accessibility Features**:
- **Screen Reader Support**: Full ARIA compliance for screen reader accessibility
- **Keyboard Navigation**: Complete functionality available via keyboard only
- **High Contrast Mode**: High contrast visual mode for visually impaired users
- **Large Text Support**: Scalable text that maintains usability at larger sizes
- **Voice Control**: Voice input for users with limited mobility

**Inclusive Design**:
- **Language Localization**: Support for multiple languages based on organizational needs
- **Cultural Considerations**: Comparison scale adaptation for different cultural contexts
- **Cognitive Load Reduction**: Simplified interface options for users preferring minimal complexity
- **Help Integration**: Contextual help available at every step without leaving the interface

### 6. Integration with QVF Calculation Engine

Seamless integration with the broader QVF system:

**Real-Time Priority Updates**:
- **Immediate Calculation**: QVF priorities recalculated immediately after comparison completion
- **Impact Visualization**: Show how comparison changes affect work item priorities
- **Preview Mode**: Preview priority changes before committing comparison session
- **Rollback Capability**: Ability to rollback comparisons and see impact on priorities

**Data Export and Integration**:
- **Matrix Export**: Export comparison matrices in various formats (Excel, PDF, CSV)
- **Integration APIs**: RESTful APIs for integration with other organizational systems
- **Audit Trail**: Complete audit trail of who made what comparisons and when
- **Compliance Reporting**: Reports suitable for compliance and governance requirements

**Quality Assurance**:
- **Comparison Validation**: Validate comparisons against business rules and constraints
- **Anomaly Detection**: Identify unusual comparison patterns that may indicate errors
- **Cross-Session Consistency**: Compare consistency across multiple comparison sessions
- **Stakeholder Feedback**: Collect feedback on comparison process for continuous improvement

## Technical Implementation Requirements

### Real-Time AHP Integration
```typescript
class StakeholderComparisonManager {
  private ahpEngine: AHPEngine;
  private webSocketManager: WebSocketManager;
  private consistencyValidator: ConsistencyValidator;
  
  async updateComparison(comparison: PairwiseComparison): Promise<ConsistencyResult> {
    // Update comparison matrix
    await this.updateMatrix(comparison);
    
    // Calculate consistency in real-time
    const consistencyResult = await this.ahpEngine.calculateConsistency(this.matrix);
    
    // Broadcast to collaborative session participants
    if (this.isCollaborativeSession) {
      await this.webSocketManager.broadcast('consistency-update', consistencyResult);
    }
    
    return consistencyResult;
  }
  
  async identifyInconsistencies(): Promise<InconsistentPair[]> {
    return await this.consistencyValidator.findInconsistentPairs(this.matrix);
  }
}
```

### Collaborative Session Architecture
```python
class CollaborativeComparisonSession:
    """Manages multi-stakeholder comparison sessions."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.participants = []
        self.comparison_state = ComparisonMatrix()
        self.websocket_manager = WebSocketManager()
    
    async def handle_comparison_input(self, stakeholder_id: str, comparison: PairwiseComparison):
        # Validate stakeholder permission
        if not await self.validate_stakeholder_permission(stakeholder_id):
            return await self.send_error(stakeholder_id, "Permission denied")
        
        # Apply comparison and calculate consistency
        await self.comparison_state.update_comparison(comparison)
        consistency = await self.calculate_consistency()
        
        # Broadcast update to all session participants
        await self.websocket_manager.broadcast_to_session(
            self.session_id, 
            {'type': 'comparison_update', 'comparison': comparison, 'consistency': consistency}
        )
```

### Performance Optimization
- **Matrix Virtualization**: Virtual rendering for large comparison matrices
- **Calculation Caching**: Cache AHP calculations to avoid redundant computation
- **Progressive Loading**: Load comparison interface progressively for faster startup
- **Optimistic Updates**: Update UI immediately, sync with server asynchronously
- **Connection Resilience**: Queue operations during network outages for later sync

## Success Metrics and Validation

### User Experience Success Criteria
- **Completion Rate**: 95% of stakeholders complete comparison sessions
- **Time to Complete**: Average 15 minutes for 9-criteria comparison session
- **Consistency Achievement**: 85% of sessions achieve acceptable consistency (CR < 0.1)
- **Mobile Usage**: 40% of comparison sessions completed on mobile devices
- **Collaboration Usage**: 60% of comparison sessions involve multiple stakeholders

### Business Impact Measures  
- **Decision Confidence**: 90% of stakeholders report high confidence in comparison results
- **Process Efficiency**: 50% reduction in time spent on prioritization discussions
- **Consensus Building**: 80% of collaborative sessions reach consensus without external intervention
- **Adoption Rate**: 95% of intended stakeholder groups actively use the interface
- **Judgment Quality**: Improved consistency in prioritization decisions across sessions

## Implementation Phases

### Phase 1: Core Comparison Interface (Week 1)
- Basic pairwise comparison matrix with Saaty scale
- Real-time consistency calculation and display  
- Session persistence and resume capability
- Mobile-responsive design

### Phase 2: Collaboration Features (Week 2)
- Multi-user session support with WebSocket integration
- Real-time collaboration with conflict resolution
- Discussion and comment integration
- Session facilitation tools

### Phase 3: Advanced Features (Week 3)
- Accessibility compliance and inclusive design
- Export capabilities and integration APIs
- Advanced inconsistency resolution tools
- Performance optimization and caching

### Phase 4: Integration and Polish (Week 4)
- Full QVF system integration with priority updates
- Comprehensive testing and validation
- User training materials and documentation
- Production deployment and monitoring

This Stakeholder Comparison Interface will serve as the critical bridge between business stakeholder expertise and the mathematical rigor of the QVF system, ensuring that organizational priorities are based on transparent, consistent, and well-informed stakeholder judgments.