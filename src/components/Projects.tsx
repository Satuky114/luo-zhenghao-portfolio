"use client";

import { motion } from "framer-motion";
import { ExternalLink, Code2, Sparkles, GitBranch, Play, Camera, Bot } from "lucide-react";
import { Volleyball } from "lucide-react";
import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { SectionWrapper } from "@/components/ui/SectionWrapper";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { useReducedMotion } from "@/hooks/useReducedMotion";

// ============================================================
// Project data
// ============================================================

interface ProjectItem {
  id: string;
  image: string | null;
  icon: React.ReactNode;
  link: { labelZh: string; labelEn: string; href: string } | null;
  accentVar: string;
  highlights: { icon: React.ReactNode; zh: string; en: string }[] | null;
  stats: { value: string; zh: string; en: string }[];
}

const PROJECTS: ProjectItem[] = [
  {
    id: "website",
    image: null,
    icon: <Code2 size={32} />,
    link: { labelZh: "GitHub", labelEn: "GitHub", href: "https://github.com/satuky114/luo-zhenghao-portfolio" },
    accentVar: "var(--accent)",
    highlights: null,
    stats: [
      { value: "100%", zh: "AI协同开发", en: "AI Co-developed" },
      { value: "3d", zh: "从零到上线", en: "Build to Ship" },
      { value: "12+", zh: "技术栈组件", en: "Stack Components" },
    ],
  },
  {
    id: "daozhonghua",
    image: "/daozhonghua-cover.jpg",
    icon: <Play size={32} />,
    link: {
      labelZh: "封面新闻观看",
      labelEn: "Watch on Cover News",
      href: "https://www.thecover.cn/video/Lk/1Scm5Z8mH90qSdq8Jkw==",
    },
    accentVar: "var(--accent3)",
    highlights: null,
    stats: [
      { value: "25", zh: "原创作品", en: "Original Works" },
      { value: "117K+", zh: "单条最高浏览", en: "Max Single Views" },
      { value: "200万+", zh: "累计传播量", en: "Total Reach" },
    ],
  },
  {
    id: "volleyball",
    image: "/volleyball.jpg",
    icon: <Volleyball size={32} />,
    link: {
      labelZh: "抖音观看集锦",
      labelEn: "Watch on Douyin",
      href: "https://v.douyin.com/7ijCop_yudg/",
    },
    accentVar: "var(--accent2)",
    highlights: null,
    stats: [
      { value: "贡嘎杯", zh: "省级超级联赛", en: "Provincial League" },
      { value: "5K+", zh: "点赞", en: "Likes" },
      { value: "8万+", zh: "浏览量", en: "Views" },
    ],
  },
  {
    id: "photography",
    image: "/sheying.jpg",
    icon: <Camera size={32} />,
    link: null,
    accentVar: "var(--accent)",
    highlights: null,
    stats: [
      { value: "二等奖", zh: "校摄影大赛", en: "2nd Prize" },
      { value: "捕捉", zh: "光影与瞬间", en: "Light & Moments" },
    ],
  },
  {
    id: "daka",
    image: null,
    icon: <Bot size={32} />,
    link: {
      labelZh: "GitHub 开源",
      labelEn: "GitHub (Open Source)",
      href: "https://github.com/satuky114/luo-zhenghao-portfolio",
    },
    accentVar: "var(--accent2)",
    highlights: null,
    stats: [
      { value: "v14", zh: "版本迭代", en: "Iterations" },
      { value: "100%", zh: "无人值守", en: "Unattended" },
      { value: "21:30", zh: "每日自动", en: "Daily Auto" },
    ],
  },
];

// ============================================================
// Full-width project card
// ============================================================

