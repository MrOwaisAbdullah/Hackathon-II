"""
T114-T117: TaskEventStream - WebSocket Client with Auto-Reconnect

Handles WebSocket connection to the realtime-sync-service for live task updates.
Features:
- Auto-reconnect with exponential backoff
- JWT token authentication
- Event subscription and handlers
- Connection state management
"""

import { EventEmitter } from 'eventemitter3';

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface TaskEvent {
  type: string;
  data: any;
  timestamp: string;
}

export interface TaskEventStreamOptions {
  url: string;
  token: string;
  reconnectDelay?: number; // Initial delay in ms
  maxReconnectDelay?: number; // Max delay in ms
  pingInterval?: number; // Ping interval in ms
}

export class TaskEventStream extends EventEmitter {
  private ws: WebSocket | null = null;
  private url: string;
  private token: string;
  private reconnectDelay: number;
  private maxReconnectDelay: number;
  private pingInterval: number;
  private state: ConnectionState = 'disconnected';
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingTimer: NodeJS.Timeout | null = null;
  private manualClose: boolean = false;

  constructor(options: TaskEventStreamOptions) {
    super();
    this.url = options.url;
    this.token = options.token;
    this.reconnectDelay = options.reconnectDelay || 1000;
    this.maxReconnectDelay = options.maxReconnectDelay || 30000;
    this.pingInterval = options.pingInterval || 30000;
  }

  /**
   * T115: Connect to WebSocket with JWT token authentication
   */
  connect(): void {
    if (this.state === 'connected' || this.state === 'connecting') {
      return;
    }

    this.manualClose = false;
    this.setState('connecting');

    try {
      // Build WebSocket URL with token
      const wsUrl = `${this.url}?token=${encodeURIComponent(this.token)}`;

      this.ws = new WebSocket(wsUrl);

      // T115: Set up event handlers
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (error) {
      this.setState('error');
      this.scheduleReconnect();
    }
  }

  /**
   * T117: Disconnect and stop reconnection attempts
   */
  disconnect(): void {
    this.manualClose = true;
    this.clearReconnectTimer();
    this.clearPingTimer();

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.setState('disconnected');
  }

  private handleOpen(): void {
    this.setState('connected');
    this.clearReconnectTimer();

    // Start ping/pong
    this.startPing();

    this.emit('connected');
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);

      // Handle pong
      if (data.type === 'pong') {
        return;
      }

      // Emit task event
      this.emit('event', data as TaskEvent);

      // Emit specific event types
      if (data.type) {
        this.emit(data.type, data.data);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error);
    this.setState('error');
    this.emit('error', error);
  }

  private handleClose(event: CloseEvent): void {
    this.ws = null;
    this.clearPingTimer();

    if (!this.manualClose) {
      this.setState('disconnected');
      this.emit('disconnected', event);

      // T117: Schedule reconnection with exponential backoff
      this.scheduleReconnect();
    }
  }

  /**
   * T117: Schedule reconnection with exponential backoff
   */
  private scheduleReconnect(): void {
    if (this.manualClose) {
      return;
    }

    this.clearReconnectTimer();

    const delay = Math.min(this.reconnectDelay, this.maxReconnectDelay);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
      // Exponential backoff: double the delay for next attempt
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    }, delay);

    this.emit('reconnecting', delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private startPing(): void {
    this.clearPingTimer();

    this.pingTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, this.pingInterval);
  }

  private clearPingTimer(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  private setState(state: ConnectionState): void {
    if (this.state !== state) {
      const oldState = this.state;
      this.state = state;
      this.emit('stateChange', { oldState, newState: state });
    }
  }

  getState(): ConnectionState {
    return this.state;
  }

  isConnected(): boolean {
    return this.state === 'connected';
  }
}

// T118: Singleton instance management
let globalStream: TaskEventStream | null = null;

export function getTaskEventStream(options: TaskEventStreamOptions): TaskEventStream {
  if (!globalStream || globalStream.getState() === 'disconnected') {
    globalStream = new TaskEventStream(options);
  }
  return globalStream;
}

export function disconnectTaskEventStream(): void {
  if (globalStream) {
    globalStream.disconnect();
    globalStream = null;
  }
}
