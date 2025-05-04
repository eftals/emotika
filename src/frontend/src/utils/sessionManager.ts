import { v4 as uuidv4 } from 'uuid';

const SESSION_KEY = 'emotika_session';
const SESSION_EXPIRY = 30 * 60 * 1000; // 30 minutes in milliseconds

interface Session {
  token: string;
  lastActivity: number;
}

export const getSession = (): Session | null => {
  const sessionStr = localStorage.getItem(SESSION_KEY);
  if (!sessionStr) return null;

  const session: Session = JSON.parse(sessionStr);
  const now = Date.now();

  // Check if session has expired
  if (now - session.lastActivity > SESSION_EXPIRY) {
    localStorage.removeItem(SESSION_KEY);
    return null;
  }

  return session;
};

export const createSession = (): Session => {
  const session: Session = {
    token: uuidv4(),
    lastActivity: Date.now(),
  };
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
};

export const refreshSession = (): Session => {
  const session = getSession();
  if (!session) return createSession();

  session.lastActivity = Date.now();
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
};

export const clearSession = (): void => {
  localStorage.removeItem(SESSION_KEY);
};

// Function to get the current session token, creating a new one if needed
export const getSessionToken = (): string => {
  const session = getSession() || createSession();
  return session.token;
}; 