# Next.js API Proxy Pattern for Kubernetes

## The Challenge

In Kubernetes deployments, the frontend and backend run as separate services. The browser can only access the frontend service (via NodePort, Ingress, or service tunnel), but needs to make API calls to the backend.

**The Problem:**
- Backend service is exposed only internally (ClusterIP)
- Browser cannot directly access internal K8s DNS
- CORS issues when making cross-origin requests
- Need to route API requests through frontend

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Frontend Service (ClusterIP:3000)                                  │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │  Next.js Application                                         │  │   │
│  │  │                                                              │  │   │
│  │  │  ├──> /pages/*          → React Components (SSR/CSR)        │  │   │
│  │  │  ├──> /api/[...path]    → API Route Proxy (catch-all)       │  │   │
│  │  │  │                                                              │  │   │
│  │  │  │  File: src/app/api/[...path]/route.ts                      │  │   │
│  │  │  │  Purpose: Forward browser requests to backend              │  │   │
│  │  │  │                                                              │  │   │
│  │  │  └──> Internal K8s DNS → backend.teamflow.svc.cluster.local   │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↕                                          │
│                          ┌──────────────────────────────────────┐           │
│                          │  Backend Service (ClusterIP:8000)    │           │
│                          │  FastAPI Application                 │           │
│                          └──────────────────────────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↕
                          ┌──────────────────────────────────────┐
                          │  Minikube Service Tunnel              │
                          │  http://127.0.0.1:46615               │
                          └──────────────────────────────────────┘
                                    ↕
                          ┌──────────────────────────────────────┐
                          │  Browser                              │
                          │  Makes requests to same origin        │
                          └──────────────────────────────────────┘
```

## Implementation

### 1. Next.js API Route Proxy

**File: `src/app/api/[...path]/route.ts`**

```typescript
import { NextRequest, NextResponse } from 'next/server';

// Internal K8s service URL (server-side environment variable)
const BACKEND_URL = process.env.BACKEND_URL ||
  'http://teamflow-backend.teamflow.svc.cluster.local:8000';

// Disable caching for API routes
export const dynamic = 'force-dynamic';

// Handle GET requests
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

// Handle POST requests
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

// Handle PUT requests
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

// Handle PATCH requests
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

// Handle DELETE requests
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

// Handle OPTIONS requests (CORS preflight)
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

/**
 * Proxies the request to the backend service
 */
async function proxyRequest(
  request: NextRequest,
  path: string[]
): Promise<NextResponse> {
  // Reconstruct the full path: /api/v1/auth/login
  const fullPath = '/api/' + path.join('/');
  const url = new URL(fullPath, BACKEND_URL);

  // Forward query parameters
  url.search = request.nextUrl.search;

  // Extract auth token from cookie or header
  const token = request.cookies.get('access_token')?.value ||
                request.headers.get('authorization')?.replace('Bearer ', '');

  // Prepare headers for backend request
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    // Forward request to backend service
    const response = await fetch(url.toString(), {
      method: request.method,
      headers,
      body: request.method !== 'GET' && request.method !== 'HEAD'
        ? await request.text()
        : undefined,
      // Important: Don't follow redirects automatically
      redirect: 'manual',
    });

    // Get response data
    const data = await response.text();

    // Return response with CORS headers
    return new NextResponse(data, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        // Forward specific headers from backend if needed
        ...(response.headers.get('Set-Cookie') && {
          'Set-Cookie': response.headers.get('Set-Cookie')!
        }),
      },
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Backend service unavailable' },
      { status: 503 }
    );
  }
}
```

### 2. Axios Configuration (Client-Side)

**File: `src/lib/api.ts`**

```typescript
import axios from 'axios';

/**
 * Axios instance configured for relative paths
 *
 * IMPORTANT: baseURL is empty string so requests use browser origin
 * - Browser makes request to: http://127.0.0.1:46615/api/v1/auth/login
 * - Next.js API route catches: /api/[...path]
 * - API route forwards to: http://backend.teamflow.svc.cluster.local:8000/api/v1/auth/login
 */
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '',  // Empty = relative paths
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // Important for cookies
});

// Request interceptor: Add auth token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor: Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        if (!window.location.pathname.startsWith('/login')) {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

### 3. Kubernetes Environment Variables

**File: `helm/teamflow/templates/frontend-deployment.yaml`**

```yaml
env:
  # CRITICAL: Empty string for relative paths
  # Browser uses current origin, no CORS issues
  - name: NEXT_PUBLIC_API_URL
    valueFrom:
      configMapKeyRef:
        name: teamflow-config
        key: NEXT_PUBLIC_API_URL

  # Internal K8s service URL for API route proxy (server-side only)
  - name: BACKEND_URL
    value: "http://teamflow-backend.teamflow.svc.cluster.local:8000"
```

**File: `helm/teamflow/values.yaml`**

```yaml
frontend:
  env:
    NEXT_PUBLIC_API_URL: ""  # Empty string, not omitted
    BACKEND_URL: "http://teamflow-backend.teamflow.svc.cluster.local:8000"
```

### 4. Backend CORS Configuration

**File: `backend/app/main.py` (FastAPI)**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TeamFlow API")

