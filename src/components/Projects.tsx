"use client";

import { motion } from "framer-motion";
import { ExternalLink, Code2, Sparkles, GitBranch } from "lucide-react";
import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { SectionWrapper } from "@/components/ui/SectionWrapper";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { TiltCard } from "@/components/ui/TiltCard";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export function Projects() {
  const { t, locale } = useI18n();
  const reduced = useReducedMotion();

  const tags = t("projects.website.tags").split(",").map((s: string) => s.trim());

  const highlights = [
    { icon: <Sparkles size={16} />, zh: "AI协同全流程", en: "AI-Powered Full Stack" },
    { icon: <GitBranch size={16} />, zh: "GitHub版本管理", en: "GitHub Version Control" },
    { icon: <Code2 size={16} />, zh: "Prompt Engineering", en: "Prompt Engineering" },
  ];

  return (
    <SectionWrapper id="projects" className="bg-bg-elevated/50" orb={{ color: "#8B5CF6", size: 380, position: "bottom-0 -left-24" }} gradientBottom>
      <SectionHeading
        number="02"
        title={t("projects.title")}
        subtitle={t("projects.subtitle")}
      />

      <TiltCard className="max-w-3xl mx-auto p-0 overflow-hidden">
        <div className="p-8 md:p-10">
          {/* Project title + link */}
          <div className="flex items-start justify-between mb-4">
            <h3 className="text-2xl md:text-3xl font-bold text-text-primary">
              {t("projects.website.title")}
            </h3>
            <a
              href="#"
              className="p-2 text-text-tertiary hover:text-accent transition-colors"
              title={locale === "zh" ? "访问网站" : "Visit site"}
            >
              <ExternalLink size={18} />
            </a>
          </div>

          {/* Description */}
          <p className="text-text-secondary leading-relaxed mb-6">
            {t("projects.website.description")}
          </p>

          {/* Highlights */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            {highlights.map((h, i) => (
              <motion.div
                key={i}
                initial={reduced ? {} : { opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="flex flex-col items-center gap-1.5 p-3 rounded-lg bg-bg-surface/50 border border-border text-center"
              >
                <span className="text-accent">{h.icon}</span>
                <span className="text-xs font-medium text-text-secondary">
                  {locale === "zh" ? h.zh : h.en}
                </span>
              </motion.div>
            ))}
          </div>

          {/* Tech tags */}
          <div className="flex flex-wrap gap-2">
            {tags.map((tag: string, i: number) => (
              <motion.span
                key={tag}
                initial={reduced ? {} : { opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.05, backgroundColor: "var(--accent)", color: "#fff" }}
                transition={{ delay: 0.5 + i * 0.05 }}
                className="px-3 py-1 rounded-full text-xs font-mono font-medium border border-border bg-bg-surface text-text-secondary hover:border-accent transition-colors cursor-default"
              >
                {tag}
              </motion.span>
            ))}
          </div>
        </div>

        {/* Decorative bottom bar */}
        <div className="h-1 bg-gradient-to-r from-accent via-accent/50 to-transparent" />
      </TiltCard>
    </SectionWrapper>
  );
}
