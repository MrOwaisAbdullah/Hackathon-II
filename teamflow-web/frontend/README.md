# TeamFlow Frontend

Next.js 16 frontend for TeamFlow Phase 2 - Full-Stack Agency CRM.

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript 5.7+
- **Styling**: Tailwind CSS
- **Animation**: Motion.dev (Framer Motion 11)
- **Drag & Drop**: dnd-kit 6
- **Auth**: Better Auth React
- **State**: Zustand
- **Testing**: Playwright

## Setup

### Prerequisites

- Node.js 20+ (LTS)
- npm or yarn

### Installation

```bash
# Install dependencies
npm install
# or
yarn install

# Copy environment file
cp ../.env.example .env.local

# Start development server
npm run dev
```

Visit http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/
│   │   ├── board/        # Task board components
│   │   ├── task/         # Task-related components
│   │   ├── dashboard/    # Dashboard components
│   │   ├── auth/         # Authentication components
│   │   ├── ui/           # Reusable UI components
│   │   └── common/       # Shared components
│   ├── lib/              # Utility functions
│   ├── hooks/            # Custom React hooks
│   ├── types/            # TypeScript types
│   └── config/           # App configuration
├── public/               # Static assets
└── e2e/                  # Playwright E2E tests
```

## Key Features

### Task Board (US2)
- Drag-and-drop with dnd-kit
- Kanban columns (Todo, In Progress, Done)
- Task cards with priority indicators
- Smooth animations with Motion

### Authentication (US1)
- Better Auth integration
- JWT-based auth with backend
- Agency-scoped sessions
- Protected routes

### Dashboard (US4)
- Agency-level statistics
- Project overview grid
- Real-time updates (10s polling)
- Manual refresh capability

## Testing

```bash
# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run in headed mode
npx playwright test --headed
```

## Development

### Code Quality

```bash
# Lint code
npm run lint

# Type check
npx tsc --noEmit

# Build for production
npm run build
```

### Component Development

Components follow these patterns:
- Server Components by default
- Client Components with "use client" directive
- Motion animations for transitions
- Type-safe props with TypeScript

## Animation Guidelines

- Use `motion` from `motion/react`
- `AnimatePresence` for enter/exit animations
- Layout animations for smooth reordering
- Drag animations with dnd-kit modifiers

## State Management

- Zustand for client state
- Server Components for data fetching
- React Server Actions for mutations

## Styling

- Tailwind CSS utility classes
- Custom components in `src/components/ui/`
- Responsive design (mobile-first)
- Dark mode support planned
