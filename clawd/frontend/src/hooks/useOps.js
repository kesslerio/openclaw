import { useState, useEffect, useCallback } from "react";
import { fetchOps } from "../utils/api";

export function useOps(pollInterval = 60000) {
  const [ops, setOps] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadOps = useCallback(async () => {
    try {
      const data = await fetchOps();
      setOps(data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOps();
    const interval = setInterval(loadOps, pollInterval);
    return () => clearInterval(interval);
  }, [loadOps, pollInterval]);

  return { ops, loading, error, refresh: loadOps };
}
