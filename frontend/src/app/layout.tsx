import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "Ecclesia Next", description: "Plataforma de gestão eclesiástica" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt">
      <body>{children}</body>
    </html>
  );
}
