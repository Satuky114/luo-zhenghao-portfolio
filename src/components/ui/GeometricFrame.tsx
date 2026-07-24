"use client";

import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";

/**
 * SVG geometric wireframe (octahedron) that slowly rotates.
 * Uses mouse position for subtle parallax offset.
 */
export function GeometricFrame() {
  const reduced = useReducedMotion();

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 50, damping: 30 });
  const springY = useSpring(mouseY, { stiffness: 50, damping: 30 });

  const offsetX = useTransform(springX, [-1, 1], [-15, 15]);
  const offsetY = useTransform(springY, [-1, 1], [-15, 15]);

  // Track mouse globally
  if (typeof window !== "undefined") {
    window.addEventListener(
      "mousemove",
      (e: MouseEvent) => {
        mouseX.set((e.clientX / window.innerWidth) * 2 - 1);
        mouseY.set((e.clientY / window.innerHeight) * 2 - 1);
      },
      { passive: true },
    );
  }

  return (
    <motion.div
      className="absolute inset-0 flex items-center justify-center pointer-events-none select-none"
      style={{ x: reduced ? 0 : offsetX, y: reduced ? 0 : offsetY }}
    >
      <motion.svg
        width="320"
        height="320"
        viewBox="-160 -160 320 320"
        className="opacity-30"
        animate={
          reduced
            ? {}
            : {
                rotateX: [0, 360],
                rotateY: [0, 360],
                rotateZ: [0, 360],
              }
        }
        transition={{
          rotateX: { duration: 20, repeat: Infinity, ease: "linear" },
          rotateY: { duration: 24, repeat: Infinity, ease: "linear" },
          rotateZ: { duration: 28, repeat: Infinity, ease: "linear" },
        }}
      >
        {/* Octahedron wireframe */}
        <g fill="none" stroke="var(--accent)" strokeWidth="1" opacity="0.6">
          {/* Top pyramid */}
          <polygon points="0,-120 104,0 -104,0" />
          {/* Bottom pyramid */}
          <polygon points="0,120 104,0 -104,0" />
          {/* Side triangles */}
          <polygon points="0,-120 104,0 0,120" />
          <polygon points="0,-120 -104,0 0,120" />
          {/* Equator */}
          <line x1="-140" y1="0" x2="140" y2="0" opacity="0.15" />
          {/* Inner connection lines */}
          <line x1="0" y1="-120" x2="0" y2="120" opacity="0.1" />
        </g>

        {/* Nodes at vertices */}
        <g fill="var(--accent)" opacity="0.8">
          <circle cx="0" cy="-120" r="3" />
          <circle cx="0" cy="120" r="3" />
          <circle cx="104" cy="0" r="3" />
          <circle cx="-104" cy="0" r="3" />
        </g>

        {/* Outer ring */}
        <circle
          cx="0"
          cy="0"
          r="130"
          fill="none"
          stroke="var(--accent)"
          strokeWidth="0.5"
          opacity="0.12"
        />
      </motion.svg>
    </motion.div>
  );
}
