# Dave - UI Guidelines

This document defines the visual design system for Dave. Follow these guidelines when creating new components to maintain consistency.

---

## Color Palette

### Primary Colors
```css
--bg-primary: #0a0a0f;        /* Main background - almost black */
--bg-secondary: #0f0f16;      /* Secondary background */
--bg-card: rgba(18, 18, 26, 0.6);   /* Card backgrounds with transparency */
--bg-input: rgba(14, 14, 20, 0.8);  /* Input field backgrounds */
```

### Accent Colors (Lima/Neon Green)
```css
--accent-primary: #F0FF3D;    /* Primary accent - lime yellow */
--accent-secondary: #c8e600;  /* Secondary accent - darker lime */
--accent-dim: #9cb800;        /* Dimmed accent */
--accent-glow: rgba(240, 255, 61, 0.5);  /* Glow effect */
```

### Secondary Accents
```css
--accent-teal: #00d4aa;       /* Teal for success/secondary highlights */
--accent-cyan: #00e5ff;       /* Cyan for info/tertiary */
```

### Text Colors
```css
--text-primary: #ffffff;      /* Primary text - white */
--text-secondary: #a1a1aa;    /* Secondary text - zinc-400 */
--text-muted: #71717a;        /* Muted text - zinc-500 */
```

### Borders
```css
--border-color: rgba(255, 255, 255, 0.06);  /* Subtle borders */
--border-glow: rgba(240, 255, 61, 0.3);     /* Glowing borders */
```

---

## Typography

- **Font Family**: System default (inherited from Tailwind)
- **Headings**: `font-semibold` or `font-bold`, white color
- **Body**: Regular weight, `text-zinc-300` or `text-zinc-400`
- **Muted**: `text-zinc-500` or `text-zinc-600`

### Size Scale
```
text-xs   - 12px - Labels, badges
text-sm   - 14px - Secondary text, inputs
text-base - 16px - Body text
text-lg   - 18px - Section headings
text-xl   - 20px - Page headings
text-2xl  - 24px - Major headings
text-3xl  - 30px - Hero text
```

---

## Components

### Glass Card
The primary container for content. Uses glassmorphism effect.

```tsx
<div className="glass-card p-6">
  {/* Content */}
</div>
```

CSS:
```css
.glass-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
}
```

### Primary Button (Gradient)
Main action buttons with lime gradient.

```tsx
<button className="px-6 py-3 btn-gradient rounded-xl font-semibold">
  Action
</button>
```

Features:
- Gradient from `#F0FF3D` to `#c8e600`
- Dark text (`#0a0a0f`)
- Shine overlay effect
- Glow on hover
- Lift effect (`translateY(-2px)`)

### Secondary Button (Glow Border)
Secondary actions with glowing border effect.

```tsx
<button className="px-6 py-3 btn-glow-border rounded-xl font-medium">
  Secondary
</button>
```

### Input Fields
Dark inputs with accent focus state.

```tsx
<input
  className="w-full px-4 py-3 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-[#F0FF3D]/40 focus:shadow-[0_0_0_3px_rgba(240,255,61,0.08)] transition-all duration-300"
  placeholder="Enter text..."
/>
```

### Input with Icon
```tsx
<div className="relative">
  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
    <Icon size={18} className="text-zinc-500" />
  </div>
  <input className="w-full pl-11 pr-4 py-3 ..." />
</div>
```

---

## Navigation

### Sidebar Nav Item
```tsx
<Link
  to="/path"
  className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
>
  <Icon size={22} />
</Link>
```

### Header Nav Pill
```tsx
<Link
  to="/path"
  className={`nav-pill ${isActive ? 'active' : ''}`}
>
  Label
</Link>
```

---

## Chat Elements

### User Message
```tsx
<div className="message-user px-4 py-3 rounded-2xl rounded-br-md">
  {content}
</div>
```

### Assistant Message
```tsx
<div className="message-assistant px-4 py-3 rounded-2xl rounded-bl-md">
  {content}
</div>
```

### Avatar Orb (Small)
Used for assistant avatar in chat.
```tsx
<div className="w-9 h-9 rounded-xl overflow-hidden relative">
  <div className="avatar-orb w-full h-full">
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="w-3 h-3 rounded-full bg-[#F0FF3D]/50 blur-sm" />
    </div>
  </div>
</div>
```

