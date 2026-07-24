"use client";

import { motion } from "framer-motion";
import { Mail, Phone, Globe, FileText } from "lucide-react";
import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { SectionWrapper } from "@/components/ui/SectionWrapper";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export function Contact() {
  const { t, locale } = useI18n();
  const reduced = useReducedMotion();

  const contacts = [
    {
      icon: <Mail size={20} />,
      label: t("contact.email"),
      value: "lzh061104lzh@163.com",
      href: "mailto:lzh061104lzh@163.com",
    },
    {
      icon: <Phone size={20} />,
      label: t("contact.phone"),
      value: "18880407747",
      href: "tel:18880407747",
    },
    {
      icon: <Globe size={20} />,
      label: t("contact.github"),
      value: "satuky114",
      href: "https://github.com/satuky114",
    },
  ];

  return (
    <SectionWrapper id="contact" className="bg-bg-elevated/50" orb={{ color: "var(--accent)", size: 360, position: "bottom-0 -right-24" }}>
      <SectionHeading
        number="06"
        title={t("contact.title")}
        align="center"
        className="text-center"
      />

      <div className="max-w-2xl mx-auto">
        {/* Contact cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
          {contacts.map((item, i) => (
            <motion.a
              key={i}
              href={item.href}
              target={item.href.startsWith("http") ? "_blank" : undefined}
              rel="noopener noreferrer"
              initial={reduced ? {} : { opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              whileHover={{ y: -4, borderColor: "var(--accent)" }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
              className="flex flex-col items-center gap-2 p-5 rounded-xl border border-border bg-bg-surface hover:bg-bg-elevated transition-colors text-center group"
            >
              <span className="text-text-tertiary group-hover:text-accent transition-colors">
                {item.icon}
              </span>
              <span className="text-xs font-mono text-text-tertiary uppercase tracking-wider">
                {item.label}
              </span>
              <span className="text-sm font-medium text-text-primary break-all">
                {item.value}
              </span>
            </motion.a>
          ))}
        </div>

        {/* Resume download */}
        <motion.a
          href="/resume.pdf"
          download
          initial={reduced ? {} : { opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          whileHover={{ scale: 1.02 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="flex items-center justify-center gap-2 mx-auto max-w-xs px-6 py-3 bg-accent hover:bg-accent/90 text-white font-medium rounded-xl transition-all hover:shadow-[0_0_30px_var(--accent-glow)]"
        >
          <FileText size={18} />
          {locale === "zh" ? "下载简历 PDF" : "Download Resume PDF"}
        </motion.a>
      </div>
    </SectionWrapper>
  );
}
