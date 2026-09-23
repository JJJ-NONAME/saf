module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  roots: ["<rootDir>/src/ts"],
  testMatch: ["**/__tests__/**/*.test.tsx", "**/__tests__/**/*.test.ts"],
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    "\\.svg$": "<rootDir>/src/ts/__tests__/__mocks__/svgMock.js",
  },
  setupFilesAfterEnv: ["<rootDir>/src/ts/__tests__/setupTests.ts"],
  collectCoverageFrom: [
    "src/ts/**/*.{ts,tsx}",
    "!src/ts/**/*.d.ts",
    "!src/ts/__tests__/**",
  ],
  coverageDirectory: "coverage",
  coverageReporters: ["text", "lcov", "html"],
  transform: {
    "^.+\\.tsx?$": [
      "ts-jest",
      {
        tsconfig: "tsconfig.json",
      },
    ],
  },
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
};
