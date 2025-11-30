/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  // CSS 최적화 보장
  swcMinify: true,
}

module.exports = nextConfig


