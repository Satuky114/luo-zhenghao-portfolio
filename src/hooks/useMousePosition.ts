"use client";

import { useState, useEffect, useCallback } from "react";

interface MousePosition {
  x: number;
  y: number;
  /** Normalized -1 to 1 relative to viewport center */
  normalizedX: number;
  normalizedY: number;
}

/**
 * Tracks mouse position with normalized coordinates (-1 to 1).
 * Used for parallax / tilt effects.
 */
export function useMousePosition(): MousePosition {
  const [pos, setPos] = useState<MousePosition>({
    x: 0,
    y: 0,
    normalizedX: 0,
    normalizedY: 0,
  });

  const handleMouseMove = useCallback((e: MouseEvent) => {
    const x = e.clientX;
    const y = e.clientY;
    setPos({
      x,
      y,
      normalizedX: (x / window.innerWidth) * 2 - 1,
      normalizedY: (y / window.innerHeight) * 2 - 1,
    });
  }, []);

  useEffect(() => {
    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [handleMouseMove]);

  return pos;
}
