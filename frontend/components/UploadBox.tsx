"use client";

import { useCallback, useState } from "react";

interface UploadBoxProps {
  accept: string;           // e.g. "image/*" or "video/*"
  label: string;            // e.g. "Drop your image here"
  subLabel?: string;        // e.g. "JPEG, PNG, WebP up to 20MB"
  icon: React.ReactNode;
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

// ── Task 5.5 — UploadBox Component ──────────────────────────────────────────
export default function UploadBox({
  accept,
  label,
  subLabel,
  icon,
  onFileSelect,
  disabled = false,
}: UploadBoxProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName,   setFileName]   = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File | null) => {
      if (!file || disabled) return;
      setFileName(file.name);
      onFileSelect(file);
    },
    [disabled, onFileSelect]
  );

  // ── Drag handlers ─────────────────────────────────────────────────────────
  const onDragEnter = (e: React.DragEvent) => { e.preventDefault(); if (!disabled) setIsDragging(true); };
  const onDragLeave = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(false); };
  const onDragOver  = (e: React.DragEvent) => { e.preventDefault(); };
  const onDrop      = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0] ?? null;
    handleFile(file);
  };

  // ── Input handler ─────────────────────────────────────────────────────────
  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    handleFile(file);
    e.target.value = "";   // allow re-selecting the same file
  };

  return (
    <label
      htmlFor="upload-input"
      onDragEnter={onDragEnter}
      onDragLeave={onDragLeave}
      onDragOver={onDragOver}
      onDrop={onDrop}
      className={`
        relative group flex flex-col items-center justify-center gap-5
        min-h-[280px] w-full rounded-2xl cursor-pointer
        border-2 border-dashed transition-all duration-300
        bg-gradient-to-br from-surfaceHi/60 to-surface/80
        backdrop-blur-md
        ${isDragging
          ? "border-neonBlue shadow-neon bg-neonBlue/5 scale-[1.01]"
          : fileName
            ? "border-success/60 shadow-success"
            : "border-white/10 hover:border-neonBlue/50 hover:shadow-neon"
        }
        ${disabled ? "opacity-50 cursor-not-allowed" : ""}
      `}
    >
      {/* ── Animated corner accents ──────────────────────────────────────── */}
      <span className="absolute top-3 left-3 w-4 h-4 border-t-2 border-l-2 border-neonBlue/40 rounded-tl-md transition-all group-hover:border-neonBlue" />
      <span className="absolute top-3 right-3 w-4 h-4 border-t-2 border-r-2 border-neonBlue/40 rounded-tr-md transition-all group-hover:border-neonBlue" />
      <span className="absolute bottom-3 left-3 w-4 h-4 border-b-2 border-l-2 border-neonBlue/40 rounded-bl-md transition-all group-hover:border-neonBlue" />
      <span className="absolute bottom-3 right-3 w-4 h-4 border-b-2 border-r-2 border-neonBlue/40 rounded-br-md transition-all group-hover:border-neonBlue" />

      {/* ── Icon ─────────────────────────────────────────────────────────── */}
      <span
        className={`text-5xl transition-all duration-300 ${
          isDragging ? "scale-125 animate-float" : "group-hover:scale-110"
        }`}
      >
        {icon}
      </span>

      {/* ── Labels ───────────────────────────────────────────────────────── */}
      {fileName ? (
        <div className="text-center px-4">
          <p className="font-poppins font-semibold text-success text-sm">File selected ✓</p>
          <p className="font-inter text-white/60 text-xs mt-1 truncate max-w-[240px]">{fileName}</p>
          <p className="font-inter text-white/40 text-xs mt-2">Click to choose a different file</p>
        </div>
      ) : (
        <div className="text-center px-6">
          <p className="font-poppins font-semibold text-white text-base">{label}</p>
          <p className="font-inter text-white/50 text-sm mt-1">or click to browse</p>
          {subLabel && (
            <p className="font-inter text-white/30 text-xs mt-2">{subLabel}</p>
          )}
        </div>
      )}

      {/* ── Drag overlay label ───────────────────────────────────────────── */}
      {isDragging && (
        <div className="absolute inset-0 flex items-center justify-center rounded-2xl bg-neonBlue/5">
          <p className="font-poppins font-bold text-neonBlue text-lg">Drop it! ↓</p>
        </div>
      )}

      <input
        id="upload-input"
        type="file"
        accept={accept}
        className="sr-only"
        onChange={onChange}
        disabled={disabled}
      />
    </label>
  );
}
