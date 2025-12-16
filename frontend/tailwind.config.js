/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        maple: {
          orange: '#ff6b00',
          dark: '#1a1a2e',
          darker: '#16162a',
          accent: '#4a90d9',
        },
      },
    },
  },
  plugins: [],
};
