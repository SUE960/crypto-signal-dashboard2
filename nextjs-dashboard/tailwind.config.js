/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  // 중요한 클래스들이 프로덕션에서 제거되지 않도록 safelist 추가
  safelist: [
    'bg-gray-900',
    'bg-gray-800',
    'bg-gray-700',
    'text-white',
    'text-gray-400',
    'text-gray-300',
    'text-gray-200',
    'text-gray-100',
    'border-gray-700',
    'bg-gradient-to-r',
    'from-gray-800',
    'via-gray-900',
    'to-gray-800',
    'bg-blue-400',
    'bg-purple-400',
    'text-blue-400',
    'text-green-400',
    'text-red-400',
    'bg-green-500',
    'bg-red-500',
    'rounded-xl',
    'shadow-xl',
    'shadow-2xl',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
  plugins: [],
}



