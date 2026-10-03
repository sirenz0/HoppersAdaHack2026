# Design

This folder is the bridge between the Figma design and the code.

## Files

- `tokens.css` — color/font/spacing variables exported from Figma styles.
  This is a reference copy; the file actually loaded by the site is
  `app/static/css/tokens.css`. When Figma values change, update both
  (or just copy this file over the static one).
- `exports/` — drop PNG/SVG exports from Figma here (icons, logos,
  illustrations) before wiring them into templates/CSS.

## Workflow once the Figma file is ready

1. Share the Figma file link so it can be reviewed against the current
   pages (`app/templates/`).
2. Pull colors/fonts from Figma's local styles into `tokens.css`.
3. Export any icons/images into `exports/` and reference them from
   templates via `{{ url_for('static', filename='img/...') }}` (add an
   `app/static/img/` folder once there are real assets to serve).
4. Adjust page markup in `app/templates/*.html` and layout rules in
   `app/static/css/style.css` to match the Figma layout — `style.css`
   should only ever read colors/spacing through `var(--token-name)`,
   never hardcode new values, so future design tweaks stay a one-file
   change in `tokens.css`.
