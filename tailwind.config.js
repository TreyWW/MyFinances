/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './frontend/templates/**/*.html',
        './components/**/*.html',
        './frontend/templates/base/base.html',
        './backend/**/views/*.py',
        '/backend/views/core/**/*.py',
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
                    "primary": "#8B45BA",
                    "secondary": "#6a74ec",
                    "secondary-content": "#c5c5c5",
                    "error": "#e6949e",
                    "accent": "#5B62E1",
                    "neutral": "#2B3440",
                    "neutral-content": "#D7DDE4",
                    "base-100": "oklch(100% 0 0)",
                    "base-200": "#F2F2F2",
                    "base-300": "#E5E6E6",
                    "base-content": "#1f2937",
                    "placeholderColor": "#0051ff",
                },
                dark:
                    {
                        "color-scheme":
                            "dark",
                        "primary":
                            "#9376e1",
                        "secondary":
                            "#9498E6",
                        "error":
                            "#e6949e",
                        "success": "#94e6a4",
                        "success-content": "#2a323c",
                        "accent":
                            "#5B62E1",
                        "neutral":
                            "#2a323c",
                        "neutral-content":
                            "#A6ADBB",
                        "base-100":
                            "#2b343d",
                        "base-200":
                            "#1D232A",
                        "base-300":
                            "#191d25",
                        "base-content":
                            "#BFBFBF",
                        "placeholderColor":
                            "#0051ff",
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
            animation: {
                // 'pulse-slow': 'pulse 4s linear infinite',
            }
            ,
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
