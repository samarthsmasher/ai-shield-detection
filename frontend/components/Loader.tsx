"use client";

// ── Task 5.7 — Loader Component ──────────────────────────────────────────────
// Animated neon spinner with glow effect + optional label.

interface LoaderProps {
  label?: string;   // e.g. "Analyzing your text..."
  size?: "sm" | "md" | "lg";
}

const SIZES = {
  sm: { outer: "w-10 h-10", inner: "w-6 h-6",  text: "text-xs" },
  md: { outer: "w-16 h-16", inner: "w-10 h-10", text: "text-sm" },
  lg: { outer: "w-24 h-24", inner: "w-16 h-16", text: "text-base" },
};

export default function Loader({ label = "Analyzing…", size = "md" }: LoaderProps) {
  const s = SIZES[size];

  return (
    <div className="flex flex-col items-center justify-center gap-5 py-10 animate-fade-in">

      {/* ── Spinner stack ─────────────────────────────────────────────────── */}
      <div className="relative flex items-center justify-center">

        {/* Outer ring — slow, neon blue */}
        <div
          className={`${s.outer} rounded-full border-2 border-transparent animate-spin-neon`}
          style={{
            borderTopColor: "#00D4FF",
            borderRightColor: "rgba(0,212,255,0.2)",
            boxShadow: "0 0 20px rgba(0,212,255,0.5), 0 0 40px rgba(0,212,255,0.2)",
            animationDuration: "1.2s",
          }}
        />

        {/* Middle ring — medium, neon purple, opposite direction */}
        <div
          className={`${s.inner} absolute rounded-full border-2 border-transparent`}
          style={{
            borderTopColor: "#7B61FF",
            borderLeftColor: "rgba(123,97,255,0.2)",
            boxShadow: "0 0 12px rgba(123,97,255,0.4)",
            animation: "spin-neon 0.8s linear infinite reverse",
          }}
        />

        {/* Centre pulse dot */}
        <div className="absolute w-2 h-2 rounded-full bg-neonBlue animate-glow-pulse" />
      </div>

      {/* ── Label ─────────────────────────────────────────────────────────── */}
      <div className="text-center">
        <p className={`font-poppins font-medium text-white/70 ${s.text}`}>{label}</p>
        {/* Shimmer dots */}
        <div className="flex items-center justify-center gap-1 mt-2">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-1 h-1 rounded-full bg-neonBlue/60"
              style={{
                animation: `glow-pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
