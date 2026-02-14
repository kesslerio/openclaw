/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "memex-primary": "#4F46E5",
        "memex-secondary": "#06B6D4",
        "memex-accent": "#F59E0B",
        "memex-bg": "#0F172A",
        "memex-surface": "#1E293B",
        "memex-text": "#F1F5F9",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["Fira Code", "monospace"],
      },
    },
  },
  plugins: [],
};
