import { locales, type Locale } from "@/i18n/routing";
import { notFound } from "next/navigation";
import { ClientIntlProvider } from "./ClientIntlProvider";

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  if (!locales.includes(locale as Locale)) {
    notFound();
  }

  return (
    <ClientIntlProvider locale={locale as Locale}>
      {children}
    </ClientIntlProvider>
  );
}
