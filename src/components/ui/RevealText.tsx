"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface RevealTextProps {
  children: ReactNode;
  /** Animation variant */
  variant?: "fade-up" | "clip" | "blur-in";
  delay?: number;
  duration?: number;
  className?: string;
  as?: keyof React.JSX.IntrinsicElements;
}

/**
 * Text reveal animation component.
 *
 * - `fade-up`: fades in from below (default)
 * - `clip`: slides in with a clip-path horizontal reveal
 * - `blur-in`: fades in from a blur state
 */
export function RevealText({
  children,
  variant = "fade-up",
  delay = 0,
  duration = 0.6,
  className = "",
  as: Tag = "div",
}: RevealTextProps) {
  const MotionTag = motion.create(Tag as any);

  const variants = {
    "fade-up": {
      initial: { opacity: 0, y: 20 },
      animate: { opacity: 1, y: 0 },
    },
    clip: {
      initial: { opacity: 0, clipPath: "inset(0 100% 0 0)" },
      animate: { opacity: 1, clipPath: "inset(0 0% 0 0)" },
    },
    "blur-in": {
      initial: { opacity: 0, filter: "blur(8px)" },
      animate: { opacity: 1, filter: "blur(0px)" },
    },
  };

  const selected = variants[variant];

  return (
    <MotionTag
      initial="initial"
      animate="animate"
      variants={{
        initial: selected.initial,
        animate: {
          ...selected.animate,
          transition: { duration, delay, ease: [0.25, 0.46, 0.45, 0.94] },
        },
      }}
      className={className}
    >
      {children}
    </MotionTag>
  );
}
