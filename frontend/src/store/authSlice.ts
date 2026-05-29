import type { StateCreator } from 'zustand';
import type { User } from '../types';

export interface AuthSlice {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const createAuthSlice: StateCreator<AuthSlice> = (set) => {
  const storedToken = localStorage.getItem('token');
  const storedUser = localStorage.getItem('user');
  let parsedUser: User | null = null;
  try {
    parsedUser = storedUser ? JSON.parse(storedUser) : null;
  } catch {
    parsedUser = null;
  }

  return {
    user: parsedUser,
    token: storedToken,
    isAuthenticated: !!storedToken && !!parsedUser,
    isLoading: false,
    error: null,
    setAuth: (user: User, token: string) => {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      set({ user, token, isAuthenticated: true, error: null });
    },
    clearAuth: () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      set({ user: null, token: null, isAuthenticated: false, error: null });
    },
    setLoading: (isLoading: boolean) => set({ isLoading }),
    setError: (error: string | null) => set({ error }),
  };
};
