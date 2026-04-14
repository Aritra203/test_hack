/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        mist: '#eef2ff',
        coral: '#fb7185',
        teal: '#14b8a6',
        saffron: '#f59e0b',
      },
      boxShadow: {
        panel: '0 24px 48px -24px rgba(15, 23, 42, 0.55)',
      },
    },
  },
  plugins: [],
};
