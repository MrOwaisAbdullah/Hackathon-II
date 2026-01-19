# TeamFlow Frontend

Next.js 16 application with animation-first design, AI chatbot integration, and modern agency management features.

---

## Overview

TeamFlow Frontend is a production-ready Next.js 16 application built for creative agencies to manage tasks, projects, time tracking, and team collaboration. It features a responsive design, smooth animations, and an AI-powered chatbot with voice input support.

**Key Differentiators:**
- Not a basic todo app - a full agency management system
- Multi-tenant architecture with agency isolation
- Animation-first design with Motion.dev
- AI chatbot with 21+ MCP tools and voice input
- Real-time analytics dashboard

---

## Tech Stack

```yaml
Framework: Next.js 16 (App Router, Turbopack)
Language: TypeScript 5.7+
Styling: Tailwind CSS
Animations: Motion.dev (Framer Motion 11)
State Management: Zustand, React Query
Drag & Drop: @dnd-kit (physics-based)
Auth: Better Auth React
AI: OpenAI ChatKit React
Testing: Playwright (E2E)
```

---

## Key Features

### Task Board (Kanban)
- Drag-and-drop with dnd-kit physics engine
- Four columns: To Do, In Progress, In Review, Done
- Task filtering by assignee and priority
- Mobile-friendly "Move to" menu
- Celebration animations on completion

### Analytics Dashboard
- Real-time statistics with animated charts
- Project progress tracking
- Upcoming deadlines view
- Team workload distribution
- 10-second auto-refresh with manual refresh

### AI Chatbot
- Floating chat widget with streaming responses
- Voice input via Web Speech API
- Fullscreen mode at `/chat`
- 21+ MCP tools for task/project management
- Multi-language support (English + Urdu)
- NDJSON streaming for real-time updates

### Project Management
- Create and manage multiple projects
- Status tracking (Active, On Hold, Completed, Archived)
- Team assignment and workload balancing
- Time tracking with billable hours

### Additional Features
- Responsive design (mobile, tablet, desktop)
- Dark/light theme support
- Marketing pages (pricing, privacy, terms)
- Protected routes with authentication

---

## Project Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (main)/                   # Dashboard pages (protected)
│   │   │   ├── dashboard/            # Analytics dashboard
│   │   │   ├── projects/             # Project management
│   │   │   ├── tasks/                # Task board
│   │   │   └── layout.tsx            # Dashboard layout
│   │   ├── (marketing)/              # Public pages
│   │   │   ├── page.tsx              # Landing page
│   │   │   ├── pricing/              # Pricing page
│   │   │   ├── privacy/              # Privacy policy
│   │   │   └── terms/                # Terms of service
│   │   ├── chat/                     # AI chatbot page
│   │   ├── login/                    # Authentication
│   │   ├── layout.tsx                # Root layout
│   │   └── globals.css               # Global styles
│   │
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── dashboard/                # Dashboard widgets
│   │   │   ├── stats-card.tsx
│   │   │   ├── projects-grid.tsx
│   │   │   └── deadlines-list.tsx
│   │   ├── board/                    # Kanban board
│   │   │   ├── task-board.tsx
│   │   │   ├── task-column.tsx
│   │   │   └── task-card.tsx
│   │   ├── chat/                     # ChatKit integration
│   │   │   ├── chat-widget.tsx       # Floating widget
│   │   │   ├── chat-fullscreen.tsx   # Fullscreen chat
│   │   │   └── voice-input.tsx       # Voice input
│   │   └── layout/                   # Layout components
│   │       ├── header.tsx
│   │       ├── sidebar.tsx
│   │       └── footer.tsx
│   │
│   ├── lib/
│   │   ├── api-client.ts             # API client (fetch)
│   │   ├── auth.ts                   # Auth utilities
│   │   └── utils.ts                  # Helper functions
│   │
│   ├── hooks/
│   │   ├── use-auth.ts               # Auth hook
│   │   ├── use-tasks.ts              # Tasks hook
│   │   └── use-projects.ts           # Projects hook
│   │
│   └── types/
│       ├── task.ts                   # Task types
│       ├── project.ts                # Project types
│       └── user.ts                   # User types
│
├── public/                           # Static assets
├── e2e/                              # Playwright E2E tests
├── package.json
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

---

## Development Setup

### Prerequisites

- Node.js 20+ (LTS)
- npm or pnpm

### Installation

```bash
# Navigate to frontend directory
cd teamflow-web/frontend

# Install dependencies
npm install
# or: pnpm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local with your configuration
# - NEXT_PUBLIC_API_URL: Backend API URL
# - NEXT_PUBLIC_CHATKIT_DOMAIN_KEY: OpenAI domain key
```

### Environment Variables

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit Domain Key (register in OpenAI dashboard)
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-registered-domain

