# Editing and publishing documentation

The website is published at [lirux9873.github.io/dwm-c9-freebsd](https://lirux9873.github.io/dwm-c9-freebsd/).
Astro turns Markdown and page templates into static HTML, CSS and JavaScript.
Node.js is a documentation build dependency; it is not required to run dwm.

## Preview locally

Install Node.js 24 and npm. From the repository root:

```sh
cd docs
npm ci
npm run dev
```

Open the local URL printed by Astro, including `/dwm-c9-freebsd/`.
The preview updates when you save a source file. To validate the finished site:

```sh
npm run build
npm run preview
```

The generated files are in `docs/dist/`; do not commit them.

## Where to edit

- `docs/FREEBSD.md` supplies both the home page and `install.html`.
- `docs/DOCUMENTATION.md` supplies this page.
- `docs/src/content/*.md` contains inherited upstream reference text.
- `docs/src/pages/*.astro` maps content to website routes.
- `docs/src/layouts/DocsLayout.astro` supplies shared branding and navigation.
- `docs/src/data/navigation.ts` defines navigation entries.
- `docs/src/styles/global.css` supplies styling.

A Markdown file outside `src/pages` needs a page that imports its `Content`
component before it appears on the site. Internal links and images must include
the `/dwm-c9-freebsd/` prefix or use a relative URL. Navigation entries use
root-relative paths; the shared layout adds the configured prefix.

## Publishing

GitHub Pages uses **GitHub Actions** as its build source. The
**Build and Deploy Astro Docs** workflow validates pull requests and publishes
documentation changes pushed to `main`. It can also be run manually on `main`.
Pull requests and other branches cannot deploy the site.

`docs/astro.config.mjs` sets the site origin to `https://lirux9873.github.io`
and the base path to `/dwm-c9-freebsd`. There is no custom domain or CNAME file.
The workflow may build on Ubuntu: its output is platform-independent static
website files. The separate Desktop smoke workflow tests dwm inside FreeBSD.

The FreeBSD port is still in progress. Other inherited pages carry a prominent
Fedora reference notice until their content has been adapted and validated.
