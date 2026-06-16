import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    include: ["tests/**/*.test.{ts,tsx}"],
    exclude: ["**/node_modules/**"],
    environment: "jsdom",
    globals: true,
    setupFiles: ["tests/setup.ts"],
  },
});
