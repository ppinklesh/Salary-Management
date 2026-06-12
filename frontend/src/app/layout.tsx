import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { Sidebar } from "@/components/layout/sidebar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Salary Management — ACME Corp",
  description: "Employee salary management tool for HR",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex h-screen overflow-hidden antialiased">
        <Sidebar />
        <main className="min-h-0 flex-1 overflow-y-auto">
          <div className="container mx-auto p-6 max-w-7xl">{children}</div>
        </main>
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
