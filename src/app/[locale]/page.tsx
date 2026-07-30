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

export default function HomePage() {
  return (
    <main className="relative z-[1]">
      {/* Global scan-line decoration */}
      <div className="scan-line" />

      <Nav />
      <Hero />
      <About />
      <div className="section-alt">
        <Projects />
      </div>
      <ContentCreation />
      <div className="section-alt">
        <Skills />
      </div>
      <Experience />
      <Contact />

      {/* Footer */}
      <Footer />
    </main>
  );
}
