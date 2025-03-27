/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {

        "dark-bg": "#1a1a1a",
        "dark-node": "#2a2a2a",
        "dark-border": "#444",
        "dark-edge": "#888",
        "hover-bg": "#3a3a3a",
        "node-input": "#ff6b6b",
        "node-output": "#4ecdc4",
        "node-default": "#6b7280",
      },
    },
  },
  plugins: [],
};