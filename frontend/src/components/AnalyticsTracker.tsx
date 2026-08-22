import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { trackPageView } from "../services/analytics";

export function AnalyticsTracker() {
  const { pathname } = useLocation();
  const lastTracked = useRef(pathname);

  useEffect(() => {
    if (pathname === lastTracked.current) return;
    lastTracked.current = pathname;
    void trackPageView(pathname);
  }, [pathname]);

  useEffect(() => {
    void trackPageView(pathname);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return null;
}
