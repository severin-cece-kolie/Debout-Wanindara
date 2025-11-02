# Copilot Instructions for Debout-Wanindara

## Project Overview

This codebase contains HTML pages exported via “Save As” with per-page asset folders. The goal is to normalize them into a **Django** project using **Django templates** and **Tailwind CSS via CDN** (no React, no Vite/Webpack). Each legacy HTML page will become a Django template that extends a shared `base.html`, with assets centralized under `core/static/`.

## Architecture & Patterns

* **Templates:**

  * `core/templates/base.html` (layout)
  * `core/templates/includes/` (`_head.html`, `_header.html`, `_footer.html`, `_scripts.html`)
  * `core/templates/pages/*.html` (one file per legacy page)
* **Static Assets:**

  * `core/static/img/` for images (centralized, no per-page duplicates)
  * `core/static/js/` for vanilla JS (optionally `components/` for small modules)
* **Tailwind (CDN):**

  * Use the Tailwind **CDN** in `_head.html`.
  * Prefer utility classes; **no inline styles**; no custom CSS unless strictly necessary.
  * Primary brand color: `#683069` (reference as `primary` via `tailwind.config` script block).

## Developer Workflows

* **Migrating a Page:**

  1. Create `core/templates/pages/<page>.html` that **extends** `base.html`.
  2. Move common `<head>` items to `includes/_head.html`.
  3. Move header/footer into `includes/_header.html` and `includes/_footer.html`.
  4. Convert all styles to **Tailwind classes** (remove inline styles).
  5. Move images to `core/static/img/` and update paths to `{% static 'img/<file>' %}`.
  6. Replace internal links with `{% url '<name>' %}` where routes exist.
  7. Validate responsive behavior and visual parity with the Figma design.
* **Editing Pages:**

  * Update only the content inside `{% block content %}` of `pages/*.html`.
  * For interactivity, add small vanilla JS modules under `core/static/js/` and include them via `_scripts.html`.
* **No Build/Run Scripts:**

  * Tailwind is via CDN for now; no CSS build step.
  * Do not introduce React, Vite, Webpack, or SPA patterns.

## Conventions

* **Naming:** `pages/<name>.html` for each page; `includes/_*.html` for partials.
* **Django Tags:** Always use `{% load static %}`, `{% static %}` for assets, and `{% url %}` for internal routes.
* **Tailwind Only:** Use Tailwind utility classes for spacing, typography, colors, radius, grid/flex, etc.
* **Accessibility:** Provide meaningful `alt` text, visible focus styles, and appropriate `aria-*` attributes.

## Integration Points

* **Backend:** Django templating only; no React components or client-side frameworks.
* **JS:** Vanilla only (optional, minimal). Avoid global state or cross-page coupling.
* **APIs:** None by default. If API calls are added later, document endpoints and auth here.

## Examples

* **Add a new page:**

  1. Create `core/templates/pages/newpage.html`:

     ```django
     {% extends "base.html" %}
     {% block title %}New Page – Debout-Wanindara{% endblock %}
     {% block content %}
       <section class="container py-10 md:py-16">
         <h1 class="text-3xl md:text-5xl font-bold tracking-tight">Titre H1</h1>
         <p class="mt-4 max-w-2xl text-gray-600">Sous-titre…</p>
       </section>
     {% endblock %}
     ```
  2. Place images in `core/static/img/` and reference with `{% static 'img/...' %}`.
  3. If needed, add a small JS file under `core/static/js/` and include it in `includes/_scripts.html`.

* **Translate a legacy block to Tailwind:**

  * Replace `<div style="padding:24px; background:#683069; color:#fff">…</div>` with
    `<div class="p-6 bg-primary text-white rounded-xl">…</div>` (define `primary: "#683069"` in the Tailwind CDN config script inside `_head.html`).

---

If you later introduce a Tailwind build, tests, or additional backend features, update this file to reflect the new workflows and conventions.
