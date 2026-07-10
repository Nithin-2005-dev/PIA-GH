import { useEffect } from 'react';
import { create } from 'zustand';

export interface TelemetryEvent {
  event_type: string;
  session_id: string;
  query_id?: string;
  timestamp: string;
  [key: string]: any;
}

interface TelemetryState {
  events: TelemetryEvent[];
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
  addEvent: (event: TelemetryEvent) => void;
  setConnectionStatus: (status: 'connecting' | 'connected' | 'disconnected') => void;
  clearEvents: () => void;
}

export const useTelemetryStore = create<TelemetryState>((set) => ({
  events: [],
  connectionStatus: 'disconnected',
  addEvent: (event) => set((state) => ({ events: [...state.events, event] })),
  setConnectionStatus: (status) => set({ connectionStatus: status }),
  clearEvents: () => set({ events: [] })
}));

export function useLiveTelemetry() {
  const { addEvent, setConnectionStatus } = useTelemetryStore();

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/v1/runtime');
    
    setConnectionStatus('connecting');

    ws.onopen = () => {
      setConnectionStatus('connected');
    };

    ws.onmessage = (message) => {
      try {
        const data = JSON.parse(message.data) as TelemetryEvent;
        addEvent(data);
      } catch (e) {
        console.error("Failed to parse telemetry event", e);
      }
    };

    ws.onclose = () => {
      setConnectionStatus('disconnected');
    };

    return () => {
      ws.close();
    };
  }, []);
}
