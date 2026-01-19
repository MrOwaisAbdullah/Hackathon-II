/**
 * API proxy route for backend requests.
 *
 * This route proxies requests to the FastAPI backend, handling CORS
 * and adding proper authentication headers from client-side stored tokens.
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://teamflow-backend.teamflow.svc.cluster.local:8000';

export const dynamic = 'force-dynamic';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

async function proxyRequest(
  request: NextRequest,
  path: string[]
): Promise<NextResponse> {
  try {
    // Prepend /api to path since the catch-all route strips it
    // Browser calls /api/v1/auth/login, path gets ['v1', 'auth', 'login']
    // Backend expects /api/v1/auth/login
    const fullPath = '/api/' + path.join('/');
    const url = new URL(fullPath, BACKEND_URL);
    url.search = request.nextUrl.search;

    // Get auth token from cookie or header
    const token =
      request.cookies.get('access_token')?.value ||
      request.headers.get('authorization')?.replace('Bearer ', '');

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Prepare request options
    const options: RequestInit = {
      method: request.method,
      headers,
    };

    // Forward body for non-GET requests
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      options.body = await request.text();
    }

    // Make request to backend
    const response = await fetch(url.toString(), options);

    // Create response with proxied data
    const data = await response.text();
    const nextResponse = new NextResponse(data, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
      },
    });

    // Forward CORS headers if needed
    nextResponse.headers.set('Access-Control-Allow-Origin', '*');
    nextResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
    nextResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    return nextResponse;
  } catch (error) {
    console.error('API proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error', detail: 'Failed to proxy request to backend' },
      { status: 500 }
    );
  }
}

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
