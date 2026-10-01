import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "NTRO Gen AI Platform",
  description: "Automated Content Transformation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50 text-slate-900`}>
        <div className="flex min-h-screen">
          <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col">
            <div className="p-6 font-bold text-xl text-white tracking-wider border-b border-slate-800">
              NTRO AI
            </div>
            <nav className="flex-1 p-4 space-y-2">
              <Link href="/" className="block p-3 rounded hover:bg-slate-800 hover:text-white transition">Dashboard</Link>
              <Link href="/projects" className="block p-3 rounded hover:bg-slate-800 hover:text-white transition">Projects</Link>
              <Link href="/history" className="block p-3 rounded hover:bg-slate-800 hover:text-white transition">History</Link>
              <Link href="/settings" className="block p-3 rounded hover:bg-slate-800 hover:text-white transition">Settings</Link>
            </nav>
            <div className="p-4 text-xs text-slate-500 border-t border-slate-800">
              v1.0.0
            </div>
          </aside>
          <main className="flex-1 flex flex-col h-screen overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
