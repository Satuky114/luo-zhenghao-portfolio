"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { Locale } from "@/i18n/routing";

// ============================================================
// Lazy-load message caches
// ============================================================
let cachedZH: Record<string, string> = {};
let cachedEN: Record<string, string> = {};
let loaded = false;

async function loadMessages() {
  if (loaded) return;
  cachedZH = flattenMessages((await import("../../../messages/zh.json")).default);
  cachedEN = flattenMessages((await import("../../../messages/en.json")).default);
  loaded = true;
}

function flattenMessages(
  obj: Record<string, unknown>,
  prefix = "",
): Record<string, string> {
  const result: Record<string, string> = {};
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (typeof value === "string") {
      result[fullKey] = value;
    } else if (Array.isArray(value)) {
      result[fullKey] = value.join(", ");
    } else if (typeof value === "object" && value !== null) {
      Object.assign(result, flattenMessages(value as Record<string, unknown>, fullKey));
    }
  }
  return result;
}

// ============================================================
// Context
// ============================================================
interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType>({
  locale: "zh",
  setLocale: () => {},
  t: (key: string) => key,
});

export function ClientIntlProvider({
  locale: initialLocale,
  children,
}: {
  locale: Locale;
  children: ReactNode;
}) {
  const [locale, setLocale] = useState<Locale>(initialLocale);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    loadMessages().then(() => setReady(true));
    document.documentElement.lang = initialLocale;
  }, [initialLocale]);

  const t = (key: string) => {
    const dict = locale === "en" ? cachedEN : cachedZH;
    return dict[key] ?? key;
  };

  const switchLocale = (l: Locale) => {
    setLocale(l);
    try { localStorage.setItem("locale", l); } catch {}
    document.documentElement.lang = l;
  };

  const ctx = { locale, setLocale: switchLocale, t };

  if (!ready) {
    return <div className="min-h-screen bg-black" />;
  }

  return (
    <I18nContext.Provider value={ctx}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
