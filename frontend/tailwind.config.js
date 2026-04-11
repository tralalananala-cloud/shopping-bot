/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        tg: {
          bg:       'var(--tg-bg)',
          bg2:      'var(--tg-bg2)',
          text:     'var(--tg-text)',
          hint:     'var(--tg-hint)',
          btn:      'var(--tg-btn)',
          'btn-t':  'var(--tg-btn-text)',
        },
      },
      borderRadius: { xl2: '16px' },
    },
  },
  plugins: [],
}
