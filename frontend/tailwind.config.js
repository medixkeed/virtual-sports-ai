/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        charcoal: "#14171c",
        navy: "#1a2332",
        "navy-light": "#243044",
        electric: "#2d8cff",
        "electric-dim": "#1e5fbf",
        purpleOdds: "#7c3aed",
        muted: "#94a3b8",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
