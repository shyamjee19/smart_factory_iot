import { useEffect, useRef, useState, useCallback } from 'react';
import { useStore } from '../store';
import type { SensorData } from '../types';

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseWebSocketReturn {
  status: ConnectionStatus;
  lastMessage: SensorData | null;
  reconnect: () => void;
}

export function useWebSocket(): UseWebSocketReturn {
  const token = useStore((s) => s.token);
  const updateLiveData = useStore((s) => s.updateLiveData);
  const addAlert = useStore((s) => s.addAlert);

  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<SensorData | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 10;

  const connect = useCallback(() => {
    if (!token) return;

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsHost = import.meta.env.VITE_WS_URL || `${protocol}://${window.location.host}/api/v1/ws/live`;
      const wsUrl = `${wsHost}?token=${token}`;

      if (wsRef.current) {
        wsRef.current.close();
      }

      setStatus('connecting');
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('connected');
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'sensor_data' && message.data) {
            const sensorData: SensorData = message.data;
            setLastMessage(sensorData);
            updateLiveData(message.device_id || sensorData.device_id, sensorData);
          } else if (message.type === 'alert' && message.data) {
            addAlert(message.data);
          }
        } catch {
          // Ignore malformed messages
        }
      };

      ws.onerror = () => {
        setStatus('error');
      };

      ws.onclose = () => {
        setStatus('disconnected');
        wsRef.current = null;

        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectTimerRef.current = setTimeout(() => {
            reconnectAttempts.current += 1;
            connect();
          }, delay);
        }
      };
    } catch {
      setStatus('error');
    }
  }, [token, updateLiveData, addAlert]);

  const reconnect = useCallback(() => {
    reconnectAttempts.current = 0;
    connect();
  }, [connect]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { status, lastMessage, reconnect };
}
