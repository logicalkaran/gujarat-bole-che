# Gujarat Bole Che — Blogger redesign

This package is a visual upgrade layer for the existing Blogger theme. It preserves existing Blogger posts/widgets and adds a modern mobile-first presentation.

## Included
- blogger-theme-upgrade.css — modern responsive visual layer
- blogger-theme-upgrade.js — lightweight client-side article filtering
- blogger-interactive-gadget.html — homepage hero, category cards and search UI

## Apply safely
1. In Blogger, Theme -> More -> Backup -> Download the current theme first.
2. Theme -> Edit HTML.
3. Add the CSS inside the existing <b:skin> section, preferably near the end.
4. Add the JavaScript before </body>.
5. Add the interactive HTML through Layout -> Add a Gadget -> HTML/JavaScript, preferably above the Blog Posts widget.
6. Save and test on phone and desktop.

Do not delete the existing widgets until the new layout is verified.

## Next phase
After visual approval: clean placeholder SEO metadata, add About/Contact/Privacy/Disclaimer pages, then connect Blogger API and the content pipeline. Automated publishing stays disabled until that stage is explicitly enabled.
