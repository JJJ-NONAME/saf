/**
 * Jest setup file for React Testing Library
 */
import "@testing-library/jest-dom";

// Mock window.URL methods for file export tests
global.URL.createObjectURL = jest.fn(() => "blob:mock-url");
global.URL.revokeObjectURL = jest.fn();

// Mock fetch for API tests
global.fetch = jest.fn();

// Reset mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
});
