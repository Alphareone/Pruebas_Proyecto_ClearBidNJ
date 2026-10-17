/** @type {import('tailwindcss').Config} */
// Los colores referencian variables CSS (definidas en index.css) para que el
// modo oscuro funcione intercambiando los tokens en :root / .dark.
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "var(--ink)",
        ink2: "var(--ink2)",
        line: "var(--line)",
        line2: "var(--line2)",
        paper: "var(--paper)",
        wash: "var(--wash)",
        chip: "var(--chip)",
        accent: "var(--accent)",
        accent2: "var(--accent2)",
        green: "var(--green)",
        "green-bg": "var(--green-bg)",
        "green-tx": "var(--green-tx)",
        amber: "var(--amber)",
        "amber-bg": "var(--amber-bg)",
        "amber-tx": "var(--amber-tx)",
        red: "var(--red)",
        "red-bg": "var(--red-bg)",
        "red-tx": "var(--red-tx)",
      },
      fontFamily: {
        sans: ["'Segoe UI'", "system-ui", "-apple-system", "Roboto", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
