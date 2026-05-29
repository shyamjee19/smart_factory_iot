import { useEffect, useCallback, useRef } from 'react';
import { useStore } from '../store';
import { getDevices } from '../api/endpoints';

export function useDevices(pollInterval: number = 30000) {
  const { devices, setDevices, isAuthenticated } = useStore();
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const fetchDevices = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const data = await getDevices();
      setDevices(data);
    } catch {
      // silently fail for polling
    }
  }, [isAuthenticated, setDevices]);

  useEffect(() => {
    fetchDevices();

    if (pollInterval > 0) {
      intervalRef.current = setInterval(fetchDevices, pollInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchDevices, pollInterval]);

  return { devices, refetch: fetchDevices };
}
