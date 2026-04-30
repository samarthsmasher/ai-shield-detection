import type { Metadata } from "next";
import { Poppins, Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

// ── Task 5.2: Load Google Fonts & expose as CSS variables ──────────────────
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI Shield — Multi-Modal Content Detection",
  description:
    "Detect spam text, fake images, and deepfake videos instantly using advanced machine learning. Powered by TF-IDF, ResNet-50, and OpenCV.",
  keywords: ["AI detection", "spam filter", "deepfake detector", "image authenticity"],
  openGraph: {
    title: "AI Shield — Multi-Modal Content Detection",
    description: "Real-time spam text, fake image, and deepfake video detection using ML.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${poppins.variable} ${inter.variable}`}>
      <body className="font-inter antialiased bg-deepBlack text-white min-h-screen">
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
