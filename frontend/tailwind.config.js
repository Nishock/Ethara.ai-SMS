/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f3ff',
          100: '#edd8ff',
          200: '#d9b6ff',
          300: '#c594ff',
          400: '#b172ff',
          500: '#9d50ff',
          600: '#892edd',
          700: '#750cbb',
          800: '#610099',
          900: '#4d0077',
        }
      }
    },
  },
  plugins: [],
}
