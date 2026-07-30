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
  { zh: "上级团组织", en: "League Org" },
];

export function ContentCreation() {
  const { t, locale } = useI18n();
  const reduced = useReducedMotion();

  const highlights = t("content.daozhonghua.highlights")
    .split(",")
    .map((s: string) => s.trim());

  return (
    <SectionWrapper id="content" gradientBottom className="md:py-48 py-32">
      <SectionHeading
        title={t("content.title")}
        subtitle={t("content.subtitle")}
      />

      <div className="max-w-6xl mx-auto space-y-12">
        {/* Stats row */}
        <div className="grid grid-cols-3 gap-4 md:gap-8">
          {STATS.map((stat, i) => (
            <div
              key={i}
              className="text-center p-6 md:p-8 rounded-2xl border border-border bg-bg-elevated"
            >
              <span className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-accent/10 text-accent mb-4">
                {stat.icon}
              </span>
              <div className="font-display text-3xl md:text-5xl text-text-primary mb-1">
                <AnimatedCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  duration={1.2}
                />
              </div>
              <p className="text-xs text-text-tertiary font-mono uppercase tracking-wider">
                {locale === "zh" ? stat.labelZh : stat.labelEn}
              </p>
            </div>
          ))}
        </div>

        {/* Main content card */}
        <motion.div
          initial={reduced ? {} : { opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="rounded-2xl border border-border bg-bg-elevated overflow-hidden"
        >
          {/* Video cover with play button */}
          <a
            href="https://www.thecover.cn/video/Lk/1Scm5Z8mH90qSdq8Jkw=="
            target="_blank"
            rel="noopener noreferrer"
            className="block relative aspect-video bg-bg-surface border-b border-border overflow-hidden group"
          >
            <img
              src="/daozhonghua-cover.jpg"
              alt={locale === "zh" ? "道中华工作室视频截图" : "Dao Zhonghua Studio Video"}
              loading="lazy"
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
            />
            <div className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/30 transition-colors">
              <div className="w-16 h-16 rounded-full bg-bg-primary/70 backdrop-blur-md flex items-center justify-center text-white group-hover:scale-110 group-hover:bg-accent group-hover:text-bg-primary transition-all duration-300 shadow-xl">
                <Play size={28} className="ml-1" />
              </div>
            </div>
          </a>

          <div className="p-6 md:p-10">
            <div className="flex items-start justify-between flex-wrap gap-4 mb-4">
              <div>
                <h3 className="font-display text-2xl md:text-3xl font-bold text-text-primary">
                  {t("content.daozhonghua.title")}
                </h3>
                <p className="text-sm text-accent mt-1.5">
                  {t("content.daozhonghua.role")} ·{" "}
                  {t("content.daozhonghua.period")}
                </p>
              </div>
            </div>

            <p className="text-text-secondary leading-relaxed mb-5">
              {t("content.daozhonghua.description")}
            </p>

            {/* Highlights badges */}
            <div className="flex flex-wrap gap-2 mb-6">
              {highlights.map((h: string, i: number) => (
                <span
                  key={i}
                  className="px-3 py-1.5 rounded-full text-xs font-medium border border-accent/20 bg-accent/5 text-accent"
                >
                  {h}
                </span>
              ))}
            </div>

            {/* Media outlet logos row */}
            <div className="flex flex-wrap items-center gap-5 pt-5 border-t border-border">
              <span className="text-[10px] font-mono text-text-tertiary uppercase tracking-[0.15em]">
                {locale === "zh" ? "媒体转载" : "Featured on"}
              </span>
              {MEDIA_OUTLETS.map((outlet, i) => (
                <span
                  key={i}
                  className="text-sm font-medium text-text-secondary hover:text-text-primary hover:-translate-y-0.5 transition-all cursor-default"
                >
                  {locale === "zh" ? outlet.zh : outlet.en}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </SectionWrapper>
  );
}
