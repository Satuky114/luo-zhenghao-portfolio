"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { ArrowDown, Mail } from "lucide-react";
import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { GeometricFrame } from "@/components/ui/GeometricFrame";
import { GlowOrb } from "@/components/ui/GlowOrb";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export function Hero() {
  const { t } = useI18n();
  const containerRef = useRef<HTMLElement>(null);
  const reduced = useReducedMotion();

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  const opacity = useTransform(scrollYProgress, [0, 0.4], [1, 0]);
  const contentScale = useTransform(scrollYProgress, [0, 0.4], [1, 0.88]);

  const subtitleWords = t("hero.subtitle").split(" ");

  return (
    <motion.section
      id="hero"
      ref={containerRef}
      className="relative min-h-screen flex items-center justify-center overflow-hidden px-6"
      style={{ opacity }}
    >
      {/* Ambient glow orbs */}
      <GlowOrb
        size={500}
        color="var(--accent)"
        className="top-1/4 -left-32"
      />
      <GlowOrb
        size={400}
        color="#8B5CF6"
        className="bottom-1/4 -right-24"
      />

      {/* Geometric wireframe */}
      <motion.div
        className="absolute inset-0 flex items-center justify-center"
        style={{ scale: reduced ? 1 : contentScale }}
      >
        <GeometricFrame />
      </motion.div>

      {/* Content */}
      <div className="relative z-10 max-w-4xl mx-auto text-center">
        {/* Greeting */}
        <motion.p
          initial={reduced ? {} : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.5, ease: "easeOut" }}
          className="text-sm md:text-base font-mono text-text-tertiary tracking-[0.2em] uppercase mb-6"
        >
          {t("hero.greeting")}
        </motion.p>

        {/* Name - clip reveal */}
        <motion.h1
          initial={reduced ? {} : { opacity: 0, clipPath: "inset(0 100% 0 0)" }}
          animate={{ opacity: 1, clipPath: "inset(0 0% 0 0)" }}
          transition={{ delay: 0.3, duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
          className="text-5xl md:text-7xl lg:text-8xl font-extrabold tracking-tight text-text-primary mb-4"
        >
          {t("hero.name")}
        </motion.h1>

        {/* Title tags */}
        <motion.div
          initial={reduced ? {} : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.55, duration: 0.5, ease: "easeOut" }}
          className="flex items-center justify-center gap-3 flex-wrap mb-6"
        >
          <span className="inline-flex items-center px-4 py-1.5 rounded-full border border-accent/40 bg-accent/5 text-accent text-sm font-medium">
            {t("hero.title1")}
          </span>
          <span className="inline-flex items-center px-4 py-1.5 rounded-full border border-border bg-bg-surface text-text-secondary text-sm font-medium">
            {t("hero.title2")}
          </span>
        </motion.div>

        {/* Subtitle - word by word stagger */}
        <p className="text-base md:text-lg text-text-secondary max-w-xl mx-auto leading-relaxed mb-10">
          {subtitleWords.map((word, i) => (
            <motion.span
              key={i}
              initial={reduced ? {} : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: 0.75 + i * 0.06,
                duration: 0.4,
                ease: "easeOut",
              }}
              className="inline-block mr-[0.25em]"
            >
              {word}
            </motion.span>
          ))}
        </p>

        {/* CTAs */}
        <motion.div
          initial={reduced ? {} : { opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.1, type: "spring", stiffness: 300, damping: 25 }}
          className="flex items-center justify-center gap-4 flex-wrap"
        >
          <a
            href="#about"
            onClick={(e) => {
              e.preventDefault();
              document.getElementById("about")?.scrollIntoView({ behavior: "smooth" });
            }}
            className="inline-flex items-center gap-2 px-6 py-3 bg-accent hover:bg-accent/90 text-white font-medium rounded-xl transition-all hover:shadow-[0_0_30px_var(--accent-glow)]"
          >
            {t("hero.cta")}
          </a>
          <a
            href="#contact"
            onClick={(e) => {
              e.preventDefault();
              document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" });
            }}
            className="inline-flex items-center gap-2 px-6 py-3 border border-border hover:border-border-hover text-text-secondary hover:text-text-primary font-medium rounded-xl transition-all bg-bg-surface/50"
          >
            <Mail size={16} />
            {t("hero.cta2")}
          </a>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-text-tertiary"
        style={{
          opacity: useTransform(scrollYProgress, [0, 0.03], [1, 0]),
        }}
      >
        <span className="text-xs font-mono tracking-[0.2em] uppercase">
          Scroll
        </span>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        >
          <ArrowDown size={16} />
        </motion.div>
      </motion.div>
    </motion.section>
  );
}
