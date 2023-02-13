const defaultTheme = require('tailwindcss/defaultTheme')
const colors = require('tailwindcss/colors')

module.exports = {
  purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'media',
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      primary: colors.rose,
      pink: colors.rose,
      gray: colors.gray,
      green: colors.green,
      black: colors.black,
      white: colors.white,
      blue: colors.sky,
      red: colors.rose,
      yellow: colors.amber,
    },
    extend: {
      fontFamily: {
        mono: 'Roboto Mono,' + defaultTheme.fontFamily.mono
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
        '108': '27rem',
        '120': '30rem',
      }
    },
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/line-clamp'),
  ],
}
