export const navigation = [
  { href: "/documentation.html", label: "Editing these docs", index: "00", group: "Project" },
  { href: "/install.html", label: "FreeBSD guide", index: "01", group: "Start" },
  { href: "/test-host.html", label: "Test VM setup", index: "01a", group: "Start" },
  { href: "/dependencies.html", label: "Dependencies", index: "02", group: "Start" },
  { href: "/getting-started.html", label: "Getting Started", index: "03", group: "Start" },
  { href: "/development-progress.html", label: "Development Progress", index: "04", group: "Project" },
  { href: "/keybinds.html", label: "Keybindings", index: "05", group: "Use" },
  { href: "/configuration.html", label: "Configuration", index: "06", group: "Customize" },
  { href: "/theming.html", label: "Theming", index: "07", group: "Customize" },
  { href: "/control-center.html", label: "Control Center", index: "08", group: "Use" },
  { href: "/settings.html", label: "Settings", index: "09", group: "Use" },
  { href: "/patches.html", label: "How It Works", index: "10", group: "Project" },
  { href: "/troubleshooting.html", label: "Troubleshooting", index: "11", group: "Help" }
] as const;

export const projectLinks = [
  { href: "https://github.com/lirux9873/dwm-c9-freebsd", label: "GitHub" },
  { href: "https://github.com/lirux9873/dwm-c9-freebsd/blob/main/docs/FREEBSD-CI-REVIEW.md", label: "Native CI evidence" }
] as const;
