"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";

// ── Icons (inline SVG to avoid extra deps) ──────────────────────────────────
const ShieldIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.35C17.25 22.15 21 17.25 21 12V7L12 2z"
      fill="url(#shieldGrad)"
    />
    <path
      d="M9 12l2 2 4-4"
      stroke="#0A0A0A"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <defs>
      <linearGradient id="shieldGrad" x1="3" y1="2" x2="21" y2="23" gradientUnits="userSpaceOnUse">
        <stop stopColor="#00D4FF" />
        <stop offset="1" stopColor="#7B61FF" />
      </linearGradient>
    </defs>
  </svg>
);

const navLinks = [
  { href: "/",              label: "Home"    },
  { href: "/detect/text",  label: "Text"    },
  { href: "/detect/image", label: "Image"   },
  { href: "/detect/video", label: "Video"   },
];

// ── Task 5.4 — Navbar Component ─────────────────────────────────────────────
export default function Navbar() {
  const pathname    = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-surface/80 backdrop-blur-xl border-b border-white/5 shadow-lg"
          : "bg-transparent"
      }`}
    >
      <nav className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

        {/* ── Logo ─────────────────────────────────────────────────────────── */}
        <Link
          href="/"
          className="flex items-center gap-2.5 group"
          aria-label="AI Shield Home"
        >
          <span className="transition-transform duration-300 group-hover:scale-110">
            <ShieldIcon />
          </span>
          <span className="font-poppins font-700 text-xl tracking-tight">
            <span className="text-neon-gradient">AI</span>
            <span className="text-white ml-1">Shield</span>
          </span>
        </Link>

        {/* ── Desktop nav links ─────────────────────────────────────────────── */}
        <ul className="hidden md:flex items-center gap-1" role="list">
          {navLinks.map(({ href, label }) => {
            const active = pathname === href;
            return (
              <li key={href}>
                <Link
                  href={href}
                  className={`relative px-4 py-2 rounded-full text-sm font-medium font-inter transition-all duration-200
                    ${active
                      ? "text-neonBlue bg-neonBlue/10"
                      : "text-white/70 hover:text-white hover:bg-white/5"
                    }`}
                >
                  {label}
                  {active && (
                    <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-neonBlue" />
                  )}
                </Link>
              </li>
            );
          })}
        </ul>

        {/* ── CTA button ───────────────────────────────────────────────────── */}
        <div className="hidden md:flex items-center gap-3">
          <Link href="/detect/text" className="btn-neon text-sm py-2 px-5">
            Try It Free
          </Link>
        </div>

        {/* ── Mobile hamburger ─────────────────────────────────────────────── */}
        <button
          className="md:hidden flex flex-col gap-1.5 p-2"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
        >
          <span className={`block w-5 h-0.5 bg-white transition-all duration-300 ${menuOpen ? "rotate-45 translate-y-2" : ""}`} />
          <span className={`block w-5 h-0.5 bg-white transition-all duration-300 ${menuOpen ? "opacity-0" : ""}`} />
          <span className={`block w-5 h-0.5 bg-white transition-all duration-300 ${menuOpen ? "-rotate-45 -translate-y-2" : ""}`} />
        </button>
      </nav>

      {/* ── Mobile dropdown ──────────────────────────────────────────────────── */}
      <div
        className={`md:hidden overflow-hidden transition-all duration-300 ${
          menuOpen ? "max-h-72 opacity-100" : "max-h-0 opacity-0"
        } bg-surface/95 backdrop-blur-xl border-b border-white/5`}
      >
        <ul className="px-6 py-4 flex flex-col gap-2" role="list">
          {navLinks.map(({ href, label }) => (
            <li key={href}>
              <Link
                href={href}
                onClick={() => setMenuOpen(false)}
                className={`block px-4 py-3 rounded-xl text-sm font-medium font-inter transition-all ${
                  pathname === href
                    ? "text-neonBlue bg-neonBlue/10"
                    : "text-white/70 hover:text-white hover:bg-white/5"
                }`}
              >
                {label}
              </Link>
            </li>
          ))}
          <li>
            <Link href="/detect/text" onClick={() => setMenuOpen(false)} className="btn-neon block text-center text-sm mt-2">
              Try It Free
            </Link>
          </li>
        </ul>
      </div>
    </header>
  );
}
