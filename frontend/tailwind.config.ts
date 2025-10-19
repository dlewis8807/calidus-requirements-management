import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // CALIDUS Aerospace brand colors
        calidus: {
          blue: '#3B7DDD',
          'blue-light': '#5A96E8',
          'blue-dark': '#2C5DBB',
          silver: '#A8A9AD',
          'silver-light': '#C8C9CD',
          'silver-dark': '#88898D',
          gray: '#6B7280',
        },
        primary: {
          50: '#EBF3FE',
          100: '#D7E7FD',
          200: '#AFCFFB',
          300: '#87B7F9',
          400: '#5F9FF7',
          500: '#3B7DDD', // Main CALIDUS blue
          600: '#2F64B1',
          700: '#234B85',
          800: '#173259',
          900: '#0B192D',
        },
      },
    },
  },
  plugins: [],
};

export default config;
