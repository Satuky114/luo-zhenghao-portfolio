"use client";

import { motion } from "framer-motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";

interface GlowOrbProps {
  /** Orb size in px */
  size?: number;
  /** Color (CSS color value) */
  color?: string;
  className?: string;
  /** Position style overrides */
  style?: React.CSSProperties;
}

/**
 * A blurred radial-gradient orb used as ambient background decoration.
 * Animates with a slow float + pulse. Respects prefers-reduced-motion.
 */
export function GlowOrb({
  size = 400,
  color = "var(--accent)",
  className = "",
  style,
}: GlowOrbProps) {
  const reduced = useReducedMotion();

  return (
    <motion.div
      className={`pointer-events-none absolute rounded-full ${className}`}
      style={{
        width: size,
        height: size,
        background: `radial-gradient(circle at center, ${color} 0%, transparent 70%)`,
        filter: "blur(80px)",
        opacity: 0.2,
        ...style,
      }}
      animate={
        reduced
          ? {}
          : { scale: [1, 1.08, 1], opacity: [0.15, 0.25, 0.15] }
      }
      transition={
        reduced
          ? {}
          : { duration: 6, repeat: Infinity, ease: "easeInOut" }
      }
    />
  );
}
