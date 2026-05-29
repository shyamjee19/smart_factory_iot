import { create } from 'zustand';
import { createAuthSlice, type AuthSlice } from './authSlice';
import { createDeviceSlice, type DeviceSlice } from './deviceSlice';

type StoreState = AuthSlice & DeviceSlice;

export const useStore = create<StoreState>()((...a) => ({
  ...createAuthSlice(...a),
  ...createDeviceSlice(...a),
}));

export type { AuthSlice, DeviceSlice };
