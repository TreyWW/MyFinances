/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: 'jit',
  content: [
    './frontend/templates/**/*.html',
    './billing/templates/**/*.html',
    './components/**/*.html',
    './frontend/templates/base/base.html',
    './backend/**/views/*.py',
    './backend/views/core/**/*.py',
  ],
  safelist: [
    'alert',
    'alert-error',
    'alert-success',
    'alert-info',
    'alert-warning',
    'mask',
    'mask-half-1',
    'mask-half-2',
    {
      pattern: /link-(.*)/
    }
  ],
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      // "dark",,
      {
        light: {
          "color-scheme": "dark",
          "primary": "#8620a2",
          "primary-content": "#faebf2",
          "secondary": "#e983a0",
          "secondary-content": "#1a0c1d",
          "error": "#f58493",
          "accent": "#b7c2be",
          "accent-content": "#1a0c1d",
          "neutral": "#2B3440",
          "neutral-content": "#D7DDE4",
          "base-100": "#faf5fa",
          "base-200": "#eeeaee",
          "base-300": "#d7d4d7",
          "base-content": "#1a0c1d",
          "placeholderColor": "#0051ff",
        },
        dark:
          {
            "color-scheme": "dark",
            "primary": "#9376e1",
            "primary-content": "#0a050a",
            "secondary": "#5eb7b7",
            "secondary-content": "#1f1f1f",
            "error": "#e6949e",
            "success": "#94e6a4",
            "success-content": "#2a323c",
            "info": "#57c7aa",
            "accent": "#3d4844",
            "accent-content": "#f0e2f3",
            "neutral": "#2a323c",
            "neutral-content": "#A6ADBB",
            "base-100": "#1e2328",
            "base-200": "#191e23",
            "base-300": "#0f1215",
            "base-content": "#f0e2f3",
            "placeholderColor": "#0051ff",
          }
      }
    ],
    darkTheme:
      "dark",
  },
  variants:
    {
      extend: {
        display: ['group-hover'],
      }
      ,
    }
  ,
  theme: {
    extend: {
      zIndex: {
        '55': '55',
        '60': '60'
      },
      animation: {
        'infinite-scroll': 'infinite-scroll 40s linear infinite',
        'infinite-scroll-replay': 'infinite-scroll-replay 40s linear infinite'
      },
      keyframes: {
        'infinite-scroll': {
          '0%': {transform: 'translateX(0)'},
          '100%': {transform: 'translateX(-100%)'},
        },
        'infinite-scroll-replay': {
          '0%': {transform: 'translateX(100%)'},
          '100%': {transform: 'translateX(0)'},
        }
      },
      dropShadow: {
        glow: [
          "0 0px 20px rgba(255,255, 255, 0.35)",
          "0 0px 65px rgba(255, 255,255, 0.2)"
        ],
        glow_gold:
          [
            "0 0px 20px #bf9553",
            "0 0px 65px #bf9553"
          ],
        glow_red:
          [
            "0 0px 20px var(--fallback-er,oklch(var(--er)/var(--tw-text-opacity)))",
            "0 0px 65px var(--fallback-er,oklch(var(--er)/var(--tw-text-opacity)))"
          ],
        glow_gold_small:
          [
            "0 0px 15px #bf9553",
            // "0 0px 80px #bf9553"
          ]
      }
      ,
      // placeholderColor: {'custom': '#0051ff'}
    }
  }
}
