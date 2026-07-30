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

const GROUPS: SkillGroup[] = [
  {
    titleKey: "skills.ai",
    category: "ai",
    items: ["ChatGPT", "Claude", "DeepSeek", "Grok", "Gemini", "Codex"],
  },
  {
    titleKey: "skills.dev",
    category: "dev",
    items: ["GitHub", "VS Code", "React", "Next.js", "Vite", "Tailwind CSS", "TypeScript"],
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

export function Skills() {
  const { t, locale } = useI18n();
  const reduced = useReducedMotion();

  return (
    <SectionWrapper id="skills" gradientBottom className="md:py-48 py-32">
      <SectionHeading title={t("skills.title")} />

      <div className="max-w-4xl mx-auto">
        <div className="grid sm:grid-cols-2 gap-8 md:gap-12">
          {GROUPS.map((group, gi) => (
            <div key={group.titleKey}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-1 h-4 rounded-full bg-accent" />
                <h3 className="text-xs font-mono font-medium text-text-tertiary uppercase tracking-[0.15em]">
                  {t(group.titleKey)}
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {group.items.map((item, i) => (
                  <SkillBadge
                    key={item}
                    label={item}
                    category={group.category}
                    delay={gi * 0.1 + i * 0.03}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Core competency highlight */}
        <div className="mt-14 pt-8 border-t border-border">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-mono text-text-secondary">
              Prompt Engineering
            </span>
            <span className="text-[10px] font-mono text-accent bg-accent/8 px-2 py-0.5 rounded-full">
              {locale === "zh" ? "精通" : "Proficient"}
            </span>
          </div>
          <div className="h-1 rounded-full bg-bg-surface overflow-hidden">
            <motion.div
              initial={reduced ? { width: "85%" } : { width: "0%" }}
              whileInView={{ width: "85%" }}
              viewport={{ once: true }}
              transition={{
                delay: 0.3,
                duration: 1.0,
                ease: [0.25, 0.46, 0.45, 0.94],
              }}
              className="h-full rounded-full bg-accent"
            />
          </div>
        </div>
      </div>
    </SectionWrapper>
  );
}
