"use client";

import { motion } from "framer-motion";
import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { SectionWrapper } from "@/components/ui/SectionWrapper";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { SkillBadge } from "@/components/ui/SkillBadge";
import { useReducedMotion } from "@/hooks/useReducedMotion";

type BadgeCategory = "ai" | "dev" | "content" | "core";

interface SkillGroup {
  titleKey: string;
  category: BadgeCategory;
  items: string[];
}

export function Skills() {
  const { t, locale } = useI18n();
  const reduced = useReducedMotion();

  const groups: SkillGroup[] = [
    {
      titleKey: "skills.ai",
      category: "ai",
      items: ["ChatGPT", "Claude", "DeepSeek", "Grok", "Gemini", "Codex"],
    },
    {
      titleKey: "skills.dev",
      category: "dev",
      items: [
        "GitHub",
        "VS Code",
        "React",
        "Next.js",
        "Vite",
        "Tailwind CSS",
        "TypeScript",
      ],
    },
    {
      titleKey: "skills.content",
      category: "content",
      items: ["Canva", "剪映/CapCut", "PR", "Figma"],
    },
    {
      titleKey: "skills.core",
      category: "core",
      items: [
        "Prompt Engineering",
        "AI内容生产",
        "内容策划",
        "热点分析",
        "信息检索",
        "视频创作",
        "双语能力",
      ],
    },
  ];

  return (
    <SectionWrapper id="skills" className="bg-bg-elevated/50" orb={{ color: "var(--accent)", size: 420, position: "top-0 left-1/3 -translate-x-1/2" }} gradientBottom>
      <SectionHeading number="04" title={t("skills.title")} />

      <div className="max-w-4xl mx-auto space-y-10">
        {groups.map((group, gi) => (
          <motion.div
            key={group.titleKey}
            initial={reduced ? {} : { opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: gi * 0.1, duration: 0.5 }}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-1 h-5 rounded-full bg-accent" />
              <h3 className="text-sm font-mono font-medium text-text-tertiary uppercase tracking-[0.15em]">
                {t(group.titleKey)}
              </h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {group.items.map((item, i) => (
                <SkillBadge
                  key={item}
                  label={item}
                  category={group.category}
                  delay={gi * 0.15 + i * 0.04}
                />
              ))}
            </div>
          </motion.div>
        ))}

        {/* Prompt Engineering progress bar */}
        <motion.div
          initial={reduced ? {} : { opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="pt-6 border-t border-border"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-mono text-text-secondary">
              Prompt Engineering
            </span>
            <span className="text-xs font-mono text-accent">
              {locale === "zh" ? "精通" : "Proficient"}
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-bg-surface overflow-hidden">
            <motion.div
              initial={reduced ? { width: "85%" } : { width: "0%" }}
              whileInView={{ width: "85%" }}
              viewport={{ once: true }}
              transition={{
                delay: 0.8,
                duration: 1.2,
                ease: [0.25, 0.46, 0.45, 0.94],
              }}
              className="h-full rounded-full bg-accent"
            />
          </div>
        </motion.div>
      </div>
    </SectionWrapper>
  );
}
