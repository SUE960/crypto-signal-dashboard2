// import type { Metadata } from 'next'
// import './globals.css'

// export const metadata: Metadata = {
//   title: 'Crypto Signal Dashboard',
//   description: '암호화폐 시그널 대시보드',
// }

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode
// }) {
//   return (
//     <html lang="ko" className="h-full">
//       <body className="m-0 p-0 bg-gray-900 text-white antialiased min-h-screen">{children}</body>
//     </html>
//   )
// }

import './globals.css';
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Crypto Signal Dashboard',
  description: 'Real-time Market Intelligence',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-white">
        {/* Header Navigation */}
        <header className="border-b border-gray-800 p-4">
          <nav className="flex gap-6 text-sm">
            <Link href="/" className="hover:text-blue-400">
              Home
            </Link>
            {/* 🔥 여기에 Community 메뉴 추가 */}
            <Link href="/community" className="hover:text-blue-400">
              Community
            </Link>
            <a
              href="https://graph-visualization2.vercel.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-400"
            >
              Whale Transaction
            </a>
            <a
              href="https://whale-arbitrage-qwodzy8wpnhpgxaxt23rj8.streamlit.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-400"
            >
              Arbitrage Simulation
            </a>
          </nav>
        </header>

        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}
