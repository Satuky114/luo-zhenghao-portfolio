"use client";

import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { useEffect } from "react";

interface GeometricFrameProps {
  /** Override default size */
  size?: number;
}

/**
 * SVG geometric wireframe (octahedron) that slowly rotates.
 * Small variant for Hero accent. Original full-size was reserved for background;
 * this one serves as a decorative accent by the heading.
 */
export function GeometricFrame({ size = 64 }: GeometricFrameProps) {
  const reduced = useReducedMotion();

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 50, damping: 30 });
  const springY = useSpring(mouseY, { stiffness: 50, damping: 30 });

  const offsetX = useTransform(springX, [-1, 1], [-6, 6]);
  const offsetY = useTransform(springY, [-1, 1], [-6, 6]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouseX.set((e.clientX / window.innerWidth) * 2 - 1);
      mouseY.set((e.clientY / window.innerHeight) * 2 - 1);
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY]);

  const half = size / 2;
  const vb = `${-half} ${-half} ${size} ${size}`;

  return (
    <motion.div
      className="pointer-events-none select-none"
      style={{ width: size, height: size, x: reduced ? 0 : offsetX, y: reduced ? 0 : offsetY }}
    >
      <motion.svg
        width={size}
        height={size}
        viewBox={vb}
        className="opacity-35"
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
          rotateX: { duration: 16, repeat: Infinity, ease: "linear" },
          rotateY: { duration: 19, repeat: Infinity, ease: "linear" },
          rotateZ: { duration: 22, repeat: Infinity, ease: "linear" },
        }}
      >
        <g fill="none" stroke="var(--accent)" strokeWidth="1.5" opacity="0.55">
          <polygon points="0,-48 42,0 -42,0" />
          <polygon points="0,48 42,0 -42,0" />
          <polygon points="0,-48 42,0 0,48" />
          <polygon points="0,-48 -42,0 0,48" />
        </g>
        <g fill="var(--accent)" opacity="0.7">
          <circle cx="0" cy="-48" r="1.2" />
          <circle cx="0" cy="48" r="1.2" />
          <circle cx="42" cy="0" r="1.2" />
          <circle cx="-42" cy="0" r="1.2" />
        </g>
        <circle cx="0" cy="0" r="52" fill="none" stroke="var(--accent)" strokeWidth="0.5" opacity="0.1" />
      </motion.svg>
    </motion.div>
  );
}
