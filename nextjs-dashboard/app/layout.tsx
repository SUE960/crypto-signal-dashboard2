import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Crypto Signal Dashboard',
  description: '암호화폐 시그널 대시보드',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className="m-0 p-0 bg-gray-900 text-white antialiased">{children}</body>
    </html>
  )
}

