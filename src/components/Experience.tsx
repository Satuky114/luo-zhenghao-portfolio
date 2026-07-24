"use client";

import { useI18n } from "@/app/[locale]/ClientIntlProvider";
import { SectionWrapper } from "@/components/ui/SectionWrapper";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { Timeline } from "@/components/ui/Timeline";

export function Experience() {
  const { t, locale } = useI18n();

  const items = [
    {
      date: t("experience.party.period"),
      title: t("experience.party.role"),
      subtitle: t("experience.party.org"),
      description: (
        <ul className="list-disc list-inside space-y-1">
          <li>{t("experience.party.desc1")}</li>
          <li>{t("experience.party.desc2")}</li>
        </ul>
      ),
      isLatest: true,
    },
    {
      date: t("education.period"),
      title: t("education.major"),
      subtitle: t("education.school"),
      description: (
        <p>
          {locale === "zh"
            ? "主修课程：新媒体运营、传播学概论、网络传播学、数字媒体内容生产、短视频创作、网页制作与建设"
            : "Core courses: New Media Operations, Communication Theory, Digital Media Production, Short Video Creation, Web Development"}
        </p>
      ),
    },
    {
      date: locale === "zh" ? "荣誉" : "Honors",
      title: t("education.honors"),
      description: null,
      isLatest: false,
    },
  ];

  return (
    <SectionWrapper id="experience" orb={{ color: "#F59E0B", size: 340, position: "top-0 -left-20" }} gradientBottom>
      <SectionHeading number="05" title={t("experience.title")} />

      <div className="max-w-3xl mx-auto">
        <Timeline items={items} />
      </div>

      {/* AI Research section inline */}
      <div className="max-w-3xl mx-auto mt-20 pt-12 border-t border-border">
        <h3 className="text-xl md:text-2xl font-bold text-text-primary mb-6">
          {t("aiResearch.title")}
        </h3>
        <div className="space-y-4">
          {[
            t("aiResearch.desc1"),
            t("aiResearch.desc2"),
            t("aiResearch.desc3"),
          ].map((desc, i) => (
            <div key={i} className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-accent/10 text-accent text-xs font-mono flex items-center justify-center">
                {i + 1}
              </span>
              <p className="text-text-secondary leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </SectionWrapper>
  );
}