# Optional: Override API URLs
NEXT_PUBLIC_AUTH_URL=http://localhost:8000/api/v1
```

### Run Development Server

```bash
npm run dev
```

Visit http://localhost:3000

### Build for Production

```bash
npm run build
npm start
```

---

## Key Components

### ChatWidget

Floating AI assistant with streaming responses:

```typescript
// Features:
- NDJSON streaming for real-time updates
- Voice input via Web Speech API
- Fullscreen mode toggle
- Multi-language (English + Urdu)
- Auto-scroll to latest message
- Loading states and error handling
```

**Location:** `src/components/chat/chat-widget.tsx`

### TaskBoard

Kanban board with drag-and-drop:

```typescript
// Features:
- dnd-kit physics-based drag
- Four columns: To Do, In Progress, In Review, Done
- Task filtering by assignee
- Mobile "Move to" menu
- Celebration animations (confetti)
- Real-time updates
```

**Location:** `src/components/board/task-board.tsx`

### Dashboard

Analytics dashboard with real-time stats:

```typescript
// Features:
- Animated stat cards
- Project grid with progress
- Upcoming deadlines
- Team workload chart
- 10s auto-refresh
- Manual refresh button
```

**Location:** `src/app/(main)/dashboard/page.tsx`

---

## Performance Optimizations

### React Optimization
- `React.memo` for component memoization
- `useCallback` for event handlers
- `useMemo` for expensive computations
- Code splitting with dynamic imports

### Animation Performance
- GPU acceleration with `transform` and `opacity`
- 60fps target for all animations
- `AnimatePresence` for enter/exit animations
- Layout animations for smooth reordering

### Image Optimization
- Next.js `Image` component for automatic optimization
- WebP format support
- Lazy loading for below-fold images
- Responsive images with `srcset`

### Bundle Size
- Tree-shaking for unused code
- Dynamic imports for heavy components
- Package size monitoring
- Route-based code splitting

---

## Animation Guidelines

### Using Motion.dev

```typescript
import { motion } from 'motion/react'

// Basic animation
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>

// Enter/exit animations
<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.2 }}
    >
  )}
</AnimatePresence>

// Drag animations
import { useDragControls } from 'framer-motion'
const controls = useDragControls()
```

### Best Practices
- Use `transform` instead of `left/top` for better performance
- Animate `opacity` and `transform` for GPU acceleration
- Keep animations under 300ms for UI feedback
- Use `layout` prop for list reordering

---

## State Management

### Zustand (Client State)

```typescript
// Example store
import { create } from 'zustand'

const useTaskStore = create<TaskStore>((set) => ({
  tasks: [],
  addTask: (task) => set((state) => ({
    tasks: [...state.tasks, task]
  })),
}))
```

### Server State (React Query)

```typescript
// Fetching data
const { data: tasks, isLoading } = useQuery({
  queryKey: ['tasks'],
  queryFn: () => fetch('/api/v1/tasks').then(r => r.json())
})
```

---

## Testing

### E2E Tests (Playwright)

```bash
# Run E2E tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui

# Run in headed mode
npx playwright test --headed

# Run specific test
npx playwright test test:task-board
```

### Example Test

```typescript
test('can create a new task', async ({ page }) => {
  await page.goto('/tasks')
  await page.click('[data-testid="create-task-button"]')
  await page.fill('[data-testid="task-title-input"]', 'New Task')
  await page.click('[data-testid="save-task-button"]')
  await expect(page.locator('text=New Task')).toBeVisible()
})
```

---

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Configure root directory: `teamflow-web/frontend`
3. Add environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY`
4. Deploy automatically on push to `main`

### Environment Variables (Production)

```env
# Production API URL
NEXT_PUBLIC_API_URL=https://your-backend.hf.space

# Production domain key
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-production-domain
```

### Build Configuration

```typescript
// next.config.ts
export default {
  output: 'standalone',
  images: {
    domains: ['your-backend.hf.space'],
  },
  // Turbopack for faster builds
  experimental: {
    turbo: {},
  },
}
```

---

## Troubleshooting

### ChatKit IntegrationError

**Error:** `IntegrationError: Domain not registered`

**Solution:**
1. Go to [OpenAI Dashboard](https://platform.openai.com)
2. Navigate to ChatKit → Domains
3. Register your domain (e.g., `localhost:3000` or `vercel.app`)
4. Copy the domain key to `.env.local`

### TypeScript Build Errors

**Error:** Type errors in components

**Solution:**
```bash
# Type check without building
npx tsc --noEmit

# Fix specific issues
npm run lint -- --fix
```

### Animation Performance

**Issue:** Animations are laggy

**Solution:**
- Use `transform` and `opacity` only
- Enable GPU acceleration with `will-change`
- Reduce animation complexity
- Use React DevTools Profiler to identify bottlenecks

### Hydration Mismatch

**Error:** Text content does not match server-rendered HTML

**Solution:**
- Ensure date formatting is consistent
- Use `suppressHydrationWarning` for timestamps
- Check for `typeof window` usage

---

## Development Workflow

### Creating a New Component

```bash
# Using shadcn/ui
npx shadcn-ui@latest add card

# Manual component
# Create in src/components/
# Add exports if needed
```

### Adding a New Page

```typescript
// Create in src/app/(main)/new-page/page.tsx
export default function NewPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Content */}
    </motion.div>
  )
}
```

### Type-Safe API Calls

```typescript
// src/lib/api-client.ts
export async function fetchTasks() {
  const response = await fetch(`${API_URL}/api/v1/tasks`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  })
  if (!response.ok) throw new Error('Failed to fetch')
  return response.json() as Promise<Task[]>
}
```

---

## Code Quality

### Linting

```bash
# Run ESLint
npm run lint

# Fix issues
npm run lint -- --fix
```

### Type Checking

```bash
# Type check
npx tsc --noEmit
```

### Formatting

```bash
# Format with Prettier
npm run format
```

---

## Related Documentation

- [Root README](../../README.md) - Overall project overview
- [Backend README](../backend/README.md) - Backend API documentation
- [Phase 2 Spec](../../specs/002-fullstack-web-crm/) - Feature specifications
- [Phase 3 Spec](../../specs/001-ai-chatbot/) - AI chatbot specifications

---

## License

MIT © 2025 Owais Abdullah

---

**Built with Next.js 16, Motion.dev, and modern web technologies**
