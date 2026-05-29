import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: "#6366f1", dark: "#4f46e5" },
      },
      fontFamily: { sans: ["var(--font-geist)", "system-ui", "sans-serif"] },
    },
  },
  plugins: [],
};
export default config;
