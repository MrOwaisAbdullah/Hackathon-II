/**
 * T118: useTaskEvents Hook
 *
 * React hook for subscribing to WebSocket task events.
 * Manages WebSocket lifecycle and event handlers.
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { TaskEventStream, TaskEvent, ConnectionState } from '@/services/websocket';

export interface UseTaskEventsOptions {
  url: string;
  token: string;
  enabled?: boolean;
}

export function useTaskEvents(options: UseTaskEventsOptions) {
  const { url, token, enabled = true } = options;
  const streamRef = useRef<TaskEventStream | null>(null);
  const [state, setState] = useState<ConnectionState>('disconnected');
  const [reconnectingIn, setReconnectingIn] = useState<number | null>(null);
  const [events, setEvents] = useState<TaskEvent[]>([]);

  // Connect to WebSocket
  useEffect(() => {
    if (!enabled || !token) {
      return;
    }

    const stream = new TaskEventStream({
      url,
      token,
      reconnectDelay: 1000,
      maxReconnectDelay: 30000,
    });

    streamRef.current = stream;

    // Set up event listeners
    const handleConnected = () => {
      setState('connected');
      setReconnectingIn(null);
    };

    const handleDisconnected = () => {
      setState('disconnected');
    };

    const handleError = (error: Event) => {
      setState('error');
    };

    const handleStateChange = ({ newState }: { oldState: ConnectionState; newState: ConnectionState }) => {
      setState(newState);
    };

    const handleReconnecting = (delay: number) => {
      setReconnectingIn(delay);
    };

    const handleEvent = (event: TaskEvent) => {
      setEvents((prev) => [...prev.slice(-99), event]); // Keep last 100 events
    };

    // Listen to specific task events
    const handleTaskCreated = (data: any) => {
      console.log('Task created:', data);
    };

    const handleTaskUpdated = (data: any) => {
      console.log('Task updated:', data);
    };

    const handleTaskCompleted = (data: any) => {
      console.log('Task completed:', data);
    };

    // Register listeners
    stream.on('connected', handleConnected);
    stream.on('disconnected', handleDisconnected);
    stream.on('error', handleError);
    stream.on('stateChange', handleStateChange);
    stream.on('reconnecting', handleReconnecting);
    stream.on('event', handleEvent);
    stream.on('task_created', handleTaskCreated);
    stream.on('task_updated', handleTaskUpdated);
    stream.on('task_completed', handleTaskCompleted);

    // Connect
    stream.connect();

    // Cleanup
    return () => {
      stream.disconnect();
      streamRef.current = null;
    };
  }, [url, token, enabled]);

  return {
    state,
    isConnected: state === 'connected',
    isConnecting: state === 'connecting',
    isError: state === 'error',
    reconnectingIn,
    events,
  };
}
