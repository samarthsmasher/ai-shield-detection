"use client";

import { useEffect, useState } from "react";

interface ResultCardProps {
  result:     string;    // "spam" | "ham" | "real" | "fake" | "unknown"
  confidence: number;    // 0.0 – 1.0
  inputType:  string;    // "text" | "image" | "video"
  timestamp?: string;    // ISO date string
}

// ── Badge config ──────────────────────────────────────────────────────────────
function getBadge(result: string, inputType: string): {
  label: string; color: string; bg: string; glow: string; icon: string;
} {
  const r = result.toLowerCase();
  if (r === "spam")    return { label: "SPAM",     color: "text-danger",     bg: "bg-danger/10",     glow: "shadow-danger",     icon: "🚨" };
  if (r === "ham")     return { label: "SAFE",     color: "text-success",    bg: "bg-success/10",    glow: "shadow-success",    icon: "✅" };
  if (r === "fake")    return { label: "FAKE",     color: "text-danger",     bg: "bg-danger/10",     glow: "shadow-danger",     icon: "🤖" };
  if (r === "real")    return { label: "AUTHENTIC",color: "text-success",    bg: "bg-success/10",    glow: "shadow-success",    icon: "🛡️" };
  return              { label: "UNKNOWN",           color: "text-warning",    bg: "bg-warning/10",    glow: "",                  icon: "❓" };
}

function getInputLabel(inputType: string): string {
  if (inputType === "text")  return "Text Analysis";
  if (inputType === "image") return "Image Analysis";
  if (inputType === "video") return "Video Analysis";
  return "Analysis";
}

// ── Task 5.6 — ResultCard Component ─────────────────────────────────────────
export default function ResultCard({ result, confidence, inputType, timestamp }: ResultCardProps) {
  const badge    = getBadge(result, inputType);
  const pct      = Math.round(confidence * 100);
  const [animPct, setAnimPct] = useState(0);

  // Animate confidence bar on mount
  useEffect(() => {
    const timer = setTimeout(() => setAnimPct(pct), 80);
    return () => clearTimeout(timer);
  }, [pct]);

  const barColor =
    badge.label === "SPAM" || badge.label === "FAKE"
      ? "from-danger to-red-600"
      : badge.label === "AUTHENTIC" || badge.label === "SAFE"
      ? "from-success to-emerald-400"
      : "from-warning to-amber-400";

  return (
    <div className={`glass-card p-6 animate-fade-up ${badge.glow}`}>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <p className="font-inter text-xs text-white/40 uppercase tracking-widest mb-1">
            {getInputLabel(inputType)}
          </p>
          <h2 className="font-poppins font-bold text-2xl text-white">Detection Result</h2>
        </div>
        {/* Timestamp */}
        {timestamp && (
          <span className="font-inter text-xs text-white/30 mt-1">
            {new Date(timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>

      {/* ── Status badge ────────────────────────────────────────────────── */}
      <div className={`inline-flex items-center gap-2.5 px-5 py-2.5 rounded-full ${badge.bg} mb-6`}>
        <span className="text-xl" aria-hidden="true">{badge.icon}</span>
        <span className={`font-poppins font-bold text-lg tracking-wide ${badge.color}`}>
          {badge.label}
        </span>
      </div>

      {/* ── Confidence bar ──────────────────────────────────────────────── */}
      <div>
        <div className="flex justify-between items-baseline mb-2">
          <span className="font-inter text-sm text-white/60">Confidence</span>
          <span className="font-poppins font-bold text-white text-xl">{pct}%</span>
        </div>

        {/* Track */}
        <div className="w-full h-2.5 bg-white/5 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${barColor} transition-all duration-700 ease-out`}
            style={{ width: `${animPct}%` }}
            role="progressbar"
            aria-valuenow={pct}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>

        {/* Scale labels */}
        <div className="flex justify-between mt-1">
          <span className="font-inter text-xs text-white/25">0%</span>
          <span className="font-inter text-xs text-white/25">100%</span>
        </div>
      </div>

      {/* ── Interpretation note ──────────────────────────────────────────── */}
      <p className="font-inter text-sm text-white/40 mt-4 border-t border-white/5 pt-4">
        {badge.label === "SPAM"
          ? "This message shows strong indicators of spam or phishing content."
          : badge.label === "SAFE"
          ? "This message appears to be legitimate and safe."
          : badge.label === "FAKE"
          ? "This content shows signs of AI generation or manipulation."
          : badge.label === "AUTHENTIC"
          ? "This content appears to be genuine and unmanipulated."
          : "Could not confidently classify this content."}
      </p>
    </div>
  );
}
