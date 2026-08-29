import { useState, useEffect, useCallback } from 'react';

/**
 * Generic data-fetching hook shared by every dashboard/list page.
 * Centralizes the loading/error/data/refetch pattern so individual
 * pages stay focused on presentation, not fetch plumbing.
 *
 * fetchFn must be a stable callback (wrap in useCallback at the call
 * site) - it re-runs whenever deps change.
 */
export function useApiData(fetchFn, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
    } catch (err) {
      setError(err.apiMessage || 'Failed to load data.');
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, refetch: load };
}
