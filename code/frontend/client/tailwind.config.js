/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'neon-green': '#ccff00',
        'neon-blue': '#00f3ff',
        'dark-bg': '#050505',
        'charcoal': '#121212',
        'glass-dark': 'rgba(20, 20, 20, 0.6)',
      },
      fontFamily: {
        'orbitron': ['"Orbitron"', 'sans-serif'],
        'rajdhani': ['"Rajdhani"', 'sans-serif'],
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #ccff00, 0 0 10px #ccff00' },
          '100%': { boxShadow: '0 0 10px #ccff00, 0 0 20px #ccff00' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
