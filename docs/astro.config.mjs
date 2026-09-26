import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://lirux9873.github.io",
  base: "/dwm-c9-freebsd",
  output: "static",
  build: {
    format: "file"
  },
  markdown: {
    shikiConfig: {
      theme: "github-dark-default",
      wrap: true
    }
  }
});
