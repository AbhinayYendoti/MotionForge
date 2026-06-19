import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ["@remotion/bundler", "@remotion/renderer", "@rspack/core", "esbuild"],
  experimental: {
    serverActions: {
      bodySizeLimit: "12mb"
    }
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "utfs.io" },
      { protocol: "https", hostname: "uploadthing.com" },
      { protocol: "https", hostname: "images.unsplash.com" }
    ]
  }
};

export default nextConfig;
