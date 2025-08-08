# LiveKit Design System Specification

## Overview

The LiveKit Design System is a comprehensive guide for building consistent, accessible, and visually striking interfaces that align with LiveKit's brand identity. This system emphasizes a dark-mode-first approach with vibrant cyan accents, creating a modern, technical aesthetic suitable for developer-focused products.

## Core Principles

### 1. **Dark-Mode First**
- All interfaces default to dark backgrounds to reduce eye strain during extended coding sessions
- Light text on dark backgrounds ensures high readability
- Dark themes align with modern development tools and terminals

### 2. **Technical Elegance**
- Clean, minimalist design that doesn't distract from content
- Geometric shapes and grid-based layouts reflect precision and reliability
- Technical diagrams and visualizations use subtle animations

### 3. **Accessibility**
- WCAG AA compliance minimum for all color combinations
- Clear typography hierarchy for easy scanning
- Consistent interactive states for all components

### 4. **Developer-Centric**
- Design patterns familiar to developers
- Code-like aesthetics where appropriate
- Performance-optimized animations and transitions

## Color System

### Background Colors
- **Primary Background** (#0A0A0A): Main application background
- **Secondary Background** (#111111): Elevated surfaces, sidebars
- **Tertiary Background** (#1A1A1A): Cards, panels, input fields
- **Elevated Background** (#1F1F1F): Modals, dropdowns, popovers

### Text Colors
- **Primary Text** (#FFFFFF): Headings, important content
- **Secondary Text** (#A3A3A3): Body text, descriptions
- **Tertiary Text** (#737373): Captions, metadata
- **Muted Text** (#525252): Placeholder text, disabled states

### Accent Colors
- **Primary Accent** (#00D9FF): CTAs, primary buttons, links
- **Accent Hover** (#33E5FF): Interactive hover states
- **Accent Pressed** (#007AA3): Active/pressed states
- **Accent Light** (rgba(0, 217, 255, 0.1)): Backgrounds, overlays

### Semantic Colors
- **Success** (#10B981): Positive actions, confirmations
- **Warning** (#F59E0B): Cautions, important notices
- **Error** (#EF4444): Errors, destructive actions
- **Info** (#3B82F6): Informational messages

## Typography

### Font Stack
```css
/* Primary */
font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;

/* Monospace */
font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, 'Courier New', monospace;
```

### Type Scale
- **Hero**: 72px / 4.5rem - Marketing headlines
- **H1**: 48px / 3rem - Page titles
- **H2**: 36px / 2.25rem - Section headers
- **H3**: 30px / 1.875rem - Subsections
- **H4**: 24px / 1.5rem - Card titles
- **H5**: 20px / 1.25rem - Labels
- **Body**: 16px / 1rem - Default text
- **Small**: 14px / 0.875rem - Secondary text
- **Caption**: 12px / 0.75rem - Metadata

### Font Weights
- **Light**: 300 - Large display text only
- **Regular**: 400 - Body text
- **Medium**: 500 - Emphasis without bold
- **Semibold**: 600 - Subheadings
- **Bold**: 700 - Headlines, CTAs

### Line Heights
- **Tight**: 1.1 - Headlines
- **Snug**: 1.2 - Subheadings
- **Normal**: 1.5 - Body text
- **Relaxed**: 1.625 - Long-form content
- **Loose**: 2.0 - Code blocks

## Spacing System

Based on a 4px base unit:
- **1**: 4px / 0.25rem
- **2**: 8px / 0.5rem
- **3**: 12px / 0.75rem
- **4**: 16px / 1rem
- **5**: 20px / 1.25rem
- **6**: 24px / 1.5rem
- **8**: 32px / 2rem
- **10**: 40px / 2.5rem
- **12**: 48px / 3rem
- **16**: 64px / 4rem
- **20**: 80px / 5rem
- **24**: 96px / 6rem

### Spacing Guidelines
- **Component padding**: 12-16px for small, 16-24px for medium, 24-32px for large
- **Section spacing**: 48-64px between major sections
- **Grid gaps**: 24px default, 16px on mobile
- **Inline spacing**: 8px between related elements, 16px between groups

## Components

### Buttons

#### Primary Button
- Background: #00D9FF
- Text: #0A0A0A (dark text for contrast)
- Padding: 12px 24px
- Border radius: 8px
- Font weight: 600
- Hover: Lighten background by 10%, add glow shadow
- Active: Darken background by 20%
- Disabled: #404040 background, #737373 text

#### Secondary Button
- Background: Transparent
- Border: 1px solid #00D9FF
- Text: #00D9FF
- Hover: Add 10% opacity background fill
- Active: Add 20% opacity background fill

#### Ghost Button
- Background: Transparent
- Text: #A3A3A3
- Hover: Text becomes #FFFFFF, subtle background

### Input Fields
- Background: #1A1A1A
- Border: 1px solid #262626
- Border radius: 8px
- Padding: 12px 16px
- Focus: Border color #00D9FF with glow
- Error: Border color #EF4444
- Placeholder: #737373

### Cards
- Background: #1A1A1A
- Border: 1px solid #262626
- Border radius: 16px
- Padding: 24px
- Shadow: Subtle dark shadow
- Hover: Slight border lightening

### Navigation
- Background: rgba(10, 10, 10, 0.95) with backdrop blur
- Height: 64px
- Border bottom: 1px solid #262626
- Logo area: 180px width
- Nav items: 14px font, #A3A3A3 default, #FFFFFF hover

### Code Blocks
- Background: #1A1A1A
- Border: 1px solid #262626
- Border radius: 8px
- Padding: 16px
- Font: JetBrains Mono, 14px
- Syntax highlighting:
  - Keywords: #00D9FF
  - Strings: #10B981
  - Numbers: #F59E0B
  - Comments: #737373
  - Functions: #3B82F6

## Layout & Grid

### Container
- Max width: 1280px
- Padding: 16px (mobile), 24px (tablet), 32px (desktop)
- Center aligned with auto margins

### Grid System
- 12-column grid
- Gap: 24px default
- Responsive breakpoints:
  - Mobile: < 640px (1-2 columns)
  - Tablet: 640px - 1024px (2-4 columns)
  - Desktop: > 1024px (12 columns)

### Breakpoints
- **xs**: 0px - 639px
- **sm**: 640px - 767px
- **md**: 768px - 1023px
- **lg**: 1024px - 1279px
- **xl**: 1280px - 1535px
- **2xl**: 1536px+

## Animation & Motion

### Timing
- **Instant**: 0ms - State changes
- **Fast**: 150ms - Hover effects
- **Normal**: 250ms - Most transitions
- **Slow**: 350ms - Complex animations
- **Slower**: 500ms - Page transitions

### Easing Functions
- **Ease Out**: cubic-bezier(0, 0, 0.2, 1) - Default for most animations
- **Ease In Out**: cubic-bezier(0.4, 0, 0.2, 1) - Smooth transitions
- **Bounce**: cubic-bezier(0.68, -0.55, 0.265, 1.55) - Playful interactions

### Animation Guidelines
- Use subtle animations to indicate state changes
- Avoid animations longer than 500ms for interactions
- Reduce motion for accessibility preferences
- Technical diagrams can have continuous subtle animations

## Visual Elements

### Borders
- Default: 1px solid #262626
- Accent: 1px solid #00D9FF
- Subtle: 1px solid #1F1F1F
- Strong: 1px solid #404040

### Border Radius
- Small: 2px - Badges, tags
- Default: 4px - Small buttons
- Medium: 6px - Inputs
- Large: 8px - Buttons, dropdowns
- XL: 12px - Cards
- 2XL: 16px - Modals
- 3XL: 24px - Large cards
- Full: 9999px - Pills, avatars

### Shadows
- None: Flat elements
- Small: Subtle depth for cards
- Medium: Dropdowns, popovers
- Large: Modals
- Glow: 0 0 20px rgba(0, 217, 255, 0.3) - Accent elements
- Glow Large: 0 0 40px rgba(0, 217, 255, 0.4) - Hero elements

## Icons & Graphics

### Icon Guidelines
- Size: 16px (small), 20px (default), 24px (large)
- Color: Match text color hierarchy
- Stroke width: 1.5px - 2px
- Style: Outlined, geometric, minimal

### Technical Diagrams
- Grid background: rgba(255, 255, 255, 0.05) lines
- Connection lines: 1px with slight glow
- Node elements: Rounded rectangles with borders
- Animation: Subtle pulse or flow effects

## Accessibility

### Color Contrast
- Normal text: Minimum 4.5:1 contrast ratio
- Large text: Minimum 3:1 contrast ratio
- Interactive elements: Minimum 3:1 against background
- Focus indicators: Visible and high contrast

### Keyboard Navigation
- All interactive elements keyboard accessible
- Clear focus states with accent color outline
- Tab order follows visual hierarchy
- Skip links for main navigation

### Screen Readers
- Semantic HTML structure
- ARIA labels for complex interactions
- Alt text for all informative images
- Descriptive link text

## Implementation Guidelines

### CSS Variables
```css
:root {
  --color-bg-primary: #0A0A0A;
  --color-bg-secondary: #111111;
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #A3A3A3;
  --color-accent: #00D9FF;
  --font-primary: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
  --spacing-unit: 4px;
  --radius-default: 8px;
  --transition-fast: 150ms ease-out;
}
```

### Dark Mode Implementation
- Always start with dark mode as default
- Use CSS custom properties for theming
- Ensure all images work on dark backgrounds
- Test contrast ratios for all color combinations

### Performance
- Limit animations to transform and opacity
- Use will-change sparingly
- Lazy load images and heavy components
- Optimize font loading with font-display: swap

### Responsive Design
- Mobile-first approach
- Fluid typography with clamp()
- Flexible grid layouts
- Touch-friendly tap targets (minimum 44px)

## Best Practices

1. **Consistency**: Use design tokens consistently across all implementations
2. **Hierarchy**: Establish clear visual hierarchy with typography and spacing
3. **Feedback**: Provide immediate visual feedback for all interactions
4. **Simplicity**: Favor clarity over complexity in design decisions
5. **Documentation**: Keep design documentation updated with implementation
6. **Testing**: Test designs across devices and accessibility tools
7. **Performance**: Monitor and optimize for performance metrics
8. **Evolution**: Design system should evolve based on user feedback

## Version Control

- **Current Version**: 1.0.0
- **Last Updated**: January 2025
- **Changelog**: Document all changes to design tokens
- **Deprecation**: Provide migration guides for breaking changes

---

*This design system is optimized for building modern, developer-focused applications with a technical aesthetic. It prioritizes functionality, accessibility, and visual consistency while maintaining the unique LiveKit brand identity.*