/**
 * Tests for useTheme hook
 */
import { renderHook, act } from "@testing-library/react";
import { useTheme } from "../hooks/useTheme";

const STORAGE_KEY = "awc-theme-preference";

describe("useTheme", () => {
  let addEventListenerMock: jest.Mock;
  let removeEventListenerMock: jest.Mock;

  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove("light", "dark");

    addEventListenerMock = jest.fn();
    removeEventListenerMock = jest.fn();
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: jest.fn().mockReturnValue({
        matches: false,
        addEventListener: addEventListenerMock,
        removeEventListener: removeEventListenerMock,
      }),
    });
  });

  afterEach(() => {
    document.documentElement.classList.remove("light", "dark");
  });

  it("defaults to light theme when no localStorage and system prefers light", () => {
    const { result } = renderHook(() => useTheme());

    expect(result.current.themeMode).toBe("light");
    expect(document.documentElement.classList.contains("light")).toBe(true);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("defaults to dark theme when no localStorage and system prefers dark", () => {
    (window.matchMedia as jest.Mock).mockReturnValue({
      matches: true,
      addEventListener: addEventListenerMock,
      removeEventListener: removeEventListenerMock,
    });

    const { result } = renderHook(() => useTheme());

    expect(result.current.themeMode).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("uses localStorage value over system preference", () => {
    localStorage.setItem(STORAGE_KEY, "dark");

    (window.matchMedia as jest.Mock).mockReturnValue({
      matches: false,
      addEventListener: addEventListenerMock,
      removeEventListener: removeEventListenerMock,
    });

    const { result } = renderHook(() => useTheme());

    expect(result.current.themeMode).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("toggles from light to dark and persists to localStorage", () => {
    const { result } = renderHook(() => useTheme());

    expect(result.current.themeMode).toBe("light");

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.themeMode).toBe("dark");
    expect(localStorage.getItem(STORAGE_KEY)).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(document.documentElement.classList.contains("light")).toBe(false);
  });

  it("toggles from dark to light and persists to localStorage", () => {
    localStorage.setItem(STORAGE_KEY, "dark");
    (window.matchMedia as jest.Mock).mockReturnValue({
      matches: true,
      addEventListener: addEventListenerMock,
      removeEventListener: removeEventListenerMock,
    });

    const { result } = renderHook(() => useTheme());

    expect(result.current.themeMode).toBe("dark");

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.themeMode).toBe("light");
    expect(localStorage.getItem(STORAGE_KEY)).toBe("light");
    expect(document.documentElement.classList.contains("light")).toBe(true);
  });

  it("removes theme classes on unmount", () => {
    const { unmount } = renderHook(() => useTheme());

    expect(document.documentElement.classList.contains("light")).toBe(true);

    unmount();

    expect(document.documentElement.classList.contains("light")).toBe(false);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("listens for system preference changes", () => {
    renderHook(() => useTheme());

    expect(addEventListenerMock).toHaveBeenCalledWith(
      "change",
      expect.any(Function),
    );
  });

  it("follows system preference change when no explicit user choice", () => {
    const { result } = renderHook(() => useTheme());

    expect(result.current.themeMode).toBe("light");

    const handler = addEventListenerMock.mock.calls[0][1];
    act(() => {
      handler({ matches: true } as MediaQueryListEvent);
    });

    expect(result.current.themeMode).toBe("dark");
  });

  it("ignores system preference change when user has explicit choice", () => {
    localStorage.setItem(STORAGE_KEY, "light");
    const { result } = renderHook(() => useTheme());

    expect(result.current.themeMode).toBe("light");

    const handler = addEventListenerMock.mock.calls[0][1];
    act(() => {
      handler({ matches: true } as MediaQueryListEvent);
    });

    expect(result.current.themeMode).toBe("light");
  });

  it("ignores invalid localStorage values and falls back to system", () => {
    localStorage.setItem(STORAGE_KEY, "invalid-value");

    const { result } = renderHook(() => useTheme());

    expect(result.current.themeMode).toBe("light");
  });

  it("cleans up media query listener on unmount", () => {
    const { unmount } = renderHook(() => useTheme());

    unmount();

    expect(removeEventListenerMock).toHaveBeenCalledWith(
      "change",
      expect.any(Function),
    );
  });
});
