/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  safelist: [
    'glass-panel',
    'glass-button',
    'glass-card',
    {
      pattern: /bg-(blue|red|yellow|green|slate|gray)-(100|200|300|400|500|600|700|800|900)/,
    },
    {
      pattern: /border-(blue|red|yellow|green|slate|gray)-(100|200|300|400|500)/,
    },
    {
      pattern: /text-(blue|red|yellow|green|slate|gray)-(100|200|300|400|500|600|700|800|900)/,
    },
  ],
  theme: {
    extend: {
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        '2xl': '24px',
        '3xl': '32px',
      },
      backgroundColor: {
        'glass': 'rgba(15, 23, 42, 0.7)',
        'glass-lighter': 'rgba(15, 23, 42, 0.5)',
        'glass-lightest': 'rgba(15, 23, 42, 0.3)',
        'glass-light': 'rgba(15, 23, 42, 0.4)',
        'glass-dark': 'rgba(15, 23, 42, 0.8)',
        'glass-card': 'rgba(15, 23, 42, 0.6)',
      },
      borderColor: {
        'glass': 'rgba(255, 255, 255, 0.1)',
        'glass-accent': 'rgba(14, 165, 233, 0.3)',
        'glass-highlight': 'rgba(56, 189, 248, 0.4)',
      },
      boxShadow: {
        'glass': '0 4px 15px -3px rgba(0, 0, 0, 0.3), 0 2px 8px -2px rgba(0, 0, 0, 0.2)',
        'glass-hover': '0 0 15px 3px rgba(14, 165, 233, 0.3)',
        'glass-highlight': '0 0 12px 2px rgba(56, 189, 248, 0.25)',
      },
      borderRadius: {
        'glass': '0.5rem',
      },
      animation: {
        'glass-shimmer': 'glass-shimmer 3s infinite',
        'glass-pulse': 'glass-pulse 4s infinite',
      },
      keyframes: {
        'glass-shimmer': {
          '0%, 100%': { transform: 'translateX(-100%)' },
          '50%': { transform: 'translateX(100%)' },
        },
        'glass-pulse': {
          '0%, 100%': { boxShadow: '0 0 12px 2px rgba(56, 189, 248, 0.1)' },
          '50%': { boxShadow: '0 0 18px 4px rgba(56, 189, 248, 0.3)' },
        },
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(135deg, rgba(15, 23, 42, 0.6), rgba(15, 23, 42, 0.7))',
      },
      textColor: {
        'content': 'rgba(255, 255, 255, 0.85)',
        'primary-light': 'rgba(125, 211, 252, 1)',
        'success-light': 'rgba(134, 239, 172, 1)',
        'warning-light': 'rgba(250, 204, 21, 1)',
        'danger-light': 'rgba(248, 113, 113, 1)',
      },
      colors: {
        primary: {
          DEFAULT: 'rgb(14, 165, 233)',
        },
        success: {
          DEFAULT: 'rgb(34, 197, 94)',
        },
        warning: {
          DEFAULT: 'rgb(234, 179, 8)',
        },
        danger: {
          DEFAULT: 'rgb(239, 68, 68)',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}