function ProjectCard({
  project,
  index,
  t,
  locale,
  reduced,
}: {
  project: ProjectItem;
  index: number;
  t: (key: string) => string;
  locale: string;
  reduced: boolean;
}) {
  const title = t(`projects.${project.id}.title`);
  const description = t(`projects.${project.id}.description`);
  const tags: string[] = t(`projects.${project.id}.tags`)
    .split(",")
    .map((s: string) => s.trim())
    .filter(Boolean);
  const isEven = index % 2 === 0;

  return (
    <motion.div
      initial={reduced ? {} : { opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ delay: index * 0.12, duration: 0.6, ease: "easeOut" }}
      className="group"
    >
      <div
        className={`grid md:grid-cols-5 gap-8 md:gap-12 items-center ${
          isEven ? "" : "md:flex-row-reverse"
        }`}
      >
        {/* ---- Visual side (3/5 or 2/5 alternating) ---- */}
        <div
          className={isEven ? "md:col-span-3 md:order-1" : "md:col-span-3 md:order-2"}
        >
          {project.image ? (
            <div className="relative aspect-video rounded-2xl overflow-hidden border border-border/60 group-hover:border-border transition-colors duration-500 shadow-xl shadow-black/30">
              <img
                src={project.image}
                alt={title}
                loading="lazy"
                                                          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
              style={{ objectPosition: "center top" }}
              />
              <div
                className="absolute inset-0 pointer-events-none"
                style={{
                  background: `linear-gradient(to top, var(--bg-primary) 0%, transparent 50%)`,
                  opacity: 0.6,
                }}
              />
              {/* Play overlay */}
              {project.id === "daozhonghua" && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <a
                    href="https://www.thecover.cn/video/Lk/1Scm5Z8mH90qSdq8Jkw=="
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-16 h-16 rounded-full bg-bg-primary/70 backdrop-blur-md flex items-center justify-center text-text-primary hover:scale-110 hover:bg-accent hover:text-bg-primary transition-all duration-300 shadow-xl"
                  >
                    <Play size={24} className="ml-1" />
                  </a>
                </div>
              )}
              {/* External link badge */}
              {project.link && (
                <a
                  href={project.link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-bg-primary/70 backdrop-blur-md border border-border/50 text-xs font-medium text-text-secondary hover:text-accent transition-all z-10"
                >
                  <ExternalLink size={12} />
                  <span>{locale === "zh" ? project.link.labelZh : project.link.labelEn}</span>
                </a>
              )}
            </div>
          ) : (
            <div className="relative aspect-video rounded-2xl overflow-hidden border border-border/60 group-hover:border-border transition-colors duration-500 shadow-xl shadow-black/30 bg-bg-surface flex items-center justify-center">
              {/* Gradient bg */}
              <div
                className="absolute inset-0 pointer-events-none opacity-50"
                style={{
                  background: `radial-gradient(ellipse at center, ${project.accentVar}10 0%, transparent 70%)`,
                }}
              />
              <motion.div
                className="relative z-10 p-6 rounded-3xl border border-border/30 bg-bg-elevated/70 backdrop-blur-sm"
                style={{ color: project.accentVar }}
                whileHover={{ scale: 1.06, rotate: 2 }}
                transition={{ type: "spring", stiffness: 250, damping: 20 }}
              >
                {project.icon}
              </motion.div>
            </div>
          )}
        </div>

        {/* ---- Text side (2/5) ---- */}
        <div
          className={
            isEven
              ? "md:col-span-2 md:order-2 md:pl-4"
              : "md:col-span-2 md:order-1 md:pr-4"
          }
        >
          {/* Eyebrow */}
          <span className="font-mono text-[10px] tracking-[0.2em] uppercase text-text-tertiary mb-3 block">
            {locale === "zh" ? `项目 · ${String(index + 1).padStart(2, "0")}` : `Project ${String(index + 1).padStart(2, "0")}`}
          </span>

          <h3 className="font-display text-2xl md:text-3xl font-bold text-text-primary group-hover:text-accent transition-colors mb-3 leading-tight">
            {title}
          </h3>

          <p className="text-sm md:text-base text-text-secondary leading-relaxed mb-6">
            {description}
          </p>

          {/* Stats grid */}
          <div className="grid grid-cols-3 gap-3 mb-5">
            {project.stats.map((stat, i) => (
              <div
                key={i}
                className="p-3 rounded-xl border border-border/50 bg-bg-surface/40 text-center"
              >
                <div className="font-display text-xl md:text-2xl font-bold text-accent mb-0.5">
                  {stat.value}
                </div>
                <div className="text-[10px] font-mono uppercase tracking-[0.08em] text-text-tertiary leading-tight">
                  {locale === "zh" ? stat.zh : stat.en}
                </div>
              </div>
            ))}
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-1.5">
            {tags.map((tag: string) => (
              <span
                key={tag}
                className="px-2.5 py-1 rounded-full text-[11px] font-mono font-medium border text-text-secondary transition-colors cursor-default"
                style={{
                  borderColor: `${project.accentVar}20`,
                  backgroundColor: `${project.accentVar}08`,
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ============================================================
// Main Projects section
// ============================================================

export function Projects() {
  const { t, locale } = useI18n();
  const reduced = useReducedMotion();

  return (
    <SectionWrapper id="projects" gradientBottom>
      <SectionHeading
        title={t("projects.title")}
        subtitle={t("projects.subtitle")}
      />

      <div className="max-w-6xl mx-auto space-y-24 md:space-y-40">
        {PROJECTS.map((project, idx) => (
          <ProjectCard
            key={project.id}
            project={project}
            index={idx}
            t={t}
            locale={locale}
            reduced={reduced}
          />
        ))}
      </div>
    </SectionWrapper>
  );
}
