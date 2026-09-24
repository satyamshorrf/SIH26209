/**
 * Tailwind CSS v4 configuration.
 *
 * With Tailwind v4 the bulk of configuration lives in CSS (see src/index.css
 * which uses `@import "tailwindcss"` and the `@theme` block).  This file is kept
 * for editor tooling and to declare the content sources explicitly.
 *
 * @type {import('tailwindcss').Config}
 */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        space: {
          900: "#070b18",
          800: "#0b1020",
          700: "#121a33",
          600: "#1b264d",
        },
        accent: {
          blue: "#4f8cff",
          purple: "#a855f7",
        },
      },
    },
  },
  plugins: [],
};
