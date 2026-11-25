/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        eduspark: {
          primary: '#2563EB',      // Electric Blue
          primaryDeep: '#1D4ED8',  // Deep Electric Blue
          secondary: '#7C3AED',    // Royal Violet
          accent: '#F59E0B',       // Warm Spark Yellow
          accentSoft: '#FEF3C7',   // Soft Yellow Tint
          bgSoft: '#F8FAFC',       // Soft White Cloud
          bgIce: '#EFF6FF',        // Very Light Blue
        },
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.25rem',
      },
    },
  },
  plugins: [],
};

