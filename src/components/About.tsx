"use client";

import { motion } from "framer-motion";
import { MapPin, Zap, GraduationCap, Radio } from "lucide-react";
import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { SectionWrapper } from "@/components/ui/SectionWrapper";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { useReducedMotion } from "@/hooks/useReducedMotion";

const INFO_ITEMS = [
  { key: "about.age", icon: <Zap size={16} /> },
  { key: "about.location", icon: <MapPin size={16} /> },
  { key: "about.school", icon: <GraduationCap size={16} /> },
  { key: "about.major", icon: <Radio size={16} /> },
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
    <SectionWrapper id="about" gradientBottom className="md:py-48 py-32">
      <SectionHeading title={t("about.title")} />

      {/* Asymmetric layout: left-aligned bio, right-anchored info */}
      <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-12 md:gap-20 items-start">
        {/* Left: Bio (2/3) */}
        <div className="md:col-span-2 relative">
          {/* Giant quote mark */}
          <span
            className="absolute -top-16 -left-3 text-[14rem] leading-none font-display text-text-primary select-none pointer-events-none"
            style={{ opacity: 0.025 }}
          >
            &ldquo;
          </span>

          <div className="relative space-y-4">
            {[t("about.bio1"), t("about.bio2"), t("about.bio3")].map(
              (text, i) => (
                <motion.p
                  key={i}
                  initial={reduced ? {} : { opacity: 0, y: 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{
                    delay: 0.15 + i * 0.1,
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

          {/* Fun tags inline with bio */}
          <div className="flex flex-wrap gap-2 mt-6">
            {FUN_TAGS.map((tag, i) => (
              <span
                key={i}
                className="inline-flex items-center px-3 py-1.5 rounded-full border border-border/60 bg-bg-elevated/60 text-sm text-text-secondary cursor-default"
              >
                {locale === "zh" ? tag.labelZh : tag.labelEn}
              </span>
            ))}
          </div>
        </div>

        {/* Right: Info cards (1/3) — compact */}
        <div className="space-y-3">
          {INFO_ITEMS.map(({ key, icon }, i) => (
            <motion.div
              key={key}
              initial={reduced ? {} : { opacity: 0, x: 12 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{
                delay: 0.25 + i * 0.08,
                duration: 0.4,
                ease: "easeOut",
              }}
              className="flex items-center gap-3 p-3.5 rounded-xl border border-border/50 bg-bg-elevated/40 transition-colors hover:border-border"
            >
              <span className="flex-shrink-0 w-8 h-8 rounded-lg bg-accent/10 text-accent flex items-center justify-center">
                {icon}
              </span>
              <p className="font-mono text-sm text-text-secondary uppercase tracking-wider">
                {t(key)}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </SectionWrapper>
  );
}
