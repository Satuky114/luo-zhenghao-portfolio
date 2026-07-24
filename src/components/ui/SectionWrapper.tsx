"use client";

import { motion, useInView, type Variants } from "framer-motion";
import { useRef, type ReactNode } from "react";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { GlowOrb } from "@/components/ui/GlowOrb";
import { cn } from "@/lib/utils";

interface OrbConfig {
  size?: number;
  color?: string;
  position: string;
}

interface SectionWrapperProps {
  id?: string;
  className?: string;
  children: ReactNode;
  /** Override default animation variants */
  variants?: Variants;
  /** Optional ambient GlowOrb behind section content */
  orb?: OrbConfig;
  /** Show gradient transition strip at bottom edge */
  gradientTop?: boolean;
  gradientBottom?: boolean;
}

const defaultVariants: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] },
  },
};

/**
 * Wraps a section with scroll-triggered fade-in animation.
 * Uses `useInView` with `once: true` for performant reveal.
 * Supports optional GlowOrb and gradient transitions.
 */
export function SectionWrapper({
  id,
  className,
  children,
  variants,
  orb,
  gradientTop,
  gradientBottom,
}: SectionWrapperProps) {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const reduced = useReducedMotion();

  return (
    <motion.section
      id={id}
      ref={ref}
      initial={reduced ? "visible" : "hidden"}
      animate={inView ? "visible" : "hidden"}
      variants={variants ?? defaultVariants}
      className={cn("relative py-24 md:py-40 px-6 md:px-12 lg:px-24 overflow-hidden", className)}
    >
      {orb && (
        <GlowOrb
          size={orb.size}
          color={orb.color}
          className={orb.position}
        />
      )}

      {gradientTop && (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute top-0 inset-x-0 h-24 section-gradient-top"
        />
      )}

      {children}

      {gradientBottom && (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute bottom-0 inset-x-0 h-24 section-gradient-bottom"
        />
      )}
    </motion.section>
  );
}
