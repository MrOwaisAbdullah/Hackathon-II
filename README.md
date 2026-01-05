# TeamFlow CRM

[![CI/CD](https://github.com/MrOwaisAbdullah/Teamflow/actions/workflows/deploy.yml/badge.svg)](https://github.com/MrOwaisAbdullah/Teamflow/actions/workflows/deploy.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MrOwaisAbdullah/Teamflow/blob/main/LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)

A modern, fullstack CRM web application for small agencies to manage tasks, projects, time tracking, and team collaboration.

## Features

### Project Management
- Create and manage multiple projects
- Track project status (Active, On Hold, Completed, Archived)
- Organize tasks by project

### Task Board (Kanban)
- Drag-and-drop task management
- Four columns: To Do, In Progress, In Review, Done
- Task filtering by assignee and status
- Priority badges (High, Medium, Low)
- Due date tracking with overdue indicators
- Mobile-friendly "Move to" menu for non-drag changes

### Team Management
- User management with roles (Admin, Member, Viewer)
- Project Manager designation
- Task assignment with workload tracking

### Time Tracking
- Log time spent on tasks
- Time entries with descriptions
- Filter time entries by task and date

### Analytics Dashboard
- Task distribution charts
- Upcoming deadlines view
- Project progress tracking
- Team performance metrics

### Additional Features
- Responsive design (mobile, tablet, desktop)
- Dark mode support
- Real-time updates
- Task archiving
- Rich task descriptions with Markdown support

## Tech Stack

### Frontend
- **Framework**: Next.js 16 (App Router, Turbopack)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Animations**: Framer Motion
- **State Management**: TanStack Query (React Query)
- **Drag & Drop**: @dnd-kit
- **Forms**: React Hook Form + Zod

### Backend
- **Framework**: FastAPI (Python 3.13+)
- **Database**: PostgreSQL (Neon)
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT tokens
- **API Documentation**: OpenAPI/Swagger

### Deployment
- **Frontend**: Vercel
- **Backend**: HuggingFace Spaces
- **CI/CD**: GitHub Actions
- **Database**: Neon PostgreSQL (free tier)

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.13+
- PostgreSQL database (or use Neon free tier)

### 1. Clone the Repository

```bash
git clone https://github.com/MrOwaisAbdullah/Teamflow.git
cd Teamflow
git checkout 002-fullstack-web-crm
```

### 2. Backend Setup

```bash
cd teamflow-web/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000
API Docs at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd teamflow-web/frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/teamflow
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
teamflow-web/
├── frontend/                    # Next.js 16 application
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   ├── components/         # React components
│   │   ├── lib/                # Utilities and API clients
│   │   └── types/              # TypeScript types
│   ├── public/                 # Static assets
│   └── package.json
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/                # API routes
│   │   ├── core/               # Configuration and security
│   │   ├── models/             # Database models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── main.py             # Application entry point
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Backend tests
│   ├── Dockerfile              # HuggingFace deployment
│   └── pyproject.toml
│
├── .github/workflows/           # CI/CD workflows
│   └── deploy.yml              # Automated deployment
│
├── scripts/                     # Utility scripts
│   ├── deploy.sh               # Deployment helpers
│   └── verify-deployment.sh    # Deployment verification
│
├── DEPLOYMENT_SUMMARY.md        # Quick deployment guide
└── DEPLOYMENT.md                # Detailed deployment documentation
```

## Deployment

For production deployment to Vercel (frontend) and HuggingFace Spaces (backend), see:

- **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** - 30-minute quick start guide
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Comprehensive deployment documentation

### Quick Deploy Summary

1. Create Neon PostgreSQL database
2. Create HuggingFace Space (Docker SDK)
3. Deploy frontend to Vercel
4. Configure GitHub Actions for automated deployments
5. Push code → automatic deployment! 🚀

## Development

### Running Tests

**Backend:**
```bash
cd teamflow-web/backend
pytest
```

**Frontend:**
```bash
cd teamflow-web/frontend
npm test
```

### Building for Production

**Frontend:**
```bash
cd teamflow-web/frontend
npm run build
```

**Backend:**
```bash
cd teamflow-web/backend
# Build Docker image
docker build -t teamflow-backend .
```

## Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)
*Overview of tasks, projects, and team performance*

### Task Board
![Task Board](docs/screenshots/taskboard.png)
*Kanban-style task management with drag-and-drop*

### Projects
![Projects](docs/screenshots/projects.png)
*Project management and organization*

## API Documentation

When running the backend locally, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT © 2025 Owais Abdullah

---

**Built with ❤️ using Next.js 16, FastAPI, and modern web technologies**