# Allow requests from frontend proxy
# Since proxy runs on same origin, this is mainly for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Add frontend service URL if needed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend URLs for JWT token validation (allowed origins)
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000,http://127.0.0.1:39315,http://192.168.49.2"
).split(",")
```

## Environment Variables Breakdown

| Variable | Scope | Purpose | Example Value |
|----------|-------|---------|---------------|
| `NEXT_PUBLIC_API_URL` | Client (browser) | Axios baseURL for API requests | `""` (empty) for relative paths |
| `BACKEND_URL` | Server (Next.js) | Internal K8s service URL for proxy | `http://teamflow-backend.teamflow.svc.cluster.local:8000` |
| `FRONTEND_URL` | Server (FastAPI) | Allowed origins for CORS | Comma-separated localhost URLs |

## Why Empty String for NEXT_PUBLIC_API_URL?

When `NEXT_PUBLIC_API_URL=""`:
- Axios makes requests to relative paths like `/api/v1/auth/login`
- Browser resolves relative path to current origin (e.g., `http://127.0.0.1:46615/api/v1/auth/login`)
- Next.js API route catches the request via `[...path]`
- API route forwards to backend via internal K8s DNS
- No CORS issues (same origin)

**Common Mistakes:**

| Mistake | Problem | Solution |
|---------|---------|----------|
| `NEXT_PUBLIC_API_URL="http://localhost:8000"` | Browser tries to reach localhost (doesn't work in K8s) | Use empty string `""` |
| `NEXT_PUBLIC_API_URL="http://backend:8000"` | Internal DNS not resolvable from browser | Use empty string, proxy on server |
| Using rewrites only | Doesn't work for client-side nav | Also implement API route proxy |
| Forgetting `dynamic = 'force-dynamic'` | API responses get cached | Add to route file |
| Missing CORS headers | Browser blocks responses | Add CORS headers to proxy |

## Testing the Setup

### Test API Proxy

```bash
# Test that frontend proxy works
curl -X POST "http://127.0.0.1:46615/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"password123"}'

# Should return JWT token (proxied to backend via Next.js)
```

### Test Backend Directly from Frontend Pod

```bash
# Exec into frontend pod
kubectl exec -it -n teamflow deployment/teamflow-frontend -- sh

# Test internal K8s DNS
curl http://teamflow-backend.teamflow.svc.cluster.local:8000/health

# Should return: {"status": "healthy"}
```

### Test Service Connectivity

```bash
# Check services
kubectl get svc -n teamflow

# Check endpoints
kubectl get endpoints -n teamflow

# Test DNS from a pod
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -n teamflow -- \
  curl http://teamflow-backend.teamflow.svc.cluster.local:8000/health
```

## Production Considerations

### 1. Ingress Configuration

```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: teamflow.local
      paths:
        - path: /          # Frontend
          service: teamflow-frontend
          port: 3000
        - path: /api       # API proxy
          service: teamflow-frontend
          port: 3000
        - path: /v1        # Optional: Rewrites
          service: teamflow-frontend
          port: 3000
```

### 2. Backend NOT Exposed Externally

- Backend service remains `ClusterIP` only
- No NodePort or Ingress for backend
- All traffic goes through frontend proxy

### 3. Security

- Rate limiting at frontend
- Auth token validation
- CORS headers configured correctly
- TLS termination at ingress

### 4. Alternative: Using Next.js Rewrites

**File: `next.config.ts`**

```typescript
async rewrites() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";
  return [
    {
      source: "/v1/:path*",
      destination: `${apiUrl}/api/v1/:path*`,
    },
  ];
},
```

**Note:** Rewrites work for server-side rendering but the API route proxy is needed for client-side requests.

## Troubleshooting

### Issue: "Network Error" in Browser

**Check:**
1. Is the frontend pod running?
2. Is the backend service reachable from frontend pod?
3. Are the environment variables set correctly?

```bash
# Check pod status
kubectl get pods -n teamflow

# Check frontend logs
kubectl logs -f deployment/teamflow-frontend -n teamflow

# Check backend service from frontend
kubectl exec -n teamflow deployment/teamflow-frontend -- \
  curl http://teamflow-backend.teamflow.svc.cluster.local:8000/health
```

### Issue: CORS Errors

**Check:**
1. Are CORS headers added in the API route?
2. Is the backend allowing requests from frontend?
3. Are you making requests to relative paths (not absolute)?

### Issue: 503 Backend Unavailable

**Check:**
1. Is the `BACKEND_URL` environment variable correct?
2. Is the backend service running?
3. Can the frontend pod resolve the backend DNS?

```bash
# Check backend URL in frontend pod
kubectl exec -n teamflow deployment/teamflow-frontend -- \
  env | grep BACKEND_URL

# Test DNS resolution
kubectl exec -n teamflow deployment/teamflow-frontend -- \
  nslookup teamflow-backend.teamflow.svc.cluster.local
```

## References

- [Next.js Route Handlers](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
- [Next.js Dynamic Routes](https://nextjs.org/docs/app/building-your-application/routing/dynamic-routes)
- [Kubernetes Service Discovery](https://kubernetes.io/docs/concepts/services-networking/service/#discovering-services)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)
