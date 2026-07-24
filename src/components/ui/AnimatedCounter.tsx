"use client";

import { motion, useInView, useSpring, useMotionValue, useTransform } from "framer-motion";
import { useRef, useEffect } from "react";
import { useReducedMotion } from "@/hooks/useReducedMotion";

interface AnimatedCounterProps {
  value: number;
  suffix?: string;
  prefix?: string;
  duration?: number;
  className?: string;
}

/**
 * Animates a number from 0 to `value` when scrolled into view.
 * Uses framer-motion spring for smooth easing.
 */
export function AnimatedCounter({
  value,
  suffix = "",
  prefix = "",
  duration = 1.2,
  className = "",
}: AnimatedCounterProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const reduced = useReducedMotion();

  const springVal = useMotionValue(0);
  const spring = useSpring(springVal, {
    stiffness: 80,
    damping: 30,
    duration: reduced ? 0 : duration * 1000,
  });
  const rounded = useTransform(spring, (v) => Math.round(v));

  useEffect(() => {
    if (inView) springVal.set(value);
  }, [inView, value, springVal]);

  return (
    <motion.span
      ref={ref}
      className={`font-mono font-bold tracking-tight ${className}`}
    >
      {prefix}
      <motion.span>{rounded}</motion.span>
      {suffix}
    </motion.span>
  );
}
