"use client";

import { motion } from "framer-motion";
import { Play, Eye, Newspaper } from "lucide-react";
import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { SectionWrapper } from "@/components/ui/SectionWrapper";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { AnimatedCounter } from "@/components/ui/AnimatedCounter";
import { useReducedMotion } from "@/hooks/useReducedMotion";

const STATS = [
  {
    value: 25,
    suffix: "",
    labelZh: "原创作品",
    labelEn: "Original Works",
    icon: <Play size={20} />,
  },
  {
    value: 117,
    suffix: "K+",
    labelZh: "单条最高浏览",
    labelEn: "Max Single Views",
    icon: <Eye size={20} />,
  },
  {
    value: 200,
    suffix: "万+",
    labelZh: "累计传播量",
    labelEn: "Total Reach",
    icon: <Newspaper size={20} />,
  },
];

const MEDIA_OUTLETS = [
  { zh: "人民网", en: "People's Daily" },
  { zh: "中国新闻网", en: "China News Network" },
  { zh: "封面新闻", en: "Cover News" },
];

export function ContentCreation() {
  const { t, locale } = useI18n();
  const reduced = useReducedMotion();

  const highlights = t("content.daozhonghua.highlights")
    .split(",")
    .map((s: string) => s.trim());

  return (
    <SectionWrapper id="content" orb={{ color: "#06B6D4", size: 320, position: "top-1/3 -right-16" }} gradientBottom>
      <SectionHeading
        number="03"
        title={t("content.title")}
        subtitle={t("content.subtitle")}
      />

      <div className="max-w-5xl mx-auto space-y-12">
        {/* Stats row */}
        <div className="grid grid-cols-3 gap-4 md:gap-8">
          {STATS.map((stat, i) => (
            <motion.div
              key={i}
              initial={reduced ? {} : { opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.12, duration: 0.5 }}
              className="text-center p-6 rounded-2xl border border-border bg-bg-elevated"
            >
              <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-accent/10 text-accent mb-3">
                {stat.icon}
              </span>
              <div className="text-3xl md:text-4xl text-text-primary mb-1">
                <AnimatedCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  duration={1.2}
                />
              </div>
              <p className="text-xs text-text-tertiary font-mono uppercase tracking-wider">
                {locale === "zh" ? stat.labelZh : stat.labelEn}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Main content card */}
        <motion.div
          initial={reduced ? {} : { opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="rounded-2xl border border-border bg-bg-elevated overflow-hidden"
        >
          {/* Video cover image */}
          <div className="aspect-video bg-bg-surface flex items-center justify-center border-b border-border overflow-hidden">
            <img
              src="/daozhonghua-cover.jpg"
              alt={locale === "zh" ? "道中华工作室视频截图" : "Dao Zhonghua Studio Video"}
              className="w-full h-full object-cover"
            />
          </div>

          <div className="p-6 md:p-8">
            <div className="flex items-start justify-between flex-wrap gap-4 mb-4">
              <div>
                <h3 className="text-xl md:text-2xl font-bold text-text-primary">
                  {t("content.daozhonghua.title")}
                </h3>
                <p className="text-sm text-accent mt-1">
                  {t("content.daozhonghua.role")} ·{" "}
                  {t("content.daozhonghua.period")}
                </p>
              </div>
            </div>

            <p className="text-text-secondary leading-relaxed mb-4">
              {t("content.daozhonghua.description")}
            </p>

            {/* Highlights badges */}
            <div className="flex flex-wrap gap-2 mb-5">
              {highlights.map((h: string, i: number) => (
                <motion.span
                  key={i}
                  initial={reduced ? {} : { opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.6 + i * 0.08, type: "spring", stiffness: 400, damping: 25 }}
                  className="px-3 py-1 rounded-full text-xs font-medium border border-accent/30 bg-accent/5 text-accent"
                >
                  {h}
                </motion.span>
              ))}
            </div>

            {/* Media outlet logos */}
            <div className="flex items-center gap-6 pt-4 border-t border-border">
              <span className="text-xs font-mono text-text-tertiary uppercase tracking-wider">
                {locale === "zh" ? "媒体转载" : "Featured on"}
              </span>
              {MEDIA_OUTLETS.map((outlet, i) => (
                <motion.span
                  key={i}
                  initial={reduced ? {} : { opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  whileHover={{ y: -2, color: "var(--accent)" }}
                  transition={{ delay: 0.8 + i * 0.12 }}
                  className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors cursor-default"
                >
                  {locale === "zh" ? outlet.zh : outlet.en}
                </motion.span>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </SectionWrapper>
  );
}
