import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "罗政皓 | Luo Zhenghao — AI Content Creator",
  description:
    "AI内容运营 / AIGC创作者 — 西南民族大学网络与新媒体专业。用AI赋予内容生命力。",
  keywords: ["罗政皓", "AI内容运营", "AIGC", "个人作品集", "Portfolio", "Luo Zhenghao"],
  openGraph: {
    title: "罗政皓 | AI Content Creator",
    description: "AI内容运营 / AIGC创作者 — 用AI赋予内容生命力",
    type: "website",
    locale: "zh_CN",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html className="h-full">
      <body className="min-h-full flex flex-col antialiased">{children}</body>
    </html>
  );
}
