# Change log

Completed repository changes. Newest first.

## 2026-10-09 — Keep heading labels visible while editing and on empty headings

Removed the active-line exclusions from the heading level indicator rules.
Empty standalone headings already retain native heading classes; empty bullet
headings lose all heading spans in Obsidian's Live Preview DOM. Added the Rice
Theme Helper plugin to supply a line decoration with the empty heading's level
from the editor document, guarded by Obsidian's syntax tree to exclude code and
frontmatter. The theme renders the fallback label after the list prefix only
when there is no heading span, preventing duplicate indicators. Added background
and typography support for those decorated lines, rebuilt the theme, installed
and enabled the helper in Padua, and documented its installation and verification.

- **Files:** `source/3-markup/headings_inline-title.css`, `theme.css`, `plugin/main.js`, `plugin/manifest.json`, `scripts/verify-headings.py`, `README.md`; Padua's `.obsidian/plugins/obsidian-rice-theme-helper` symlink and `.obsidian/community-plugins.json`.
- **Verification:** `npm run build` — compiled all 30 CSS sources; `node --check plugin/main.js` — passed; `python scripts/verify-headings.py` — passed 37 cases through Obsidian's actual CodeMirror parser in an isolated in-memory editor, checking active/inactive H1–H6 labels, empty standalone/bullet/nested headings, backgrounds/borders, code/frontmatter exclusion, and existing visibility toggles; `git diff --check` — passed. Live DOM inspection also confirmed H3/H5 labels on the user's active list headings and H1 labels on active standalone headings. Temporary parser probes were removed without changing notes or workspace tabs.

## 2026-10-09 — Create the Rice theme with indented heading styling

Copied the complete Shimmering Focus repository at 5.81.0 (`c862131`), matching
Padua's installed theme byte for byte before changes. Named the fork
`obsidian-rice-theme` and extended its editor heading labels, backgrounds, borders,
and letter spacing to list/indented headings. Labels attach to the first heading
span, preserving bullets and indentation and avoiding duplicates on formatted
text. Existing visibility settings and editing behavior are retained. Added a
Linux-compatible build command and adapted the reload recipe for Padua. Preserved
the MIT license, upstream attribution, history, and Style Settings preferences;
the upstream remote is named `upstream`. Installed a symlink from
`/home/malte/Padua/.obsidian/themes/obsidian-rice-theme` to this repository and
activated the custom theme in Padua.

- **Files:** `source/3-markup/headings_inline-title.css`, `source/style-settings.yaml`, `theme.css`, `manifest.json`, `package.json`, `package-lock.json`, `scripts/build.mjs`, `Justfile`, `README.md`; Padua's theme symlink and `.obsidian/appearance.json`.
- **Verification:** `npm ci` — installed the locked dependencies; `npm run build` — compiled all 30 source CSS files successfully; `git diff --check` — passed; `env -u ELECTRON_RUN_AS_NODE obsidian vault=Padua theme` — returned `obsidian-rice-theme`; `env -u ELECTRON_RUN_AS_NODE obsidian vault=Padua dev:errors` — no errors captured. A rebuilt upstream stylesheet exactly matched the previously installed CSS; rule comparison isolated all CSS changes to the requested heading styling. Obsidian CLI DOM inspection confirmed the actual “deadlines” list heading has an H3 label and the same background/border as native headings. Temporary offscreen DOM fixtures in Obsidian verified all six levels, preserved 42px nested indentation, no duplicate labels on split heading spans, hidden labels on active lines, both visibility toggles, and exclusion of ordinary text/code labels; fixtures and temporary body classes were removed afterward.
