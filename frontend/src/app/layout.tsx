import type { Metadata } from "next";
import { Noto_Serif_SC } from "next/font/google";
import "./globals.css";

const notoSerifSC = Noto_Serif_SC({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-serif-sc",
  display: "swap",
});

export const metadata: Metadata = {
  title: "经典著作索引",
  description:
    "基于 Qwen Embedding + Milvus 构建的语义搜索引擎，在浩瀚典籍中寻觅思想的光芒",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={`${notoSerifSC.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
