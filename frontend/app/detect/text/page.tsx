"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Loader     from "@/components/Loader";
import ResultCard from "@/components/ResultCard";

// ── API base URL (falls back to localhost for dev) ────────────────────────────
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

interface DetectionResult {
  result:     string;
  confidence: number;
  input_type: string;
  timestamp:  string;
}

// ── Tasks 6.3, 6.4, 6.5 — Text Detection Page ────────────────────────────────
export default function TextDetectPage() {
  // Task 6.4: useState hooks
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result,    setResult]    = useState<DetectionResult | null>(null);
  const [error,     setError]     = useState<string | null>(null);

  const charLimit = 2000;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      // Task 6.4: wire submit to POST /api/detect/text
      const res = await fetch(`${API_BASE}/api/detect/text`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ text: inputText }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `Server error ${res.status}`);
      }

      const data: DetectionResult = await res.json();
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleClear() {
    setInputText("");
    setResult(null);
    setError(null);
  }

  return (
    <div className="min-h-screen pt-24 pb-16 px-6">
      <div className="max-w-2xl mx-auto">

        {/* ── Page header ─────────────────────────────────────────────────── */}
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-neonBlue/10 text-3xl mb-4">
            💬
          </div>
          <h1 className="font-poppins font-bold text-3xl text-white mb-2">
            Text <span className="text-neon-gradient">Spam Detection</span>
          </h1>
          <p className="font-inter text-white/50 text-sm">
            Paste any message, email, or SMS to check if it&apos;s spam.
          </p>
        </motion.div>

        {/* ── Input form ──────────────────────────────────────────────────── */}
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="glass-card p-6 mb-6"
          aria-label="Text detection form"
        >
          {/* Textarea */}
          <label htmlFor="text-input" className="block font-inter text-sm text-white/60 mb-2">
            Enter message to analyse
          </label>
          <div className="relative">
            <textarea
              id="text-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value.slice(0, charLimit))}
              placeholder="e.g. WINNER!! You've been selected for a FREE prize. Click here now..."
              rows={6}
              disabled={isLoading}
              className={`
                w-full resize-none rounded-xl px-4 py-3 text-sm font-inter
                bg-white/5 border text-white placeholder-white/20
                focus:outline-none focus:ring-2 focus:ring-neonBlue/40 focus:border-neonBlue/50
                transition-all duration-200
                ${isLoading ? "opacity-50 cursor-not-allowed" : "border-white/10 hover:border-white/20"}
              `}
            />
            {/* Char counter */}
            <span className={`absolute bottom-3 right-4 font-inter text-xs ${
              inputText.length > charLimit * 0.9 ? "text-danger" : "text-white/25"
            }`}>
              {inputText.length}/{charLimit}
            </span>
          </div>

          {/* Quick samples */}
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="font-inter text-xs text-white/30 self-center">Try:</span>
            {[
              { label: "Spam sample",   text: "URGENT! You've won £1,000,000! Claim your prize NOW at bit.ly/claimwin before it expires!" },
              { label: "Normal sample", text: "Hey, are we still meeting for coffee at 3pm? Let me know if you need to reschedule." },
            ].map(({ label, text }) => (
              <button
                key={label}
                type="button"
                onClick={() => { setInputText(text); setResult(null); setError(null); }}
                className="text-xs font-inter px-3 py-1 rounded-full border border-white/10 text-white/40 hover:text-neonBlue hover:border-neonBlue/30 transition-all"
              >
                {label}
              </button>
            ))}
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-3 mt-5">
            <button
              type="submit"
              id="detect-text-btn"
              disabled={!inputText.trim() || isLoading}
              className="btn-neon flex-1 text-sm py-3 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:hover:transform-none"
            >
              {isLoading ? "Analysing…" : "Detect Spam →"}
            </button>
            {(inputText || result) && (
              <button
                type="button"
                onClick={handleClear}
                className="btn-ghost text-sm py-3 px-5"
              >
                Clear
              </button>
            )}
          </div>
        </motion.form>

        {/* ── Task 6.5: Loader / ResultCard / Error ─────────────────────── */}
        <AnimatePresence mode="wait">
          {isLoading && (
            <motion.div
              key="loader"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <Loader label="Analysing your message…" size="md" />
            </motion.div>
          )}

          {!isLoading && result && (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
            >
              <ResultCard
                result={result.result}
                confidence={result.confidence}
                inputType={result.input_type}
                timestamp={result.timestamp}
              />
            </motion.div>
          )}

          {!isLoading && error && (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="glass-card p-5 border-danger/30"
            >
              <p className="font-inter text-sm text-danger">⚠️ {error}</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
