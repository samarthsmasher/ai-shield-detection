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

// ── Tasks 6.8 & 6.9 — Video Detection Page ────────────────────────────────────
export default function VideoDetectPage() {
  const [isLoading,  setIsLoading]  = useState(false);
  const [result,     setResult]     = useState<DetectionResult | null>(null);
  const [error,      setError]      = useState<string | null>(null);
  const [fileName,   setFileName]   = useState<string | null>(null);
  const [fileSize,   setFileSize]   = useState<string | null>(null);
  const [progress,   setProgress]   = useState(0);   // fake progress for UX

  // Task 6.9: on file select → FormData → POST /api/detect/video
  const handleFileSelect = useCallback(async (file: File) => {
    setIsLoading(true);
    setResult(null);
    setError(null);
    setFileName(file.name);
    setFileSize((file.size / (1024 * 1024)).toFixed(1) + " MB");
    setProgress(0);

    // Fake progress animation while server processes
    const progressInterval = setInterval(() => {
      setProgress((p) => Math.min(p + Math.random() * 8, 85));
    }, 400);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/detect/video`, {
        method: "POST",
        body:   formData,
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `Server error ${res.status}`);
      }

      const data: DetectionResult = await res.json();
      setResult(data);
    } catch (err: unknown) {
      clearInterval(progressInterval);
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  function handleClear() {
    setResult(null);
    setError(null);
    setFileName(null);
    setFileSize(null);
    setProgress(0);
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
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-success/10 text-3xl mb-4">
            🎬
          </div>
          <h1 className="font-poppins font-bold text-3xl text-white mb-2">
            Video <span className="text-neon-gradient">Deepfake Detection</span>
          </h1>
          <p className="font-inter text-white/50 text-sm">
            Upload a video to scan it frame-by-frame for deepfake or synthetic content.
          </p>
        </motion.div>

        {/* ── Upload box ──────────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-6"
        >
          {/* Task 6.8: UploadBox restricted to video types */}
          <UploadBox
            accept="video/mp4,video/avi,video/quicktime,video/webm,video/x-matroska,image/gif"
            label="Drop your video here"
            subLabel="MP4, AVI, MOV, WebM · Max 200 MB"
            icon="🎬"
            onFileSelect={handleFileSelect}
            disabled={isLoading}
          />
        </motion.div>

        {/* ── File info + progress ─────────────────────────────────────────── */}
        <AnimatePresence>
          {(fileName && isLoading) && (
            <motion.div
              key="progress"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="glass-card p-5 mb-6"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-xl">🎬</span>
                  <div>
                    <p className="font-inter text-sm text-white truncate max-w-[180px]">{fileName}</p>
                    <p className="font-inter text-xs text-white/40">{fileSize}</p>
                  </div>
                </div>
                <span className="font-poppins text-sm font-semibold text-neonBlue">
                  {Math.round(progress)}%
                </span>
              </div>
              {/* Progress bar */}
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-neonBlue to-neonPurple"
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
              <p className="font-inter text-xs text-white/30 mt-2">
                Extracting frames and running inference…
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Loader / ResultCard / Error ─────────────────────────────────── */}
        <AnimatePresence mode="wait">
          {isLoading && (
            <motion.div key="loader" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <Loader label="Analysing video frames…" size="md" />
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
              <button
                onClick={handleClear}
                className="mt-4 w-full btn-ghost text-sm"
              >
                Analyse another video
              </button>
            </motion.div>
          )}

          {!isLoading && error && (
            <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="glass-card p-5 border-danger/30"
            >
              <p className="font-inter text-sm text-danger">⚠️ {error}</p>
              <button onClick={handleClear} className="mt-3 btn-ghost text-xs py-2">
                Try again
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Info tiles ──────────────────────────────────────────────────── */}
        {!result && !isLoading && (
          <motion.div
            className="grid grid-cols-2 gap-3 mt-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {[
              { icon: "⚡", label: "Frame-by-frame scan" },
              { icon: "🔒", label: "No permanent storage" },
              { icon: "🎯", label: "Majority-vote result"  },
              { icon: "📊", label: "Confidence scoring"   },
            ].map(({ icon, label }) => (
              <div key={label} className="flex items-center gap-2.5 glass-card px-4 py-3">
                <span className="text-base">{icon}</span>
                <span className="font-inter text-xs text-white/50">{label}</span>
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}
