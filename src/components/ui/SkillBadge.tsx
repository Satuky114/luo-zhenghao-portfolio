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
  ai: "border-amber-400/25 hover:border-amber-400 hover:shadow-[0_0_20px_rgba(212,145,92,0.15)]",
  dev: "border-cyan-400/25 hover:border-cyan-400 hover:shadow-[0_0_20px_rgba(90,143,143,0.15)]",
  content:
    "border-orange-400/25 hover:border-orange-400 hover:shadow-[0_0_20px_rgba(196,84,62,0.15)]",
  core: "border-amber-300/25 hover:border-amber-300 hover:shadow-[0_0_20px_rgba(212,145,92,0.12)]",
};

const categoryBgHover: Record<BadgeCategory, string> = {
  ai: "hover:bg-amber-500/8",
  dev: "hover:bg-cyan-500/8",
  content: "hover:bg-orange-500/8",
  core: "hover:bg-amber-400/8",
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
