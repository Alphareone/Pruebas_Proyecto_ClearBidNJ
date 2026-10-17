// Configuración de internacionalización (react-i18next) con los 4 idiomas.
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import de from "./locales/de.json";
import en from "./locales/en.json";
import es from "./locales/es.json";
import zh from "./locales/zh.json";

export const LANGS: [string, string][] = [
  ["en", "English"],
  ["es", "Español"],
  ["zh", "中文"],
  ["de", "Deutsch"],
];

const stored = localStorage.getItem("cb_lang") || "en";

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    es: { translation: es },
    zh: { translation: zh },
    de: { translation: de },
  },
  lng: stored,
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export function setLang(code: string) {
  localStorage.setItem("cb_lang", code);
  void i18n.changeLanguage(code);
}

export default i18n;
