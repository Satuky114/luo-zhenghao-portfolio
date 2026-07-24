"use client";

import { useScroll, useTransform, type MotionValue } from "framer-motion";
import { useEffect, useState } from "react";

/**
 * Returns a 0-1 scroll progress value based on the full page height.
 */
export function useScrollProgress(): MotionValue<number> {
  const { scrollYProgress } = useScroll();
  return scrollYProgress;
}

/**
 * Returns a 0-1 progress through a specific element's visibility.
 * Uses IntersectionObserver for performance.
 */
export function useElementProgress(
  threshold: number = 0.2,
): { ref: (node: HTMLElement | null) => void; progress: number } {
  const [progress, setProgress] = useState(0);
  const [node, setNode] = useState<HTMLElement | null>(null);

  useEffect(() => {
    if (!node) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setProgress(entry.intersectionRatio);
      },
      { threshold: Array.from({ length: 21 }, (_, i) => i / 20) },
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [node]);

  return { ref: setNode, progress };
}
