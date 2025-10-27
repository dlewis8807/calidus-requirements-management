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
        // Modern pastel palette for charts (Quicken-inspired)
        chart: {
          mint: '#A7F3D0',
          teal: '#5EEAD4',
          sky: '#7DD3FC',
          lavender: '#C4B5FD',
          rose: '#FECDD3',
          amber: '#FDE68A',
        },
      },
      borderRadius: {
        'card': '16px',
        'card-lg': '20px',
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.03), 0 1px 2px 0 rgba(0, 0, 0, 0.02)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
      },
    },
  },
  plugins: [],
};

export default config;
