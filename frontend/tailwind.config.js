/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          600: '#2563eb',
          800: '#1e40af',
          900: '#1e3a5f',
        },
      },
    },
  },
  plugins: [],
};
