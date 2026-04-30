"use client";

import Link from "next/link";

interface DetectionModeCardProps {
  href:        string;
  icon:        React.ReactNode;
  title:       string;
  description: string;
  accent:      "blue" | "purple" | "success";
  badge?:      string;   // e.g. "Most Popular"
}

const ACCENT = {
  blue: {
    border: "hover:border-neonBlue/60",
    glow:   "hover:shadow-neon",
    text:   "text-neonBlue",
    bg:     "bg-neonBlue/10 group-hover:bg-neonBlue/15",
    dot:    "bg-neonBlue",
    badge:  "bg-neonBlue/20 text-neonBlue border-neonBlue/30",
  },
  purple: {
    border: "hover:border-neonPurple/60",
    glow:   "hover:shadow-purple",
    text:   "text-neonPurple",
    bg:     "bg-neonPurple/10 group-hover:bg-neonPurple/15",
    dot:    "bg-neonPurple",
    badge:  "bg-neonPurple/20 text-neonPurple border-neonPurple/30",
  },
  success: {
    border: "hover:border-success/60",
    glow:   "hover:shadow-success",
    text:   "text-success",
    bg:     "bg-success/10 group-hover:bg-success/15",
    dot:    "bg-success",
    badge:  "bg-success/20 text-success border-success/30",
  },
};

// ── Task 5.8 — DetectionModeCard Component ───────────────────────────────────
export default function DetectionModeCard({
  href,
  icon,
  title,
  description,
  accent,
  badge,
}: DetectionModeCardProps) {
  const a = ACCENT[accent];

  return (
    <Link href={href} className="group block h-full" aria-label={`${title} detection`}>
      <div
        className={`
          relative h-full glass-card p-7
          border border-white/8
          transition-all duration-300 ease-out
          ${a.border} ${a.glow}
          hover:-translate-y-1 hover:scale-[1.01]
          cursor-pointer
        `}
      >
        {/* ── Badge ─────────────────────────────────────────────────────── */}
        {badge && (
          <span className={`absolute top-4 right-4 text-xs font-poppins font-semibold px-2.5 py-1 rounded-full border ${a.badge}`}>
            {badge}
          </span>
        )}

        {/* ── Icon circle ───────────────────────────────────────────────── */}
        <div className={`
          w-14 h-14 rounded-2xl flex items-center justify-center
          transition-all duration-300
          ${a.bg}
          group-hover:scale-110
          mb-5
        `}>
          <span className="text-2xl" aria-hidden="true">{icon}</span>
        </div>

        {/* ── Title ─────────────────────────────────────────────────────── */}
        <h3 className={`font-poppins font-bold text-lg mb-2 transition-colors duration-200 ${a.text}`}>
          {title}
        </h3>

        {/* ── Description ───────────────────────────────────────────────── */}
        <p className="font-inter text-sm text-white/55 leading-relaxed mb-5">
          {description}
        </p>

        {/* ── CTA row ───────────────────────────────────────────────────── */}
        <div className="flex items-center gap-2">
          <span className={`font-inter text-sm font-medium ${a.text}`}>
            Analyze now
          </span>
          <span
            className={`transition-transform duration-200 group-hover:translate-x-1.5 ${a.text}`}
            aria-hidden="true"
          >
            →
          </span>
        </div>

        {/* ── Bottom accent line ────────────────────────────────────────── */}
        <div
          className={`
            absolute bottom-0 left-0 right-0 h-0.5 rounded-b-2xl
            transition-all duration-300
            opacity-0 group-hover:opacity-100
            ${a.dot === "bg-neonBlue" ? "bg-gradient-to-r from-neonBlue/0 via-neonBlue to-neonBlue/0"
              : a.dot === "bg-neonPurple" ? "bg-gradient-to-r from-neonPurple/0 via-neonPurple to-neonPurple/0"
              : "bg-gradient-to-r from-success/0 via-success to-success/0"}
          `}
        />
      </div>
    </Link>
  );
}
