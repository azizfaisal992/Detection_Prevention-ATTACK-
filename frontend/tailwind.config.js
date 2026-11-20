/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#050b18',
          900: '#091426',
          800: '#10203a',
        },
      },
    },
  },
  plugins: [],
}

