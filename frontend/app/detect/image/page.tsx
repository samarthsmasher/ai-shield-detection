"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import UploadBox  from "@/components/UploadBox";
import Loader     from "@/components/Loader";
import ResultCard from "@/components/ResultCard";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

interface DetectionResult {
  result:     string;
  confidence: number;
  input_type: string;
  timestamp:  string;
}

// ── Tasks 6.6 & 6.7 — Image Detection Page ────────────────────────────────────
export default function ImageDetectPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [result,    setResult]    = useState<DetectionResult | null>(null);
  const [error,     setError]     = useState<string | null>(null);
  const [preview,   setPreview]   = useState<string | null>(null);

  // Task 6.7: on file select → FormData → POST /api/detect/image
  const handleFileSelect = useCallback(async (file: File) => {
    setIsLoading(true);
    setResult(null);
    setError(null);

    // Generate preview URL
    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/detect/image`, {
        method: "POST",
        body:   formData,
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
  }, []);

  function handleClear() {
    setResult(null);
    setError(null);
    setPreview(null);
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
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-neonPurple/10 text-3xl mb-4">
            🖼️
          </div>
          <h1 className="font-poppins font-bold text-3xl text-white mb-2">
            Image <span className="text-neon-gradient">Authenticity Check</span>
          </h1>
          <p className="font-inter text-white/50 text-sm">
            Upload an image to detect AI generation, deepfakes, or manipulation.
          </p>
        </motion.div>

        {/* ── Disclaimer banner ───────────────────────────────────────────── */}
        <motion.div
          className="mb-8 flex items-start gap-3 rounded-2xl border border-amber-500/20 bg-amber-500/5 px-4 py-3"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.05 }}
        >
          <span className="text-amber-400 text-lg mt-0.5">ⓘ</span>
          <div>
            <p className="font-inter text-xs font-semibold text-amber-400 mb-0.5">Statistical Analysis</p>
            <p className="font-inter text-xs text-white/40 leading-relaxed">
              Image analysis uses colour entropy, edge density, and texture variance heuristics.
              It reliably detects blank or clearly artificial images. For subtle AI-generated
              content, a deep-learning model trained on labelled data would be required.
            </p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-6"
        >
          {/* Task 6.6: UploadBox restricted to image types */}
          <UploadBox
            accept="image/jpeg,image/png,image/webp,image/gif,image/bmp"
            label="Drop your image here"
            subLabel="JPEG, PNG, WebP, GIF · Max 20 MB"
            icon="🖼️"
            onFileSelect={handleFileSelect}
            disabled={isLoading}
          />
        </motion.div>

        {/* ── Image preview ───────────────────────────────────────────────── */}
        <AnimatePresence>
          {preview && (
            <motion.div
              key="preview"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="glass-card p-3 mb-6 flex items-center justify-between gap-4"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={preview}
                alt="Preview"
                className="w-16 h-16 object-cover rounded-xl"
              />
              <p className="font-inter text-sm text-white/50 flex-1">
                Image loaded · {isLoading ? "Analysing…" : "Ready"}
              </p>
              <button
                onClick={handleClear}
                className="text-white/30 hover:text-white text-sm font-inter transition-colors"
              >
                ✕ Clear
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Loader / ResultCard / Error ─────────────────────────────────── */}
        <AnimatePresence mode="wait">
          {isLoading && (
            <motion.div key="loader" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <Loader label="Analysing image authenticity…" size="md" />
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
            <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="glass-card p-5 border-danger/30"
            >
              <p className="font-inter text-sm text-danger">⚠️ {error}</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Info note ───────────────────────────────────────────────────── */}
        <motion.p
          className="font-inter text-xs text-white/20 text-center mt-6"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
        >
          Your image is analysed locally and never stored permanently.
        </motion.p>
      </div>
    </div>
  );
}
