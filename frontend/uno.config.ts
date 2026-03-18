import { defineConfig, presetUno } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
  ],
  theme: {
    colors: {
      'void': '#0a0a0f',
      'deep': '#111118',
      'surface': '#1a1a24',
      'gold-primary': '#c9a84c',
      'gold-bright': '#e8c56a',
      'gold-glow': 'rgba(201,168,76,0.15)',
      'cinnabar': '#c0392b',
      'indigo': '#2c5f8a',
      'text-primary': '#e8dcc8',
      'text-secondary': '#a09070',
    }
  },
  safelist: [
    'bg-void', 'bg-deep', 'bg-surface',
    'text-text-primary', 'text-text-secondary',
    'border-gold-primary',
  ]
})
