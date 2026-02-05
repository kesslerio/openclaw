import { useState, useEffect, useCallback } from "react";
import { fetchStatus } from "../utils/api";

export function useStatus(pollInterval = 30000) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadStatus = useCallback(async () => {
    try {
      const data = await fetchStatus();
      setStatus(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStatus();

    // Poll every 30 seconds
    const interval = setInterval(loadStatus, pollInterval);

    return () => clearInterval(interval);
  }, [loadStatus, pollInterval]);

  return {
    status,
    loading,
    error,
    lastUpdated,
    refresh: loadStatus,
  };
}
