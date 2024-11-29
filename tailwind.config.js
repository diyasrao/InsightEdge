module.exports = {
  content: [
    './src/**/*.{html,js}',  // This tells Tailwind to look for class names in files inside the src folder
  ],
  theme: {
    extend: {
      colors: {
        brandBlue: '#1E40AF',  // Custom color example
      },
      fontFamily: {
        sans: ['Inter', 'Helvetica', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
