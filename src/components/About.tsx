"use client";

import { motion } from "framer-motion";
import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { SectionWrapper } from "@/components/ui/SectionWrapper";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { useReducedMotion } from "@/hooks/useReducedMotion";

const INFO_ITEMS = [
  { key: "about.age", icon: "⚡" },
  { key: "about.location", icon: "📍" },
  { key: "about.school", icon: "🎓" },
  { key: "about.major", icon: "📡" },
];

const FUN_TAGS = [
  { labelZh: "🏐 排球运动员", labelEn: "🏐 Volleyball Athlete" },
  { labelZh: "📷 摄影爱好者", labelEn: "📷 Photographer" },
  { labelZh: "🎙️ 双语主播", labelEn: "🎙️ Bilingual Anchor" },
];

export function About() {
  const { t, locale } = useI18n();
  const reduced = useReducedMotion();

  return (
    <SectionWrapper id="about" orb={{ color: "var(--accent)", size: 350, position: "top-0 -right-32" }} gradientBottom>
      <SectionHeading number="01" title={t("about.title")} />

      <div className="grid md:grid-cols-2 gap-16 items-start">
        {/* Left: Bio */}
        <div className="relative">
          {/* Giant quote mark */}
          <span
            className="absolute -top-12 -left-2 text-[12rem] leading-none font-serif text-text-primary select-none pointer-events-none"
            style={{ opacity: 0.03 }}
          >
            &ldquo;
          </span>

          <div className="relative space-y-5">
            {[t("about.bio1"), t("about.bio2"), t("about.bio3")].map(
              (text, i) => (
                <motion.p
                  key={i}
                  initial={reduced ? {} : { opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{
                    delay: 0.2 + i * 0.12,
                    duration: 0.5,
                    ease: "easeOut",
                  }}
                  className="text-base md:text-lg text-text-secondary leading-relaxed"
                >
                  {text}
                </motion.p>
              ),
            )}
          </div>
        </div>

        {/* Right: Avatar + Info grid + fun tags */}
        <div className="space-y-6">
          {/* Avatar photo */}
          <motion.div
            initial={reduced ? {} : { opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.15, duration: 0.5, ease: "easeOut" }}
            className="relative mx-auto w-40 h-40 md:w-48 md:h-48 rounded-2xl overflow-hidden border-2 border-border group"
          >
            <img
              src="/avatar.jpg"
              alt={locale === "zh" ? "罗政皓" : "Luo Zhenghao"}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            {/* Subtle overlay glow on hover */}
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
              style={{ boxShadow: "inset 0 0 30px var(--accent-glow)" }}
            />
          </motion.div>

          {/* 4 info cards */}
          <div className="grid grid-cols-2 gap-3">
            {INFO_ITEMS.map(({ key, icon }, i) => (
              <motion.div
                key={key}
                initial={reduced ? {} : { opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{
                  delay: 0.3 + i * 0.1,
                  duration: 0.5,
                  ease: "easeOut",
                }}
                whileHover={{ y: -2, borderColor: "var(--accent)" }}
                className="p-4 rounded-xl border border-border bg-bg-elevated transition-colors"
              >
                <span className="text-lg">{icon}</span>
                <p className="mt-2 font-mono text-sm text-text-tertiary uppercase tracking-wider">
                  {t(key)}
                </p>
              </motion.div>
            ))}
          </div>

          {/* Fun tags */}
          <div className="flex flex-wrap gap-2">
            {FUN_TAGS.map((tag, i) => (
              <motion.span
                key={i}
                initial={reduced ? {} : { opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                whileHover={{ rotate: 2, scale: 1.05 }}
                transition={{
                  delay: 0.7 + i * 0.08,
                  type: "spring",
                  stiffness: 400,
                  damping: 25,
                }}
                className="inline-flex items-center px-3 py-1.5 rounded-full border border-border bg-bg-surface text-sm text-text-secondary hover:text-text-primary hover:bg-bg-elevated cursor-default transition-colors"
              >
                {locale === "zh" ? tag.labelZh : tag.labelEn}
              </motion.span>
            ))}
          </div>
        </div>
      </div>
    </SectionWrapper>
  );
}
