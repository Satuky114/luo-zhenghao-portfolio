"use client";

import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { GitFork, Video, Camera, Globe } from "lucide-react";

const SOCIAL_LINKS = [
  {
    icon: <GitFork size={18} />,
    label: "GitHub",
    href: "https://github.com/satuky114",
  },
  {
    icon: <Video size={18} />,
    label: "bilibili",
    href: "#",
  },
  {
    icon: <Camera size={18} />,
    label: "小红书",
    href: "#",
  },
  {
    icon: <Globe size={18} />,
    label: "Cover News",
    href: "https://www.thecover.cn/video/Lk/1Scm5Z8mH90qSdq8Jkw==",
  },
];

export function Footer() {
  const { t, locale } = useI18n();

  return (
    <footer className="py-12 px-6 border-t border-border bg-bg-primary">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        {/* Social links */}
        <div className="flex items-center gap-4">
          {SOCIAL_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              target={link.href.startsWith("http") ? "_blank" : undefined}
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-text-tertiary hover:text-accent transition-colors"
              title={link.label}
            >
              {link.icon}
              <span className="text-xs font-mono hidden sm:inline">{link.label}</span>
            </a>
          ))}
        </div>

        {/* Copyright */}
        <p className="text-xs text-text-tertiary font-mono">
          {t("footer.copyright")} &mdash;{" "}
          <span className="text-text-secondary">{t("footer.builtWith")}</span>
        </p>
      </div>
    </footer>
  );
}
