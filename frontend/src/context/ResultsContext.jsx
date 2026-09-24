import { createContext, useCallback, useContext, useMemo, useState } from "react";

const ResultsContext = createContext(null);

/**
 * Stores the most recent result from each analysis module so the Results page
 * can present a consolidated mission summary.
 */
export function ResultsProvider({ children }) {
  const [results, setResults] = useState({});

  const saveResult = useCallback((moduleKey, payload) => {
    setResults((prev) => ({
      ...prev,
      [moduleKey]: { payload, savedAt: new Date().toISOString() },
    }));
  }, []);

  const clearResults = useCallback(() => setResults({}), []);

  const value = useMemo(
    () => ({ results, saveResult, clearResults }),
    [results, saveResult, clearResults]
  );

  return (
    <ResultsContext.Provider value={value}>{children}</ResultsContext.Provider>
  );
}

export function useResults() {
  const ctx = useContext(ResultsContext);
  if (!ctx) throw new Error("useResults must be used within a ResultsProvider");
  return ctx;
}
