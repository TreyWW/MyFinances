/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './frontend/templates/**/*.html',
        './components/**/*.html',
        './frontend/templates/base/base.html', './backend/**/views/*.py',
    ],
    safelist: [
        'alert',
        'alert-error',
        'alert-success',
        'alert-info',
        'alert-warning',
        'mask',
        'mask-half-1',
        'mask-half-2'
    ],
    plugins: [require("daisyui")],
    daisyui: {
        themes: [
            // "dark",
            "light",
            {
                dark: {
                    "color-scheme": "dark",
                    "primary": "#985eff", // 985eff
                    "primary-content": "#ffffff",
                    "gold": "#bf9553",
                    "secondary": "#1FB2A5",
                    "secondary-content": "#ffffff",
                    "accent": "#1FB2A5",
                    "accent-content": "#ffffff",
                    "neutral": "#2a323c",
                    "neutral-focus": "#242b33",
                    "neutral-content": "#A6ADBB",
                    "base-100": "#1d232a",
                    "base-200": "#191e24",
                    "base-300": "#15191e",
                    "base-content": "#A6ADBB",
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
            },
        },
    theme: {
        extend: {
            animation: {
                // 'pulse-slow': 'pulse 4s linear infinite',
            },
            dropShadow: {
                glow: [
                    "0 0px 20px rgba(255,255, 255, 0.35)",
                    "0 0px 65px rgba(255, 255,255, 0.2)"
                ],
                glow_gold: [
                    "0 0px 20px #bf9553",
                    "0 0px 65px #bf9553"
                ],
                glow_gold_small: [
                    "0 0px 15px #bf9553",
                    // "0 0px 80px #bf9553"
                ]
            },
            // placeholderColor: {'custom': '#0051ff'}
        }
    }
}
