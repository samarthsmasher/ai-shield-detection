"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import DetectionModeCard from "@/components/DetectionModeCard";

// ── Animation variants ────────────────────────────────────────────────────────
const fadeUp = {
  hidden:  { opacity: 0, y: 20 },
  visible: (i: number = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.4, delay: i * 0.08, ease: "easeOut" as const },
  }),
};


const detectionModes = [
  {
    href:        "/detect/text",
    icon:        "💬",
    title:       "Text Detection",
    description: "Instantly classify SMS, emails, and messages as spam or legitimate using our TF-IDF + Naive Bayes model trained on 5,500+ samples.",
    accent:      "blue"  as const,
    badge:       "98.5% Accurate",
  },
  {
    href:        "/detect/image",
    icon:        "🖼️",
    title:       "Image Detection",
    description: "Detect AI-generated, deepfake, or manipulated images. Upload any JPEG, PNG, or WebP and get an authenticity score instantly.",
    accent:      "purple" as const,
    badge:       "Most Popular",
  },
  {
    href:        "/detect/video",
    icon:        "🎬",
    title:       "Video Detection",
    description: "Analyse video files frame-by-frame for deepfake indicators. Supports MP4, AVI, MOV and other common formats.",
    accent:      "success" as const,
  },
];

const stats = [
  { value: "98.5%",   label: "Text Accuracy"     },
  { value: "5,572",   label: "Training Samples"  },
  { value: "<1s",     label: "Response Time"      },
  { value: "3",       label: "Detection Modes"    },
];

// ── Tasks 6.1 & 6.2 — Landing Page ───────────────────────────────────────────
export default function HomePage() {
  return (
    <div className="relative overflow-hidden">

      {/* ── Ambient glow blobs ───────────────────────────────────────────── */}
      <div className="fixed inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neonBlue/5 rounded-full blur-3xl" />
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-neonPurple/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/2 w-72 h-72 bg-success/3 rounded-full blur-3xl" />
      </div>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ── HERO SECTION ─────────────────────────────────────────────────── */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <section
        className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-20 pb-16 text-center"
        aria-labelledby="hero-heading"
      >
        {/* Badge */}
        <motion.div
          variants={fadeUp} initial="hidden" animate="visible" custom={0}
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-neonBlue/30 bg-neonBlue/5 text-neonBlue text-xs font-poppins font-semibold tracking-widest uppercase mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-neonBlue animate-pulse" />
            Multi-Modal AI Detection System
          </span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          id="hero-heading"
          className="font-poppins font-bold text-5xl sm:text-6xl md:text-7xl leading-tight max-w-4xl mb-6"
          variants={fadeUp} initial="hidden" animate="visible" custom={1}
        >
          Detect{" "}
          <span className="text-neon-gradient">Spam & Fakes</span>
          <br />
          <span className="text-white">Before They Reach You</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          className="font-inter text-lg sm:text-xl text-white/55 max-w-2xl leading-relaxed mb-10"
          variants={fadeUp} initial="hidden" animate="visible" custom={2}
        >
          AI Shield analyses text messages, images, and videos in real-time using
          machine learning to identify spam, deepfakes, and AI-generated content
          with industry-leading accuracy.
        </motion.p>

        {/* CTA buttons */}
        <motion.div
          className="flex flex-wrap items-center justify-center gap-4 mb-16"
          variants={fadeUp} initial="hidden" animate="visible" custom={3}
        >
          <Link href="/detect/text" className="btn-neon text-base px-8 py-3.5">
            Start Detecting Free →
          </Link>
          <a
            href="#how-it-works"
            className="btn-ghost text-base px-7 py-3.5"
          >
            How it works
          </a>
        </motion.div>

        {/* Stats row */}
        <motion.div
          className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-8 max-w-2xl w-full"
          variants={fadeUp} initial="hidden" animate="visible" custom={4}
        >
          {stats.map(({ value, label }) => (
            <div key={label} className="text-center">
              <p className="font-poppins font-bold text-2xl text-neon-gradient">{value}</p>
              <p className="font-inter text-xs text-white/40 mt-1">{label}</p>
            </div>
          ))}
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1.5"
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        >
          <span className="font-inter text-xs text-white/25">scroll</span>
          <div className="w-px h-8 bg-gradient-to-b from-white/20 to-transparent" />
        </motion.div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ── HOW IT WORKS ─────────────────────────────────────────────────── */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <section id="how-it-works" className="py-20 px-6" aria-labelledby="how-heading">
        <div className="max-w-5xl mx-auto">
          <motion.div
            className="text-center mb-14"
            variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={0}
          >
            <p className="font-inter text-xs text-neonBlue uppercase tracking-widest mb-3">The Process</p>
            <h2 id="how-heading" className="font-poppins font-bold text-3xl sm:text-4xl text-white">
              How AI Shield Works
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[
              { step: "01", icon: "📤", title: "Upload Content",   desc: "Drop your text, image, or video file into the detector." },
              { step: "02", icon: "🤖", title: "ML Analysis",      desc: "Our models analyse patterns, features, and anomalies in milliseconds." },
              { step: "03", icon: "📊", title: "Instant Results",  desc: "Get a clear verdict with confidence score and detailed explanation." },
            ].map(({ step, icon, title, desc }, i) => (
              <motion.div
                key={step}
                className="glass-card p-7 text-center relative"
                variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={i}
              >
                <span className="absolute top-4 right-5 font-poppins font-bold text-4xl text-white/5">{step}</span>
                <div className="text-4xl mb-4">{icon}</div>
                <h3 className="font-poppins font-semibold text-white text-base mb-2">{title}</h3>
                <p className="font-inter text-sm text-white/50 leading-relaxed">{desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ── DETECTION MODE CARDS — Task 6.2 ──────────────────────────────── */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <section className="py-20 px-6" aria-labelledby="modes-heading">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="text-center mb-14"
            variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={0}
          >
            <p className="font-inter text-xs text-neonBlue uppercase tracking-widest mb-3">Choose a Mode</p>
            <h2 id="modes-heading" className="font-poppins font-bold text-3xl sm:text-4xl text-white mb-4">
              Three Detection Modes
            </h2>
            <p className="font-inter text-white/50 max-w-xl mx-auto">
              Select the type of content you want to analyse and get results in seconds.
            </p>
          </motion.div>

          {/* Responsive 3-column grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {detectionModes.map((mode, i) => (
              <motion.div
                key={mode.href}
                className="h-full"
                variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={i}
              >
                <DetectionModeCard {...mode} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ── FOOTER ────────────────────────────────────────────────────────── */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <footer className="border-t border-white/5 py-8 px-6 text-center">
        <p className="font-inter text-sm text-white/25">
          © 2026 AI Shield — Multi-Modal Content Detection System
        </p>
        <p className="font-inter text-xs text-white/15 mt-1">
          Built with FastAPI · Next.js · MongoDB · scikit-learn
        </p>
      </footer>
    </div>
  );
}
