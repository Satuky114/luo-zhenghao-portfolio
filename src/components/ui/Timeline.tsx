"use client";

import { motion, useInView } from "framer-motion";
import { useRef, type ReactNode } from "react";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils";

interface TimelineItem {
  /** Year/date label */
  date: string;
  title: string;
  subtitle?: string;
  description?: ReactNode;
  /** Whether this is the latest/current item */
  isLatest?: boolean;
}

interface TimelineProps {
  items: TimelineItem[];
  className?: string;
}

/**
 * Vertical timeline with animated line drawing and staggered item reveals.
 */
export function Timeline({ items, className }: TimelineProps) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const reduced = useReducedMotion();

  return (
    <div ref={ref} className={cn("relative", className)}>
      {/* Animated vertical line */}
      <motion.div
        className="absolute left-4 md:left-1/2 top-0 w-px bg-border origin-top"
        style={{
          height: reduced ? "100%" : undefined,
          marginLeft: reduced ? undefined : undefined,
        }}
        initial={reduced ? { height: "100%" } : { scaleY: 0 }}
        animate={inView ? { scaleY: 1 } : {}}
        transition={{ duration: 0.8, ease: "easeOut" }}
      />

      <div className="space-y-12">
        {items.map((item, i) => (
          <motion.div
            key={i}
            className={cn(
              "relative pl-10 md:pl-0",
              i % 2 === 0
                ? "md:pr-[50%] md:pl-0 md:text-right"
                : "md:pl-[50%] md:pr-0",
            )}
            initial={reduced ? { opacity: 1 } : { opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ delay: 0.3 + i * 0.15, duration: 0.5 }}
          >
            {/* Timeline dot */}
            <div
              className={cn(
                "absolute left-[13px] md:left-1/2 top-1 w-[11px] h-[11px] -translate-x-1/2 rounded-full border-2 bg-bg-primary z-10",
                item.isLatest
                  ? "border-accent animate-pulse-glow"
                  : "border-border",
              )}
            />

            {/* Content */}
            <div
              className={cn(
                "p-5 rounded-xl border border-border bg-bg-elevated hover:border-border-hover transition-colors",
                i % 2 === 0 ? "md:mr-8" : "md:ml-8",
              )}
            >
              <span className="font-mono text-xs text-text-tertiary tracking-[0.15em] uppercase">
                {item.date}
              </span>
              <h4 className="mt-1 text-lg font-semibold text-text-primary">
                {item.title}
              </h4>
              {item.subtitle && (
                <p className="text-sm text-accent mt-0.5">{item.subtitle}</p>
              )}
              {item.description && (
                <div className="mt-2 text-sm text-text-secondary leading-relaxed">
                  {item.description}
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
