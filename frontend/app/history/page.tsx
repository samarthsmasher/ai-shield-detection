"use client";

import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// ── Types ─────────────────────────────────────────────────────────────────────
interface HistoryItem {
  id:         string;
  input_type: "text" | "image" | "video";
  result:     string;
  confidence: number;
  timestamp:  string;
  user_id:    string | null;
}

interface Stats {
  total:     number;
  by_type:   { text: number; image: number; video: number };
  by_result: { spam: number; fake: number; real: number; ham: number };
}

interface HistoryResponse {
  items: HistoryItem[];
  stats: Stats;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const TYPE_META = {
  text:  { icon: "💬", label: "Text",  color: "text-neonBlue",   bg: "bg-neonBlue/10",   border: "border-neonBlue/20"  },
  image: { icon: "🖼️", label: "Image", color: "text-neonPurple", bg: "bg-neonPurple/10", border: "border-neonPurple/20"},
  video: { icon: "🎬", label: "Video", color: "text-success",    bg: "bg-success/10",    border: "border-success/20"   },
};

const RESULT_META: Record<string, { label: string; color: string; bg: string; icon: string }> = {
  spam:    { label: "SPAM",     color: "text-danger",     bg: "bg-danger/10",     icon: "🚨" },
  fake:    { label: "FAKE",     color: "text-danger",     bg: "bg-danger/10",     icon: "🤖" },
  real:    { label: "AUTHENTIC",color: "text-success",    bg: "bg-success/10",    icon: "🛡️" },
  ham:     { label: "SAFE",     color: "text-success",    bg: "bg-success/10",    icon: "✅" },
};

function fmtTime(iso: string): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("en-IN", {
    day:    "2-digit",
    month:  "short",
    hour:   "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

function fmtPct(conf: number): string {
  return `${Math.round(conf * 100)}%`;
}

// ── Stat Card ─────────────────────────────────────────────────────────────────
function StatCard({ value, label, icon, accent }: {
  value: number | string; label: string; icon: string; accent: string;
}) {
  return (
    <motion.div
      className="glass-card p-5 flex flex-col gap-2"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex items-center justify-between">
        <span className="text-2xl">{icon}</span>
        <span className={`font-poppins font-bold text-3xl ${accent}`}>{value}</span>
      </div>
      <p className="font-inter text-xs text-white/40 uppercase tracking-widest">{label}</p>
    </motion.div>
  );
}

// ── Donut mini chart (CSS only) ────────────────────────────────────────────────
function MiniDonut({ slices }: { slices: { pct: number; color: string }[] }) {
  let cumulative = 0;
  const r = 30;
  const cx = 36, cy = 36;
  const circumference = 2 * Math.PI * r;

  return (
    <svg width="72" height="72" viewBox="0 0 72 72" className="rotate-[-90deg]">
      {slices.map((s, i) => {
        const dashArray  = (s.pct / 100) * circumference;
        const dashOffset = circumference - cumulative * circumference / 100;
        cumulative += s.pct;
        return (
          <circle
            key={i}
            cx={cx} cy={cy} r={r}
            fill="none"
            stroke={s.color}
            strokeWidth="10"
            strokeDasharray={`${dashArray} ${circumference}`}
            strokeDashoffset={circumference - (cumulative - s.pct) * circumference / 100}
            style={{ transition: "stroke-dasharray 0.6s ease" }}
          />
        );
      })}
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10"
        strokeDasharray={`${circumference} ${circumference}`} />
    </svg>
  );
}

// ── History Row ────────────────────────────────────────────────────────────────
function HistoryRow({ item, index }: { item: HistoryItem; index: number }) {
  const typeMeta   = TYPE_META[item.input_type] ?? TYPE_META.text;
  const resultMeta = RESULT_META[item.result.toLowerCase()] ?? {
    label: item.result.toUpperCase(), color: "text-white/60", bg: "bg-white/5", icon: "❓"
  };
  const pct = Math.round(item.confidence * 100);
  const barColor = (item.result === "spam" || item.result === "fake")
    ? "from-danger to-red-600"
    : "from-success to-emerald-400";

  return (
    <motion.div
      className="glass-card p-4 flex flex-col sm:flex-row sm:items-center gap-4"
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: index * 0.03 }}
    >
      {/* Type badge */}
      <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full ${typeMeta.bg} border ${typeMeta.border} shrink-0`}>
        <span className="text-sm">{typeMeta.icon}</span>
        <span className={`font-poppins font-semibold text-xs ${typeMeta.color}`}>{typeMeta.label}</span>
      </div>

      {/* Result badge */}
      <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full ${resultMeta.bg} shrink-0`}>
        <span className="text-sm">{resultMeta.icon}</span>
        <span className={`font-poppins font-bold text-xs ${resultMeta.color}`}>{resultMeta.label}</span>
      </div>

      {/* Confidence bar */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <span className="font-inter text-xs text-white/40">Confidence</span>
          <span className="font-poppins font-bold text-sm text-white">{fmtPct(item.confidence)}</span>
        </div>
        <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${barColor} transition-all duration-700`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* User */}
      <div className="flex items-center gap-1.5 shrink-0">
        <span className="text-white/20 text-xs">{item.user_id ? "👤" : "👁️"}</span>
        <span className="font-inter text-xs text-white/30">
          {item.user_id ? "Logged in" : "Anonymous"}
        </span>
      </div>

      {/* Timestamp */}
      <div className="shrink-0 text-right">
        <p className="font-inter text-xs text-white/30">{fmtTime(item.timestamp)}</p>
      </div>
    </motion.div>
  );
}

// ── Filter Pill ────────────────────────────────────────────────────────────────
function FilterPill({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-1.5 rounded-full text-xs font-poppins font-semibold border transition-all duration-200 ${
        active
          ? "bg-neonBlue/15 border-neonBlue/50 text-neonBlue shadow-neon"
          : "bg-white/3 border-white/10 text-white/40 hover:border-white/30 hover:text-white/70"
      }`}
    >
      {label}
    </button>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function HistoryPage() {
  const [data,       setData]       = useState<HistoryResponse | null>(null);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState<string | null>(null);
  const [filter,     setFilter]     = useState<string>("all");
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchHistory = useCallback(async (type?: string) => {
    setLoading(true);
    setError(null);
    try {
      const param = type && type !== "all" ? `?input_type=${type}&limit=50` : "?limit=50";
      const res   = await fetch(`${API_BASE}/api/detect/history${param}`);
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const json: HistoryResponse = await res.json();
      setData(json);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load history.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => { fetchHistory(filter); }, [fetchHistory, filter]);

  // Auto-refresh every 10s
  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(() => fetchHistory(filter), 10000);
    return () => clearInterval(id);
  }, [autoRefresh, filter, fetchHistory]);

  // ── Computed stats ──────────────────────────────────────────────────────────
  const stats = data?.stats;
  const total = stats?.total ?? 0;

  const textPct  = total ? Math.round((stats?.by_type.text  ?? 0) / total * 100) : 0;
  const imagePct = total ? Math.round((stats?.by_type.image ?? 0) / total * 100) : 0;
  const videoPct = total ? Math.round((stats?.by_type.video ?? 0) / total * 100) : 0;

  const threatTotal = (stats?.by_result.spam ?? 0) + (stats?.by_result.fake ?? 0);
  const safeTotal   = (stats?.by_result.ham  ?? 0) + (stats?.by_result.real ?? 0);

  return (
    <div className="min-h-screen pt-24 pb-16 px-6">
      <div className="max-w-5xl mx-auto">

        {/* ── Page Header ─────────────────────────────────────────────────── */}
        <motion.div
          className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-10"
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
        >
          <div>
            <p className="font-inter text-xs text-neonBlue uppercase tracking-widest mb-2">Live Monitor</p>
            <h1 className="font-poppins font-bold text-4xl text-white">
              Detection <span className="text-neon-gradient">History</span>
            </h1>
            <p className="font-inter text-white/40 text-sm mt-2">
              Real-time log of all detections run through AI Shield.
            </p>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-3 flex-wrap">
            {/* Auto-refresh toggle */}
            <button
              onClick={() => setAutoRefresh(v => !v)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-inter border transition-all ${
                autoRefresh
                  ? "bg-success/10 border-success/40 text-success"
                  : "bg-white/3 border-white/10 text-white/40 hover:border-white/30"
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${autoRefresh ? "bg-success animate-pulse" : "bg-white/20"}`} />
              {autoRefresh ? "Live" : "Auto-refresh"}
            </button>

            {/* Manual refresh */}
            <button
              onClick={() => fetchHistory(filter)}
              disabled={loading}
              className="px-4 py-2 rounded-full text-xs font-inter border border-white/10 text-white/40 hover:border-neonBlue/40 hover:text-neonBlue transition-all disabled:opacity-40"
            >
              {loading ? "⟳ Loading…" : "⟳ Refresh"}
            </button>
          </div>
        </motion.div>

        {/* ── Stats Row ───────────────────────────────────────────────────── */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            <StatCard value={total}       label="Total Scans"    icon="📊" accent="text-neon-gradient" />
            <StatCard value={threatTotal} label="Threats Found"  icon="⚠️" accent="text-danger"        />
            <StatCard value={safeTotal}   label="Safe Content"   icon="🛡️" accent="text-success"       />
            <StatCard value={`${total > 0 ? Math.round(safeTotal/total*100) : 0}%`} label="Safe Rate" icon="✨" accent="text-neonBlue" />
          </div>
        )}

        {/* ── Breakdown Cards ─────────────────────────────────────────────── */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">

            {/* By type donut */}
            <motion.div
              className="glass-card p-6"
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            >
              <p className="font-inter text-xs text-white/40 uppercase tracking-widest mb-5">By Input Type</p>
              <div className="flex items-center gap-6">
                <MiniDonut slices={[
                  { pct: textPct,  color: "#00D4FF" },
                  { pct: imagePct, color: "#7B61FF" },
                  { pct: videoPct, color: "#00FF9C" },
                ]} />
                <div className="flex flex-col gap-3 flex-1">
                  {[
                    { label: "Text",  count: stats.by_type.text,  pct: textPct,  color: "bg-neonBlue"   },
                    { label: "Image", count: stats.by_type.image, pct: imagePct, color: "bg-neonPurple" },
                    { label: "Video", count: stats.by_type.video, pct: videoPct, color: "bg-success"    },
                  ].map(({ label, count, pct, color }) => (
                    <div key={label}>
                      <div className="flex justify-between mb-1">
                        <span className="font-inter text-xs text-white/50">{label}</span>
                        <span className="font-poppins text-xs font-bold text-white">{count} <span className="text-white/30">({pct}%)</span></span>
                      </div>
                      <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                        <div className={`h-full ${color} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* By result */}
            <motion.div
              className="glass-card p-6"
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
            >
              <p className="font-inter text-xs text-white/40 uppercase tracking-widest mb-5">By Verdict</p>
              <div className="flex flex-col gap-4">
                {[
                  { label: "SPAM detected",  count: stats.by_result.spam, icon: "🚨", color: "bg-danger",    textColor: "text-danger"  },
                  { label: "FAKE detected",  count: stats.by_result.fake, icon: "🤖", color: "bg-danger",    textColor: "text-danger"  },
                  { label: "Safe text",      count: stats.by_result.ham,  icon: "✅", color: "bg-success",   textColor: "text-success" },
                  { label: "Authentic media",count: stats.by_result.real, icon: "🛡️", color: "bg-success",   textColor: "text-success" },
                ].map(({ label, count, icon, color, textColor }) => {
                  const pct = total ? Math.round(count / total * 100) : 0;
                  return (
                    <div key={label} className="flex items-center gap-3">
                      <span className="text-base w-5 text-center">{icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between mb-0.5">
                          <span className="font-inter text-xs text-white/50 truncate">{label}</span>
                          <span className={`font-poppins text-xs font-bold ${textColor}`}>{count}</span>
                        </div>
                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                          <div className={`h-full ${color}/60 rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          </div>
        )}

        {/* ── Filter pills ────────────────────────────────────────────────── */}
        <div className="flex items-center gap-2 flex-wrap mb-5">
          <span className="font-inter text-xs text-white/30 mr-1">Filter:</span>
          {["all", "text", "image", "video"].map(f => (
            <FilterPill key={f} label={f.charAt(0).toUpperCase() + f.slice(1)} active={filter === f} onClick={() => setFilter(f)} />
          ))}
          <span className="font-inter text-xs text-white/20 ml-auto">
            Showing last {data?.items.length ?? 0} results
          </span>
        </div>

        {/* ── Results List ────────────────────────────────────────────────── */}
        <AnimatePresence mode="wait">
          {loading && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-20 gap-4"
            >
              <div className="w-10 h-10 rounded-full border-2 border-neonBlue/30 border-t-neonBlue animate-spin" />
              <p className="font-inter text-sm text-white/30">Loading history…</p>
            </motion.div>
          )}

          {!loading && error && (
            <motion.div
              key="error"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="glass-card p-6 border-danger/20 text-center"
            >
              <p className="text-2xl mb-2">⚠️</p>
              <p className="font-inter text-sm text-danger">{error}</p>
              <p className="font-inter text-xs text-white/30 mt-1">Make sure the backend is running.</p>
            </motion.div>
          )}

          {!loading && !error && data?.items.length === 0 && (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="glass-card p-12 text-center"
            >
              <p className="text-4xl mb-4">📭</p>
              <p className="font-poppins font-semibold text-white/60 text-lg">No detections yet</p>
              <p className="font-inter text-sm text-white/30 mt-1">
                Run a detection and it will appear here instantly.
              </p>
            </motion.div>
          )}

          {!loading && !error && data && data.items.length > 0 && (
            <motion.div
              key="list"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex flex-col gap-3"
            >
              {data.items.map((item, i) => (
                <HistoryRow key={item.id} item={item} index={i} />
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Footer note ─────────────────────────────────────────────────── */}
        <motion.p
          className="font-inter text-xs text-white/15 text-center mt-10"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}
        >
          Detection logs are stored anonymously. Logged-in users have results linked to their account.
        </motion.p>
      </div>
    </div>
  );
}
