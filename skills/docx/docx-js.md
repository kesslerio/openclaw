# DOCX Library Tutorial

Generate .docx files with JavaScript/TypeScript.

## Setup

Assumes docx is already installed globally
If not installed: `npm install -g docx`

```javascript
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  ImageRun,
  Header,
  Footer,
  AlignmentType,
  PageOrientation,
  LevelFormat,
  ExternalHyperlink,
  InternalHyperlink,
  TableOfContents,
  HeadingLevel,
  BorderStyle,
  WidthType,
  UnderlineType,
  ShadingType,
  VerticalAlign,
  PageNumber,
  PageBreak,
} = require("docx");

// Create & Save
const doc = new Document({
  sections: [
    {
      children: [
        /* content */
      ],
    },
  ],
});
Packer.toBuffer(doc).then((buffer) => fs.writeFileSync("doc.docx", buffer));
```

## Text & Formatting

```javascript
// Basic text with formatting options
new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 200, after: 200 },
  children: [
    new TextRun({ text: "Bold", bold: true }),
    new TextRun({ text: "Italic", italics: true }),
    new TextRun({ text: "Colored", color: "FF0000", size: 28, font: "Arial" }),
  ],
});
```

## Lists

```javascript
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullet-list",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
      {
        reference: "numbered-list",
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
    ],
  },
  sections: [
    {
      children: [
        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [new TextRun("First bullet point")],
        }),
      ],
    },
  ],
});
```

## Tables

```javascript
new Table({
  columnWidths: [4680, 4680],
  rows: [
    new TableRow({
      children: [
        new TableCell({
          width: { size: 4680, type: WidthType.DXA },
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
          children: [new Paragraph({ children: [new TextRun({ text: "Header", bold: true })] })],
        }),
      ],
    }),
  ],
});
```

## Images

```javascript
new Paragraph({
  children: [
    new ImageRun({
      type: "png", // REQUIRED
      data: fs.readFileSync("image.png"),
      transformation: { width: 200, height: 150 },
      altText: { title: "Logo", description: "Company logo", name: "Name" },
    }),
  ],
});
```

## Page Breaks

```javascript
// Manual page break
new Paragraph({ children: [new PageBreak()] });

// Page break before paragraph
new Paragraph({
  pageBreakBefore: true,
  children: [new TextRun("This starts on a new page")],
});
```

## Critical Rules

- **ALWAYS use ShadingType.CLEAR for table cell shading**
- **NEVER use unicode symbols for bullets** - use proper numbering config
- **NEVER use \n for line breaks** - use separate Paragraph elements
- **ImageRun REQUIRES `type` parameter**
- Measurements in DXA (1440 = 1 inch)
