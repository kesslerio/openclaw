/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "gray-850": "#1a1f2e",
        "priority-high": "#EF4444",
        "priority-medium": "#F59E0B",
        "priority-low": "#22C55E",
        "column-backlog": "#6B7280",
        "column-todo": "#3B82F6",
        "column-doing": "#F59E0B",
        "column-done": "#10B981",
      },
    },
  },
  plugins: [],
};
