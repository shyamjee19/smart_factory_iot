import type { StateCreator } from 'zustand';
import type { Device, Alert, SensorData } from '../types';

export interface DeviceSlice {
  devices: Device[];
  selectedDevice: Device | null;
  alerts: Alert[];
  liveData: Record<string, SensorData>;
  setDevices: (devices: Device[]) => void;
  setSelectedDevice: (device: Device | null) => void;
  setAlerts: (alerts: Alert[]) => void;
  addAlert: (alert: Alert) => void;
  updateAlert: (id: number, updates: Partial<Alert>) => void;
  updateLiveData: (deviceId: string, data: SensorData) => void;
  updateDeviceStatus: (deviceId: string, status: string) => void;
}

export const createDeviceSlice: StateCreator<DeviceSlice> = (set) => ({
  devices: [],
  selectedDevice: null,
  alerts: [],
  liveData: {},
  setDevices: (devices: Device[]) => set({ devices }),
  setSelectedDevice: (selectedDevice: Device | null) => set({ selectedDevice }),
  setAlerts: (alerts: Alert[]) => set({ alerts }),
  addAlert: (alert: Alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts].slice(0, 100),
    })),
  updateAlert: (id: number, updates: Partial<Alert>) =>
    set((state) => ({
      alerts: state.alerts.map((a) => (a.id === id ? { ...a, ...updates } : a)),
    })),
  updateLiveData: (deviceId: string, data: SensorData) =>
    set((state) => ({
      liveData: { ...state.liveData, [deviceId]: data },
    })),
  updateDeviceStatus: (deviceId: string, status: string) =>
    set((state) => ({
      devices: state.devices.map((d) =>
        d.device_id === deviceId ? { ...d, status } : d
      ),
    })),
});
