/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,jsx,ts,tsx}",
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./animations/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f5f7ff",
          100: "#e7ebff",
          200: "#cfd7ff",
          300: "#a7b7ff",
          400: "#7d93ff",
          500: "#546cff",
          600: "#3f53f5",
          700: "#3342d6",
          800: "#2d3aa8",
          900: "#292f84",
        },
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(255,255,255,.2), 0 10px 40px rgba(31,38,135,.25)",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};

