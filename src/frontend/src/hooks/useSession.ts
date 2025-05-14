import { useEffect } from 'react';
import { getSessionToken, refreshSession } from '../utils/sessionManager';

export const useSession = () => {
  useEffect(() => {
    // Refresh session on mount
    refreshSession();

    // Set up activity listeners
    const handleActivity = () => {
      refreshSession();
    };

    // Listen for user activity
    window.addEventListener('mousemove', handleActivity);
    window.addEventListener('keydown', handleActivity);
    window.addEventListener('click', handleActivity);
    window.addEventListener('scroll', handleActivity);

    // Cleanup
    return () => {
      window.removeEventListener('mousemove', handleActivity);
      window.removeEventListener('keydown', handleActivity);
      window.removeEventListener('click', handleActivity);
      window.removeEventListener('scroll', handleActivity);
    };
  }, []);

  // Return the current session token
  return getSessionToken();
}; 