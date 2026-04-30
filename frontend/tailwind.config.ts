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
        // ── Custom design palette ──────────────────────────────
        deepBlack:  "#0A0A0A",
        surface:    "#121212",
        surfaceHi:  "#1A1A2E",
        neonBlue:   "#00D4FF",
        neonPurple: "#7B61FF",
        success:    "#00FF9C",
        danger:     "#FF4D4D",
        warning:    "#FFB347",
        muted:      "#6B7280",
        // keep default var() tokens
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      fontFamily: {
        poppins: ["var(--font-poppins)", "sans-serif"],
        inter:   ["var(--font-inter)",   "sans-serif"],
      },
      boxShadow: {
        neon:    "0 0 20px rgba(0, 212, 255, 0.4), 0 0 60px rgba(0, 212, 255, 0.1)",
        purple:  "0 0 20px rgba(123, 97, 255, 0.4), 0 0 60px rgba(123, 97, 255, 0.1)",
        success: "0 0 20px rgba(0, 255, 156, 0.35)",
        danger:  "0 0 20px rgba(255, 77, 77, 0.35)",
        glass:   "inset 0 1px 0 rgba(255,255,255,0.1), 0 4px 32px rgba(0,0,0,0.4)",
      },
      backgroundImage: {
        "hero-gradient":   "linear-gradient(135deg, #0A0A0A 0%, #1A1A2E 50%, #0A0A0A 100%)",
        "neon-gradient":   "linear-gradient(135deg, #00D4FF, #7B61FF)",
        "card-gradient":   "linear-gradient(145deg, rgba(26,26,46,0.9), rgba(18,18,18,0.95))",
        "border-gradient": "linear-gradient(135deg, rgba(0,212,255,0.3), rgba(123,97,255,0.3))",
      },
      keyframes: {
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(0,212,255,0.4)" },
          "50%":      { boxShadow: "0 0 40px rgba(0,212,255,0.8), 0 0 80px rgba(0,212,255,0.3)" },
        },
        "spin-neon": {
          "0%":   { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        "fade-up": {
          "0%":   { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "spin-neon":  "spin-neon 1s linear infinite",
        "fade-up":    "fade-up 0.5s ease-out forwards",
        "fade-in":    "fade-in 0.4s ease-out forwards",
        shimmer:      "shimmer 2s linear infinite",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
export default config;
