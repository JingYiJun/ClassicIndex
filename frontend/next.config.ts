import type { NextConfig } from "next";

const nextConfig: NextConfig = {};

if (process.env.NEXT_OUTPUT === "export") {
  nextConfig.output = "export";
}

export default nextConfig;
