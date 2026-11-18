// Build Arabic RTL study book (DOCX) from simple markup files.
const fs = require('fs');
const path = require('path');
const D = require('docx');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, AlignmentType, HeadingLevel, LevelFormat, Header, Footer, PageNumber, PageBreak, VerticalAlign,
} = D;

const ROOT = __dirname;
const AR = 'Arial';       // Arabic (complex script) font - present on Windows and macOS
const LAT = 'Calibri';    // Latin font
const CODE = 'Consolas';
const C = { plum: '493347', body: '2F343B', sec: '56616D', brand: 'A83296', title: 'F5EDF4', sect: 'F7F3F7', rule: 'C8ABC3', blue: '356B8C',
  note: 'EFF4F7', noteRule: '6C91A8', hdr: 'F3F4F6', div: 'DEE2E6', rose: '9C5A6E', warn: 'F8EEF1', mauve: '8A6884' };
const PAGE_W = 11906, MARGIN = 1134, CONTENT_W = PAGE_W - 2 * MARGIN; // A4

const ORD = ['', 'الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس', 'السادس', 'السابع', 'الثامن', 'التاسع', 'العاشر'];

// ---------- inline text -> runs (auto split Arabic / Latin) ----------
const LATIN_RE = /([A-Za-z][A-Za-z0-9]*(?:[ \-_\/.+’'&:,](?=[A-Za-z0-9])[A-Za-z0-9]*)*(?:\(\))?)/g;

function mkRun(text, o) {
  const latin = /^[A-Za-z]/.test(text);
  const size = o.size || 24;
  const base = {
    text, bold: !!o.bold, italics: !!o.italics, color: o.color || C.body, size,
    boldComplexScript: !!o.bold, sizeComplexScript: size,
    font: { ascii: o.font || LAT, hAnsi: o.font || LAT, cs: AR, eastAsia: AR },
  };
  if (!latin && !o.ltr) base.rightToLeft = true;
  return new TextRun(base);
}
function splitScript(text, o) {
  if (o.code) return [new TextRun({ text, font: CODE, size: (o.size || 24) - 2, color: C.body, shading: { type: ShadingType.CLEAR, fill: C.hdr, color: 'auto' } })];
  const out = []; let last = 0; let m;
  LATIN_RE.lastIndex = 0;
  while ((m = LATIN_RE.exec(text))) {
    if (m.index > last) out.push(mkRun(text.slice(last, m.index), o));
    out.push(mkRun(m[0], o));
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push(mkRun(text.slice(last), o));
  return out;
}
function inline(text, o = {}) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/);
  const runs = [];
  for (const p of parts) {
    if (!p) continue;
    if (p.startsWith('**')) runs.push(...splitScript(p.slice(2, -2), { ...o, bold: true }));
    else if (p.startsWith('`')) runs.push(...splitScript(p.slice(1, -1), { ...o, code: true }));
    else runs.push(...splitScript(p, o));
  }
  return runs;
}

// ---------- block builders ----------
let numCount = 0; const numConfigs = [];
function newNumbering() {
  const ref = `num${++numCount}`;
  numConfigs.push({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.START,
    style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] });
  return ref;
}
const BUL = 'bul';
numConfigs.push({ reference: BUL, levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.START,
  style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] });

const P = (children, extra = {}) => new Paragraph({ bidirectional: true, spacing: { after: 120, line: 340 }, ...extra, children });

function para(text, o = {}) { return P(inline(text, o), o.p || {}); }
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, bidirectional: true, keepNext: true,
    shading: { type: ShadingType.CLEAR, fill: C.sect, color: 'auto' },
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: C.rule, space: 4 } },
    spacing: { before: 360, after: 160 }, children: inline(text, { bold: true, color: C.plum, size: 30, font: 'Cambria' }) });
}
function h3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, bidirectional: true, keepNext: true, spacing: { before: 260, after: 100 },
    children: inline(text, { bold: true, color: C.body, size: 26, font: 'Cambria' }) });
}
function codeBlock(lines) {
  return lines.map((ln, i) => new Paragraph({ bidirectional: false, alignment: AlignmentType.LEFT, keepLines: true, spacing: { after: 0, line: 276 },
    shading: { type: ShadingType.CLEAR, fill: C.hdr, color: 'auto' },
    indent: { left: 120, right: 120 },
    children: [new TextRun({ text: ln === '' ? ' ' : ln, font: CODE, size: 20, color: C.body })],
    ...(i === lines.length - 1 ? { spacing: { after: 200, line: 276 } } : {}) }));
}
function pngSize(file) {
  const b = fs.readFileSync(file); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function figure(src, widthCm, caption) {
  const file = path.join(ROOT, src); const { w, h } = pngSize(file);
  const wpx = Math.round(widthCm * 37.8), hpx = Math.round(wpx * h / w);
  const ext = src.endsWith('.jpg') ? 'jpg' : 'png';
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 80 },
      children: [new ImageRun({ type: ext, data: fs.readFileSync(file), transformation: { width: wpx, height: hpx },
        altText: { title: caption, description: caption, name: path.basename(src) } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, bidirectional: true, spacing: { after: 220 }, children: inline(caption, { size: 19, color: C.sec }) }),
  ];
}
const thin = (color) => ({ style: BorderStyle.SINGLE, size: 4, color });
function cellBorders(color) { return { top: thin(color), bottom: thin(color), left: thin(color), right: thin(color) }; }