### Avatar Orb (Large)
Used for welcome screens and login.
```tsx
<div className="w-24 h-24 avatar-orb-large relative">
  <div className="smoke-particle smoke-particle-1" />
  <div className="smoke-particle smoke-particle-2" />
  <div className="smoke-particle smoke-particle-3" />
  <div className="avatar-inner-ring" />
  <div className="absolute inset-0 flex items-center justify-center">
    <div className="w-6 h-6 rounded-full bg-[#F0FF3D]/30 blur-md animate-pulse" />
  </div>
</div>
```

---

## Icons

Use **Lucide React** icons throughout the app.

```tsx
import { Icon } from 'lucide-react'
```

### Icon Sizes
- Navigation: `size={22}`
- Buttons: `size={18}`
- Inline: `size={14}` or `size={16}`
- Large decorative: `size={32}` or larger

### Icon Colors
- Default: `text-zinc-400` or `text-zinc-500`
- Active: `text-[#F0FF3D]`
- Success: `text-green-400`
- Error: `text-red-400`

---

## Spacing & Layout

### Border Radius
```
rounded-lg   - 8px  - Small elements
rounded-xl   - 12px - Inputs, buttons
rounded-2xl  - 16px - Cards, large containers
rounded-full - Pills, avatars
```

### Padding Scale
```
p-2   - 8px  - Tight
p-3   - 12px - Compact
p-4   - 16px - Standard
p-6   - 24px - Comfortable
p-8   - 32px - Spacious
```

### Gap Scale
```
gap-1   - 4px
gap-2   - 8px
gap-3   - 12px
gap-4   - 16px
gap-6   - 24px
```

---

## Animations

### Transitions
Standard transition for interactive elements:
```css
transition-all duration-200  /* Fast */
transition-all duration-300  /* Standard */
```

### Float Animation
For decorative elements:
```tsx
<div className="animate-float">...</div>
```

### Pulse
For attention-grabbing elements:
```tsx
<div className="animate-pulse">...</div>
```

### Loading Spinner
```tsx
import { Loader2 } from 'lucide-react'
<Loader2 className="animate-spin text-[#F0FF3D]" />
```

---

## States

### Disabled
```css
disabled:opacity-50 disabled:cursor-not-allowed
```

### Error
```tsx
<div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm">
  Error message
</div>
```

### Success
```tsx
<div className="p-3 bg-green-500/10 border border-green-500/20 text-green-400 rounded-xl text-sm">
  Success message
</div>
```

### Empty State
```tsx
<div className="text-center py-8">
  <Icon size={48} className="mx-auto text-zinc-600 mb-4" />
  <p className="text-zinc-400">No items found</p>
  <p className="text-zinc-600 text-sm mt-1">
    Helpful description text
  </p>
</div>
```

---

## Page Layout Pattern

```tsx
export default function PageName() {
  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Page Title</h1>
            <p className="text-zinc-500">Description text</p>
          </div>
          {/* Actions */}
        </div>

        {/* Content */}
        <div className="space-y-6">
          {/* Sections */}
        </div>
      </div>
    </div>
  )
}
```

---

## Dark Theme Notes

- **Never use pure white backgrounds** - Always use dark variants
- **Avoid harsh contrasts** - Use semi-transparent colors
- **Glow effects** - Use sparingly for emphasis
- **Text hierarchy** - Use zinc scale (zinc-300 to zinc-600)

---

## File Organization

```
frontend/src/
├── components/
│   ├── auth/           # Auth components (ProtectedRoute)
│   ├── chat/           # Chat components (MarkdownMessage, ToolIndicator)
│   └── layout/         # Layout components (Layout)
├── pages/              # Page components
├── services/           # API services
├── stores/             # Zustand stores
└── index.css           # Global styles & CSS variables
```

---

## Example: Creating a New Page

```tsx
import { useState, useEffect } from 'react'
import { Loader2, RefreshCw, SomeIcon } from 'lucide-react'

export default function NewFeature() {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load data...

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 size={32} className="animate-spin text-[#F0FF3D]" />
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Feature Name</h1>
            <p className="text-zinc-500">Feature description</p>
          </div>
          <button
            onClick={() => {/* refresh */}}
            className="p-2.5 rounded-xl hover:bg-[#F0FF3D]/5 transition-all duration-200 text-zinc-400 hover:text-[#F0FF3D]"
          >
            <RefreshCw size={20} />
          </button>
        </div>

        {/* Error state */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl">
            {error}
          </div>
        )}

        {/* Content cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="glass-card p-6">
            {/* Card content */}
          </div>
        </div>
      </div>
    </div>
  )
}
```
