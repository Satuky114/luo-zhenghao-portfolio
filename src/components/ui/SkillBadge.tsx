"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

type BadgeCategory = "ai" | "dev" | "content" | "core";

interface SkillBadgeProps {
  label: string;
  category: BadgeCategory;
  delay?: number;
  className?: string;
}

const categoryColors: Record<BadgeCategory, string> = {
  ai: "border-purple-500/30 hover:border-purple-500 hover:shadow-[0_0_20px_rgba(147,51,234,0.2)]",
  dev: "border-blue-500/30 hover:border-blue-500 hover:shadow-[0_0_20px_rgba(59,130,246,0.2)]",
  content:
    "border-amber-500/30 hover:border-amber-500 hover:shadow-[0_0_20px_rgba(245,158,11,0.2)]",
  core: "border-emerald-500/30 hover:border-emerald-500 hover:shadow-[0_0_20px_rgba(52,211,153,0.2)]",
};

const categoryBgHover: Record<BadgeCategory, string> = {
  ai: "hover:bg-purple-500/10",
  dev: "hover:bg-blue-500/10",
  content: "hover:bg-amber-500/10",
  core: "hover:bg-emerald-500/10",
};

/**
 * Animated skill badge with category-based accent colors.
 */
export function SkillBadge({
  label,
  category,
  delay = 0,
  className,
}: SkillBadgeProps) {
  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.8 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{
        delay,
        type: "spring",
        stiffness: 400,
        damping: 25,
      }}
      whileHover={{ scale: 1.1, y: -2 }}
      className={cn(
        "inline-flex items-center px-3 py-1.5 rounded-full border text-sm font-medium cursor-default transition-colors duration-200",
        "bg-bg-surface text-text-secondary",
        categoryColors[category],
        categoryBgHover[category],
        className,
      )}
    >
      {label}
    </motion.span>
  );
}
