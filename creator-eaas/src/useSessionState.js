import { useEffect, useState } from 'react';

// Like useState, but the value also lives in this browser tab's
// sessionStorage, so a page refresh keeps you where you were. Closing the
// tab clears it.
//
// This is a convenience, not security: anyone can edit sessionStorage.
// Real sign-in sessions are tracked in issue #17.
//
// Storage can be unavailable (private browsing, blocked site data), so
// every access is wrapped and the app falls back to plain state.
function useSessionState(key, initialValue) {
  const storageKey = `creator-eaas:${key}`;

  const [value, setValue] = useState(() => {
    try {
      const stored = window.sessionStorage.getItem(storageKey);
      return stored === null ? initialValue : JSON.parse(stored);
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      if (value === null || value === undefined) {
        window.sessionStorage.removeItem(storageKey);
      } else {
        window.sessionStorage.setItem(storageKey, JSON.stringify(value));
      }
    } catch {
      // Storage unavailable; the value still works for this page load.
    }
  }, [storageKey, value]);

  return [value, setValue];
}

export default useSessionState;
