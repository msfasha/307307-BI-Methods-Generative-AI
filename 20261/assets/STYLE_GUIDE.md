# Course document style

The approved style uses soft surfaces and dark text. Avoid large saturated purple panels. This is the Applied Statistics course's teaching-document style, inspired by University of Petra branding; it is not a substitute for an official university identity manual.

## Exact color specification

| Role | Hex | Usage |
|---|---|---|
| Reading surface | `#FFFFFF` | Main document background |
| Main title surface | `#F5EDF4` | Pale lavender panel |
| Main title and H2 text | `#493347` | Dark plum on pale surfaces |
| Subtitle | `#655263` | Text inside the main title panel |
| H2 surface | `#F7F3F7` | Very light lavender section panel |
| H2 left rule | `#C8ABC3` | Thin muted accent |
| Body and H3/H4 text | `#2F343B` | Dark neutral text |
| Secondary text | `#56616D` | Breadcrumb separators, metadata, captions |
| Links | `#356B8C` | Blue links; underline breadcrumb links |
| Link hover | `#244D68` | Darker blue |
| Petra brand accent | `#A83296` | Thin line above the main title |
| Table header | `#F3F4F6` | Neutral surface |
| Table divider | `#DEE2E6` | Subtle horizontal rule |
| Code left rule | `#CED4DA` | Neutral code-block edge |
| Note surface | `#EFF4F7` | Soft blue callout header |
| Note left rule | `#6C91A8` | Muted blue accent |

Use the hex values as authoritative. `#A83296` is RGB **168, 50, 150**. White body areas, quiet panels, and ample space should dominate the page; saturated purple should occupy very little area.

## Palette and heading hierarchy

- Main title background: **#F5EDF4**; title text: **#493347**.
- Section (H2) background: **#F7F3F7**, with a thin **#C8ABC3** left rule.
- Subheadings (H3 and below): plain dark text, without filled panels or shadows.
- Body text: **#2F343B** on white; secondary text: **#56616D**.
- Links: **#356B8C**, with visible underlines in breadcrumbs.
- University of Petra purple **#A83296** appears as a thin accent above the main title. The former bright **#D070D0** accent is no longer used for large decorative areas.
- Keep breadcrumbs above the main title panel, on the white reading surface. Retain real Markdown headings and the normal document navigation.
- Use the same restrained palette for HTML documents, Reveal slides, and future exports. Preserve adequate contrast in captions, subtitles, and metadata.

## Layout and readability

- Place breadcrumbs on the white surface **above** the title panel. Use readable blue links and dark secondary text; do not place blue text over saturated purple.
- Main title: 3 px brand-purple top rule, padding `1.5rem 1.75rem`, and 8 px lower corner rounding. No heavy shadow.
- H2: 3 px muted left rule, padding `.75rem 1.1rem`, and a light fill. Leave about `2.3rem` of space before the section.
- H3/H4: plain dark headings. Use size, weight, and spacing to show hierarchy; do not repeat the filled H2 treatment.
- Preserve the document's normal typeface and font size. The stylesheet changes color and hierarchy, not the underlying content typography. For other systems, use a readable sans-serif font and a comfortable body line height around 1.5–1.65.
- Keep tables neutral and code readable. Color should support meaning rather than decorate every element.
- Keep captions and navigation readable at smaller screen sizes. On narrow screens, reduce panel padding rather than shrink essential text excessively.
- Use text labels, shapes, or line styles alongside color in charts.

The title pairing (`#493347` on `#F5EDF4`) has approximately **9.9:1** contrast; the subtitle pairing has approximately **6.2:1**. Do not use pale accent colors as body text on white. These pair checks do not replace a full accessibility review of each finished document.

## Using the scheme in another project

1. Copy `petra-brand.css` into the new project's `assets/` folder.
2. For a Quarto website, add the following to `_quarto.yml`:

```yaml
format:
  html:
    css: assets/petra-brand.css
```

For a standalone QMD, put the equivalent `format` block in its YAML header and adjust the relative path from that file. Existing format settings can stay in place; add the `css` setting to the existing HTML configuration. For Reveal slides, add the stylesheet under the document's `format.revealjs.css` setting.

3. Use ordinary Markdown headings: the document title, `##` for sections, and `###` for subsections. Avoid embedded inline color rules.
4. Render a sample with a long title, breadcrumb, subtitle, table, note, and chart. Inspect both narrow and wide layouts before publishing.
5. For Word, PowerPoint, or PDF templates, recreate the color roles and hierarchy in that format's styles. A CSS file directly styles HTML/Reveal output; it does not automatically style a separate LaTeX or Word export.

The CSS selectors target Quarto's HTML structure. For a different publishing system, map the same visual roles to that system's elements. Keep one shared stylesheet rather than copying custom style blocks into each document. If an older page still shows the former palette, refresh its cached stylesheet.

## Figures and business cases

- Open lessons with a concrete question and explain that students will return to it as they learn each tool.
- Use a purposeful business illustration when it clarifies the observational unit or the variables. A reusable pattern is business context → data record → question → analysis → interpretation.
- Label conceptual illustrations so they cannot be mistaken for observed evidence.
- Charts use analytical colors suited to their purpose: blue/orange, categorical palettes, meaningful diverging scales, or neutral reference lines. Do not force them into the Petra purple palette.
- Book figure excerpts retain their original colors and attribution.

## Shared implementation

`assets/petra-brand.css` is the master stylesheet. Keep its copies synchronized in `20261/assets`, `beta/assets`, `surveys/assets`, the module assets folder, and generated site assets. The project defaults and existing QMDs link their project stylesheet. Beta's SCSS files support HTML and Reveal slides.

Do not embed separate heading-color rules in individual QMDs. Existing rendered HTML pages also load the shared stylesheet; branding changes can preserve their generated charts and results. Render edited lesson content from its QMD source. Existing PDF exports are static snapshots; apply the current style when producing fresh exports.