function table(rows, cols) {
  const n = rows[0].length;
  const pct = cols && cols.length === n ? cols : Array(n).fill(100 / n);
  const widths = pct.map(p => Math.round(CONTENT_W * p / 100));
  widths[n - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: widths, visuallyRightToLeft: true,
    rows: rows.map((r, ri) => new TableRow({ tableHeader: ri === 0, cantSplit: true, children: r.map((c, ci) => new TableCell({
      width: { size: widths[ci], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      borders: cellBorders(C.div),
      shading: ri === 0 ? { type: ShadingType.CLEAR, fill: C.hdr, color: 'auto' } : undefined,
      margins: { top: 70, bottom: 70, left: 110, right: 110 },
      children: [new Paragraph({ bidirectional: true, spacing: { after: 0, line: 300 }, children: inline(c, { size: 21, bold: ri === 0 }) })],
    })) })) });
}

const KINDS = {
  note: { fill: C.note, rule: C.noteRule, label: 'ملاحظة', color: C.blue },
  ex: { fill: C.sect, rule: C.rule, label: 'مثال', color: C.plum },
  warn: { fill: C.warn, rule: C.rose, label: 'تنبيه', color: C.rose },
  ext: { fill: C.hdr, rule: C.mauve, label: 'للتوسع', color: C.mauve },
};
function callout(kind, title, innerLines) {
  const k = KINDS[kind];
  const kids = [];
  if (title) kids.push(new Paragraph({ bidirectional: true, keepNext: true, spacing: { after: 80 }, children: inline(title, { bold: true, color: k.color, size: 23 }) }));
  kids.push(...parseBlocks(innerLines, true));
  if (kids.length === 0) kids.push(new Paragraph({ children: [] }));
  return [new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], visuallyRightToLeft: true,
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA },
      borders: { top: thin(k.rule), bottom: thin(k.rule), left: { style: BorderStyle.SINGLE, size: 24, color: k.rule }, right: { style: BorderStyle.SINGLE, size: 24, color: k.rule } },
      shading: { type: ShadingType.CLEAR, fill: k.fill, color: 'auto' }, margins: { top: 120, bottom: 100, left: 200, right: 200 }, children: kids })] })] }),
    new Paragraph({ spacing: { after: 120 }, children: [] })];
}

