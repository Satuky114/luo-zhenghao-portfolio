"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils";

interface SectionHeadingProps {
  /** Section number, e.g. "01" */
  number?: string;
  title: string;
  subtitle?: string;
  align?: "left" | "center";
  className?: string;
}

/**
 * Unified section heading with optional number prefix.
 * Animates on scroll into view.
 */
export function SectionHeading({
  number,
  title,
  subtitle,
  align = "left",
  className,
}: SectionHeadingProps) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const reduced = useReducedMotion();

  return (
    <motion.div
      ref={ref}
      initial={reduced ? { opacity: 1 } : { opacity: 0, y: 16 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className={cn(
        "mb-16 md:mb-24",
        align === "center" && "text-center",
        className,
      )}
    >
      {number && (
        <span className="block font-mono text-xs tracking-[0.2em] text-text-tertiary mb-4">
          {number}
        </span>
      )}
      <h2 className="font-display text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight text-text-primary">
        {title}
      </h2>
      {subtitle && (
        <p className="mt-4 text-sm md:text-base text-text-secondary max-w-2xl">
          {subtitle}
        </p>
      )}
    </motion.div>
  );
}
