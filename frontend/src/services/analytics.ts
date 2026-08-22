import { apiClient } from "./api";

const SESSION_KEY = "portfolio_analytics_session";

function generateSessionId(): string {
  try {
    return crypto.randomUUID();
  } catch {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
    });
  }
}

function getOrCreateSessionId(): string {
  try {
    const stored = sessionStorage.getItem(SESSION_KEY);
    if (stored) return stored;
  } catch {
    // sessionStorage unavailable
  }

  const id = generateSessionId();

  try {
    sessionStorage.setItem(SESSION_KEY, id);
  } catch {
    // storage full or unavailable
  }

  return id;
}

export async function trackPageView(pathname: string): Promise<void> {
  try {
    await apiClient.post("/analytics/track/", {
      session_id: getOrCreateSessionId(),
      path: pathname,
    });
  } catch {
    if (import.meta.env.DEV) {
      console.debug("[analytics] page view not tracked:", pathname);
    }
  }
}
