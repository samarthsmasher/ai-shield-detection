"use client";

import { useState, useRef } from "react";
import { Menu, X } from "lucide-react";

const VIDEO_URL =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_091828_e240eb17-6edc-4129-ad9d-98678e3fd238.mp4";

const NAV_LINKS = [
  { label: "Start",    href: "#start"    },
  { label: "Story",    href: "#story"    },
  { label: "Rates",    href: "#rates"    },
  { label: "Benefits", href: "#benefits" },
  { label: "FAQ",      href: "#faq"      },
];

export default function SkyEliteHero() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [videoError, setVideoError] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  return (
    <div className="min-h-screen" style={{ fontFamily: "'Inter', system-ui, sans-serif", background: "#F0F2F5" }}>
      {/* ── Hero Section ──────────────────────────────────────────────────── */}
      <section className="relative h-screen overflow-hidden">

        {/* ── Fallback gradient (shows if video fails to load) ─────────── */}
        <div
          className="absolute inset-0"
          style={{
            background: videoError
              ? "linear-gradient(135deg, #1a2229 0%, #202A36 40%, #2d3748 70%, #1a2229 100%)"
              : "#0a0a0a",
          }}
        />

        {/* ── Video Background ──────────────────────────────────────────── */}
        {!videoError && (
          <video
            ref={videoRef}
            className="absolute inset-0 w-full h-full object-cover"
            autoPlay
            muted
            loop
            playsInline
            preload="auto"
            aria-hidden="true"
            onError={() => setVideoError(true)}
            onCanPlay={() => {
              // Force play in case autoplay was deferred
              videoRef.current?.play().catch(() => setVideoError(true));
            }}
          >
            <source src={VIDEO_URL} type="video/mp4" />
          </video>
        )}

        {/* ── Overlay: darkens video slightly for text legibility ────────── */}
        <div
          className="absolute inset-0"
          style={{
            background: videoError
              ? "rgba(0,0,0,0.0)"
              : "rgba(0,0,0,0.18)",
          }}
        />

        {/* ── Content wrapper ───────────────────────────────────────────── */}
        <div className="relative h-full flex flex-col">

          {/* ── Navigation ──────────────────────────────────────────────── */}
          <nav className="w-full max-w-7xl mx-auto px-8 py-6">
            <div className="flex items-center justify-between">

              {/* Brand */}
              <span
                className="text-2xl font-semibold text-gray-900 tracking-tight select-none"
                aria-label="SkyElite"
              >
                SkyElite
              </span>

              {/* Desktop links */}
              <ul className="hidden md:flex items-center gap-8" role="list">
                {NAV_LINKS.map(({ label, href }) => (
                  <li key={label}>
                    <a
                      href={href}
                      className="text-sm font-medium text-gray-900 hover:text-gray-700 transition-colors duration-200"
                    >
                      {label}
                    </a>
                  </li>
                ))}
              </ul>

              {/* Mobile hamburger */}
              <button
                id="sky-mobile-menu-btn"
                className="md:hidden p-2 rounded-lg text-gray-900 hover:bg-black/5 transition-colors"
                onClick={() => setMenuOpen(!menuOpen)}
                aria-label="Toggle navigation"
                aria-expanded={menuOpen}
              >
                {menuOpen ? <X size={22} /> : <Menu size={22} />}
              </button>
            </div>

            {/* Mobile dropdown */}
            <div
              className={`
                md:hidden overflow-hidden transition-all duration-300 ease-in-out
                ${menuOpen ? "max-h-72 opacity-100 mt-4" : "max-h-0 opacity-0"}
              `}
            >
              <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-xl px-4 py-3">
                <ul className="flex flex-col gap-1" role="list">
                  {NAV_LINKS.map(({ label, href }) => (
                    <li key={label}>
                      <a
                        href={href}
                        onClick={() => setMenuOpen(false)}
                        className="block px-4 py-3 rounded-xl text-sm font-medium text-gray-900 hover:bg-gray-100 transition-colors duration-200"
                      >
                        {label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </nav>

          {/* ── Main Hero Content ──────────────────────────────────────────── */}
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center px-6" style={{ marginTop: "-16rem" }}>

              {/* Label */}
              <p
                className="text-sm font-semibold tracking-wider uppercase mb-4"
                style={{ letterSpacing: "0.15em", color: videoError ? "#9CA3AF" : "rgba(255,255,255,0.75)" }}
              >
                PRIVATE JETS
              </p>

              {/* Heading */}
              <div className="mb-6" aria-label="Premium. Accessible.">
                <h1
                  className="text-6xl md:text-7xl lg:text-8xl font-normal leading-none tracking-tighter"
                  style={{ lineHeight: 1, color: videoError ? "#6B7280" : "rgba(255,255,255,0.55)" }}
                >
                  Premium.
                </h1>
                <h2
                  className="text-6xl md:text-7xl lg:text-8xl font-normal leading-none tracking-tighter"
                  style={{
                    color: videoError ? "#202A36" : "#FFFFFF",
                    marginTop: "-12px",
                    lineHeight: 1,
                  }}
                >
                  Accessible.
                </h2>
              </div>

              {/* Subtitle */}
              <p className="text-lg md:text-xl mb-8 max-w-2xl mx-auto" style={{ color: videoError ? "#6B7280" : "rgba(255,255,255,0.7)" }}>
                Your dedication deserves recognition.
              </p>

              {/* CTA Buttons */}
              <div className="flex items-center justify-center gap-4 flex-wrap">
                <a
                  id="sky-discover-btn"
                  href="#start"
                  className="
                    px-6 py-2.5 rounded-full bg-gray-300 text-gray-800 font-medium text-sm
                    hover:bg-gray-400 transition-colors duration-200 cursor-pointer
                    inline-block no-underline
                  "
                >
                  Discover
                </a>
                <a
                  id="sky-book-btn"
                  href="#book"
                  className="
                    px-6 py-2.5 rounded-full text-white font-medium text-sm
                    transition-colors duration-200 cursor-pointer
                    inline-block no-underline
                  "
                  style={{ backgroundColor: "#202A36" }}
                  onMouseEnter={(e) =>
                    ((e.currentTarget as HTMLElement).style.backgroundColor = "#1a2229")
                  }
                  onMouseLeave={(e) =>
                    ((e.currentTarget as HTMLElement).style.backgroundColor = "#202A36")
                  }
                >
                  Book Now
                </a>
              </div>
            </div>
          </div>

        </div>
      </section>
    </div>
  );
}
