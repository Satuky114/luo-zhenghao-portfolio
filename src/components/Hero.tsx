"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { ArrowDown, Mail, Play, ExternalLink } from "lucide-react";
import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { GlowOrb } from "@/components/ui/GlowOrb";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export function Hero() {
  const { t, locale } = useI18n();
  const containerRef = useRef<HTMLElement>(null);
  const reduced = useReducedMotion();

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  const opacity = useTransform(scrollYProgress, [0, 0.4], [1, 0]);
  const imageScale = useTransform(scrollYProgress, [0, 0.4], [1, 0.92]);

  return (
    <motion.section
      id="hero"
      ref={containerRef}
      className="relative min-h-screen flex items-center justify-center overflow-hidden px-6 md:px-12 lg:px-24"
      style={{ opacity }}
    >
      {/* Vignette overlay — viewfinder metaphor */}
      <div className="hero-vignette" />

      {/* Ambient safelight glow */}
      <GlowOrb
        size={700}
        color="var(--accent)"
        className="top-1/3 -left-32 opacity-15"
      />

      <div className="relative z-10 w-full max-w-7xl mx-auto grid md:grid-cols-2 gap-12 md:gap-20 items-center">
        {/* ====== LEFT: Photo + vibe ====== */}
        <motion.div
          className="relative order-2 md:order-1 flex justify-center md:justify-start"
          style={{ scale: reduced ? 1 : imageScale }}
        >
          <div className="relative">
            {/* Photo frame */}
            <div className="w-56 h-56 md:w-80 md:h-80 rounded-3xl overflow-hidden border-2 border-border/60 shadow-2xl shadow-black/40">
              <img
                src="/avatar.jpg"
                alt={locale === "zh" ? "罗政皓" : "Luo Zhenghao"}
                className="w-full h-full object-cover"
              />
            </div>
            {/* Decorative accent ring */}
            <div
              className="absolute -inset-3 rounded-[28px] border border-accent/15 pointer-events-none hidden md:block"
            />
            {/* Floating stat chip */}
            <motion.div
              initial={reduced ? {} : { opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8, duration: 0.5 }}
              className="absolute -bottom-4 -right-4 md:bottom-6 md:-right-10 bg-bg-elevated border border-border rounded-2xl px-4 py-3 shadow-xl hidden md:block"
            >
              <span className="block text-2xl md:text-3xl font-display font-bold text-accent">
                200<span className="text-sm text-text-tertiary">万+</span>
              </span>
              <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-text-tertiary">
                {locale === "zh" ? "累计传播量" : "Total Reach"}
              </span>
            </motion.div>
          </div>
        </motion.div>

        {/* ====== RIGHT: Value proposition ====== */}
        <div className="relative z-10 order-1 md:order-2 text-center md:text-left">
          {/* Eyebrow */}
          <motion.p
            initial={reduced ? {} : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.5, ease: "easeOut" }}
            className="font-mono text-xs md:text-sm text-text-tertiary tracking-[0.2em] uppercase mb-6"
          >
            {locale === "zh" ? "AI 内容创作者 · 成都" : "AI Content Creator · Chengdu"}
          </motion.p>

          {/* Value proposition — the thesis */}
          <motion.h1
            initial={reduced ? {} : { opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25, duration: 0.6, ease: "easeOut" }}
            className="font-display text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-text-primary mb-4 leading-[1.15]"
          >
            {locale === "zh" ? (
              <>
                用 AI 放大<span className="text-accent">内容创作</span>
                <br />
                的每一帧想象
              </>
            ) : (
              <>
                Amplifying <span className="text-accent">content creation</span>
                <br />
                with AI — frame by frame
              </>
            )}
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={reduced ? {} : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.45, duration: 0.5 }}
            className="text-base md:text-lg text-text-secondary max-w-lg leading-relaxed mb-8"
          >
            {locale === "zh"
              ? "罗政皓 · 西南民族大学网络与新媒体专业 · 双语主播、内容运营、AI工具深度实践者"
              : "Luo Zhenghao · Network & New Media at Southwest Minzu University · Bilingual anchor, content strategist, AI practitioner"}
          </motion.p>

          {/* Tags + CTA */}
          <motion.div
            initial={reduced ? {} : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="flex items-center gap-3 flex-wrap mb-8 justify-center md:justify-start"
          >
            <span className="inline-flex items-center px-4 py-2 rounded-full border border-accent/30 bg-accent/5 text-accent text-sm font-medium">
              {t("hero.title1")}
            </span>
            <span className="inline-flex items-center px-4 py-2 rounded-full border border-border bg-bg-surface/50 text-text-secondary text-sm font-medium">
              {t("hero.title2")}
            </span>
          </motion.div>

          {/* CTAs */}
          <motion.div
            initial={reduced ? {} : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.75, duration: 0.5 }}
            className="flex items-center gap-4 flex-wrap justify-center md:justify-start"
          >
            <a
              href="#projects"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById("projects")?.scrollIntoView({ behavior: "smooth" });
              }}
              className="inline-flex items-center gap-2.5 px-6 py-3.5 bg-accent hover:bg-accent/90 text-bg-primary font-semibold rounded-xl transition-all hover:shadow-[0_0_50px_var(--accent-glow)]"
            >
              <Play size={16} />
              {locale === "zh" ? "看我的作品" : "See My Work"}
            </a>
            <a
              href="#contact"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" });
              }}
              className="inline-flex items-center gap-2.5 px-6 py-3.5 border border-border hover:border-text-secondary text-text-secondary hover:text-text-primary font-medium rounded-xl transition-all bg-bg-surface/40"
            >
              <Mail size={16} />
              {locale === "zh" ? "联系我" : "Contact Me"}
            </a>
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-text-tertiary"
        style={{
          opacity: useTransform(scrollYProgress, [0, 0.03], [1, 0]),
        }}
      >
        <span className="text-[10px] font-mono tracking-[0.25em] uppercase">
          Scroll
        </span>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        >
          <ArrowDown size={14} />
        </motion.div>
      </motion.div>
    </motion.section>
  );
}