// ---------- markup parser ----------
function parseBlocks(lines, inBox = false) {
  const out = []; let i = 0; let pendingCols = null;
  while (i < lines.length) {
    const ln = lines[i];
    if (ln.trim() === '') { i++; continue; }
    if (ln.startsWith('%cols ')) { pendingCols = ln.slice(6).split(',').map(Number); i++; continue; }
    if (ln.startsWith('```')) {
      const code = []; i++;
      while (i < lines.length && !lines[i].startsWith('```')) code.push(lines[i++]);
      i++; out.push(...codeBlock(code)); continue;
    }
    if (ln.startsWith(':::')) {
      const m = ln.match(/^:::(\w+)\s*(.*)$/); const inner = []; i++;
      while (i < lines.length && lines[i].trim() !== ':::') inner.push(lines[i++]);
      i++; out.push(...callout(m[1], m[2], inner)); continue;
    }
    if (ln.startsWith('### ')) { out.push(h3(ln.slice(4))); i++; continue; }
    if (ln.startsWith('## ')) { out.push(h2(ln.slice(3))); i++; continue; }
    if (ln.startsWith('---')) { out.push(new Paragraph({ children: [new PageBreak()] })); i++; continue; }
    const img = ln.match(/^!\[(.*?)\]\((.+?)\|(\d+(?:\.\d+)?)\|(.*)\)$/);
    if (img) { out.push(...figure(img[2], parseFloat(img[3]), img[4])); i++; continue; }
    if (ln.startsWith('|')) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith('|')) {
        if (!/^\|[\s\-|]+\|?$/.test(lines[i])) rows.push(lines[i].replace(/^\||\|$/g, '').split('|').map(s => s.trim()));
        i++;
      }
      out.push(table(rows, pendingCols)); pendingCols = null;
      out.push(new Paragraph({ spacing: { after: 160 }, children: [] })); continue;
    }
    if (/^- /.test(ln)) {
      while (i < lines.length && /^- /.test(lines[i])) {
        out.push(new Paragraph({ bidirectional: true, numbering: { reference: BUL, level: 0 }, spacing: { after: 80, line: 336 }, children: inline(lines[i].slice(2)) })); i++;
      }
      continue;
    }
    if (/^\d+\. /.test(ln)) {
      const ref = newNumbering();
      while (i < lines.length && (/^\d+\. /.test(lines[i]) || /^ {2,}- /.test(lines[i]))) {
        if (/^\d+\. /.test(lines[i])) {
          out.push(new Paragraph({ bidirectional: true, numbering: { reference: ref, level: 0 }, keepNext: true, spacing: { before: 80, after: 60, line: 336 }, children: inline(lines[i].replace(/^\d+\. /, '')) }));
        } else {
          out.push(new Paragraph({ bidirectional: true, indent: { left: 900 }, spacing: { after: 30, line: 320 }, children: inline(lines[i].replace(/^ +- /, '')) }));
        }
        i++;
      }
      continue;
    }
    // paragraph (join consecutive plain lines)
    const buf = [ln]; i++;
    while (i < lines.length && lines[i].trim() !== '' && !/^(#|- |\d+\. |```|:::|\||!\[|%|---)/.test(lines[i])) buf.push(lines[i++]);
    out.push(para(buf.join(' ')));
  }
  return out;
}

// ---------- chapter header ----------
function chapterHeader(meta) {
  const num = parseInt(meta.chapter, 10);
  const kids = [
    new Paragraph({ bidirectional: true, spacing: { after: 60 }, children: inline(`الفصل ${ORD[num] || num}`, { size: 24, color: C.sec, bold: true }) }),
    new Paragraph({ heading: HeadingLevel.HEADING_1, bidirectional: true, keepNext: true, spacing: { after: 60 }, children: inline(meta.title, { size: 44, bold: true, color: C.plum, font: 'Cambria' }) }),
    new Paragraph({ bidirectional: false, alignment: AlignmentType.RIGHT, spacing: { after: 120 }, children: [new TextRun({ text: meta.en, font: 'Cambria', size: 28, color: '655263' })] }),
  ];
  if (meta.source) kids.push(new Paragraph({ bidirectional: true, spacing: { after: 0 }, children: inline(meta.source, { size: 19, color: C.sec }) }));
  return [new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], visuallyRightToLeft: true,
    rows: [new TableRow({ children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA },
      borders: { top: { style: BorderStyle.SINGLE, size: 24, color: C.brand }, bottom: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } },
      shading: { type: ShadingType.CLEAR, fill: C.title, color: 'auto' }, margins: { top: 240, bottom: 220, left: 300, right: 300 }, children: kids })] })] }),
    new Paragraph({ spacing: { after: 200 }, children: [] })];
}

function loadFile(f) {
  const raw = fs.readFileSync(path.join(ROOT, f), 'utf8').split('\n');
  const meta = {}; const body = [];
  for (const l of raw) { const m = l.match(/^%(chapter|title|en|source) (.*)$/); if (m) meta[m[1]] = m[2]; else if (l.trim() === '%frontmatter') meta.front = true; else body.push(l); }
  return { meta, body };
}

// ---------- glossary appendix ----------
function glossary() {
  const rows = fs.readFileSync(path.join(ROOT, 'glossary.tsv'), 'utf8').trim().split('\n').map(l => l.split('\t'))
    .sort((a, b) => a[0].toLowerCase().localeCompare(b[0].toLowerCase()));
  const header = ['English', 'المصطلح العربي', 'المعنى باختصار', 'الفصل'];
  const trs = [header, ...rows.map(r => [r[0], r[4] === 'Y' ? `${r[1]} ★` : r[1], r[2], r[3]])];
  return [
    new Paragraph({ heading: HeadingLevel.HEADING_1, bidirectional: true, pageBreakBefore: true, spacing: { after: 160 }, children: inline('فهرس المصطلحات (إنجليزي ← عربي)', { size: 40, bold: true, color: C.plum, font: 'Cambria' }) }),
    para('مرتّب أبجديًّا بالإنجليزية. العلامة ★ تعني أن الترجمة العربية المقترحة **قيد المراجعة**.', { size: 21, color: C.sec }),
    table(trs, [24, 26, 40, 10]),
  ];
}

