import { useState, useEffect, useCallback } from "react";

export type Theme = "light" | "dark";

const STORAGE_KEY = "awc-theme-preference";

/**
 * Detect the system/browser preferred color scheme.
 * Falls back to "light" if no preference is detected.
 */
const getSystemTheme = (): Theme => {
  if (typeof window !== "undefined" && window.matchMedia) {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }
  return "light";
};

/**
 * Resolve the initial theme: localStorage > system preference > "light".
 */
const getInitialTheme = (): Theme => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") {
      return stored;
    }
  }
  return getSystemTheme();
};

/**
 * Apply the theme class to <html> and remove the opposite one.
 */
const applyThemeClass = (theme: Theme): void => {
  const root = document.documentElement;
  const opposite: Theme = theme === "light" ? "dark" : "light";
  root.classList.remove(opposite);
  root.classList.add(theme);
};

/**
 * Custom hook that manages the light/dark theme.
 *
 * - If `externalTheme` is provided, it takes precedence (controlled mode).
 * - Otherwise reads initial theme from localStorage, then system preference, then "light"
 * - Applies the theme class ("light" or "dark") to <html>
 * - Persists the user's choice to localStorage
 * - Listens for system preference changes (if no explicit user choice)
 */
export const useTheme = (externalTheme?: Theme) => {
  const [theme, setTheme] = useState<Theme>(externalTheme ?? getInitialTheme);

  // Sync with external theme prop when it changes
  useEffect(() => {
    if (externalTheme) {
      setTheme(externalTheme);
    }
  }, [externalTheme]);

  // Apply theme class whenever it changes
  useEffect(() => {
    applyThemeClass(theme);
  }, [theme]);

  // Listen for system preference changes
  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;

    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = (e: MediaQueryListEvent) => {
      // Only follow system if user hasn't explicitly chosen and no external control
      if (externalTheme) return;
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        setTheme(e.matches ? "dark" : "light");
      }
    };

    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, [externalTheme]);

  // Cleanup theme class on unmount
  useEffect(() => {
    return () => {
      document.documentElement.classList.remove("light", "dark");
    };
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const next: Theme = prev === "light" ? "dark" : "light";
      localStorage.setItem(STORAGE_KEY, next);
      return next;
    });
  }, []);

  return { themeMode: theme, toggleTheme } as const;
};
