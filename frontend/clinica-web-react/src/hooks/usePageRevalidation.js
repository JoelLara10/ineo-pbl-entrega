import { useEffect, useState } from 'react';

export function useDebouncedSearch(value, delay = 450) {
  const [query, setQuery] = useState(value.trim());
  useEffect(() => {
    const timer = setTimeout(() => setQuery(value.trim()), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return query;
}

export function usePageRevalidation(refresh) {
  useEffect(() => {
    const revalidate = () => { if (document.visibilityState !== 'hidden') refresh(); };
    window.addEventListener('focus', revalidate);
    document.addEventListener('visibilitychange', revalidate);
    return () => {
      window.removeEventListener('focus', revalidate);
      document.removeEventListener('visibilitychange', revalidate);
    };
  }, [refresh]);
}
