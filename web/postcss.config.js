// postcss.config.js - FIXED for Tailwind v4
export default {
  plugins: {
    '@tailwindcss/postcss': {},  // ← Correct for v4
    autoprefixer: {},
  },
}