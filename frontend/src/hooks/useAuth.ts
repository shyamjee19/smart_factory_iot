import { useCallback } from 'react';
import { useStore } from '../store';
import { login as apiLogin, register as apiRegister, getCurrentUser } from '../api/endpoints';

export function useAuth() {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    setAuth,
    clearAuth,
    setLoading,
    setError,
  } = useStore();

  const login = useCallback(
    async (username: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiLogin(username, password);
        const userData = await getCurrentUser();
        setAuth(userData, response.access_token);
        return true;
      } catch (err: unknown) {
        const message =
          (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          'Login failed. Please check your credentials.';
        setError(message);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [setAuth, setLoading, setError]
  );

  const register = useCallback(
    async (username: string, email: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        await apiRegister(username, email, password);
        return true;
      } catch (err: unknown) {
        const message =
          (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          'Registration failed.';
        setError(message);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [setLoading, setError]
  );

  const logout = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    setError,
  };
}