// ---------- cover ----------
function cover() {
  const mid = (t, o) => new Paragraph({ alignment: AlignmentType.CENTER, bidirectional: true, spacing: { after: o.after || 160 }, children: inline(t, o) });
  return [
    new Paragraph({ spacing: { before: 1800 }, children: [] }),
    new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], visuallyRightToLeft: true,
      rows: [new TableRow({ children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA },
        borders: { top: { style: BorderStyle.SINGLE, size: 24, color: C.brand }, bottom: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } },
        shading: { type: ShadingType.CLEAR, fill: C.title, color: 'auto' }, margins: { top: 500, bottom: 500, left: 400, right: 400 },
        children: [
          mid('الذكاء الاصطناعي الوكيلي وحوكمة الذكاء الاصطناعي', { size: 52, bold: true, color: C.plum, font: 'Cambria', after: 200 }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: 'Agentic AI and AI Governance', font: 'Cambria', size: 34, color: '655263' })] }),
          mid('دليل الطالب الدراسي', { size: 32, color: C.body, bold: true }),
        ] })] })] }),
    new Paragraph({ spacing: { before: 700 }, children: [] }),
    mid('المقرر 307307: أساليب ذكاء الأعمال للذكاء الاصطناعي التوليدي', { size: 26, color: C.body }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: 'BI Methods for Generative AI', font: LAT, size: 24, color: C.sec })] }),
    mid('جامعة البترا', { size: 26, color: C.body }),
    new Paragraph({ spacing: { before: 900 }, children: [] }),
    mid('نسخة تجريبية: الفصل 3 (الذاكرة وهندسة السياق) وفهرس المصطلحات', { size: 22, color: C.rose, bold: true }),
    new Paragraph({ children: [new PageBreak()] }),
  ];
}

// ---------- assemble ----------
function main() {
  const files = process.argv.slice(2);
  const children = [...cover()];
  let first = true;
  for (const f of files) {
    const { meta, body } = loadFile(f);
    if (meta.front) { children.push(...parseBlocks(body)); children.push(new Paragraph({ children: [new PageBreak()] })); continue; }
    children.push(...chapterHeader(meta)); children.push(...parseBlocks(body));
  }
  children.push(...glossary());

  const hdrPar = new Paragraph({ bidirectional: true, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.rule, space: 4 } },
    children: inline('307307 — أساليب ذكاء الأعمال للذكاء الاصطناعي التوليدي | دليل الطالب', { size: 17, color: C.sec }) });
  const ftrPar = new Paragraph({ alignment: AlignmentType.CENTER, bidirectional: true,
    children: [...inline('صفحة ', { size: 18, color: C.sec }), new TextRun({ children: [PageNumber.CURRENT], size: 18, color: C.sec, font: LAT })] });

  const doc = new Document({
    creator: 'University of Petra - 307307', title: 'الذكاء الاصطناعي الوكيلي وحوكمة الذكاء الاصطناعي: دليل الطالب',
    styles: {
      default: { document: { run: { font: { ascii: LAT, hAnsi: LAT, cs: AR }, size: 24, sizeComplexScript: 24, color: C.body, language: { value: 'en-US', bidirectional: 'ar-SA' } } } },
      paragraphStyles: [
        { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: 'Cambria', size: 40, bold: true, color: C.plum }, paragraph: { spacing: { before: 0, after: 120 }, keepNext: true, outlineLevel: 0 } },
        { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: 'Cambria', size: 30, bold: true, color: C.plum }, paragraph: { spacing: { before: 360, after: 160 }, keepNext: true, outlineLevel: 1 } },
        { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: 'Cambria', size: 26, bold: true, color: C.body }, paragraph: { spacing: { before: 260, after: 100 }, keepNext: true, outlineLevel: 2 } },
      ],
    },
    numbering: { config: numConfigs },
    sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1200, left: MARGIN, right: MARGIN } } },
      headers: { default: new Header({ children: [hdrPar] }) }, footers: { default: new Footer({ children: [ftrPar] }) }, children }],
  });
  Packer.toBuffer(doc).then(b => { fs.writeFileSync(path.join(ROOT, 'out.docx'), b); console.log('written', b.length); });
}
main();
