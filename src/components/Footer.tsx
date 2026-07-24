"use client";

import { useI18n } from "@/app/[locale]/ClientIntlProvider";

export function Footer() {
  const { t } = useI18n();

  return (
    <footer className="py-10 px-6 border-t border-border">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <p className="text-sm text-text-tertiary">{t("footer.copyright")}</p>
        <p className="text-sm font-medium">
          <span className="text-text-tertiary">{t("footer.builtWith")}</span>
        </p>
      </div>
    </footer>
  );
}
