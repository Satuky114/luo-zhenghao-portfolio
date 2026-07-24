"use client";

import { Hero } from "@/components/Hero";
import { About } from "@/components/About";
import { Projects } from "@/components/Projects";
import { ContentCreation } from "@/components/ContentCreation";
import { Skills } from "@/components/Skills";
import { Experience } from "@/components/Experience";
import { Contact } from "@/components/Contact";
import { Footer } from "@/components/Footer";
import { Nav } from "@/components/Nav";
import { GlowOrb } from "@/components/ui/GlowOrb";

export default function HomePage() {
  return (
    <main className="relative z-[1]">
      {/* Global scan-line decoration */}
      <div className="scan-line" />

      <Nav />
      <Hero />
      <About />
      <Projects />
      <ContentCreation />
      <Skills />
      <Experience />
      <Contact />

      {/* Footer with closing orb */}
      <div className="relative overflow-hidden">
        <GlowOrb size={500} color="var(--accent)" className="bottom-0 left-1/2 -translate-x-1/2 translate-y-1/3" />
        <Footer />
      </div>
    </main>
  );
}
