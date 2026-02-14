# HTML to PowerPoint Guide

Convert HTML slides to PowerPoint presentations with accurate positioning using the `html2pptx.js` library.

## Creating HTML Slides

Every HTML slide must include proper body dimensions:

### Layout Dimensions

- **16:9** (default): `width: 720pt; height: 405pt`
- **4:3**: `width: 720pt; height: 540pt`
- **16:10**: `width: 720pt; height: 450pt`

### Supported Elements

- `<p>`, `<h1>`-`<h6>` - Text with styling
- `<ul>`, `<ol>` - Lists (never use manual bullets •, -, \*)
- `<b>`, `<strong>` - Bold text
- `<i>`, `<em>` - Italic text
- `<u>` - Underlined text
- `<span>` - Inline formatting with CSS styles
- `<br>` - Line breaks
- `<div>` with bg/border - Becomes shape
- `<img>` - Images
- `class="placeholder"` - Reserved space for charts

### Critical Text Rules

**ALL text MUST be inside `<p>`, `<h1>`-`<h6>`, `<ul>`, or `<ol>` tags:**

- ✅ Correct: `<div><p>Text here</p></div>`
- ❌ Wrong: `<div>Text here</div>` - **Text will NOT appear**

**ONLY use web-safe fonts:**

- ✅ Web-safe fonts: `Arial`, `Helvetica`, `Times New Roman`, `Georgia`, `Courier New`, `Verdana`, `Tahoma`

### Shape Styling (DIV elements only)

- **Backgrounds**: CSS `background` on `<div>` elements only
- **Borders**: CSS `border` on `<div>` elements
- **Border radius**: CSS `border-radius` for rounded corners
- **Box shadows**: CSS `box-shadow` for shadows

### Icons & Gradients

**CRITICAL: Never use CSS gradients** - They don't convert to PowerPoint. Always rasterize to PNG first using Sharp.

### Example

```html
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        width: 720pt;
        height: 405pt;
        margin: 0;
        padding: 0;
        background: #f5f5f5;
        font-family: Arial, sans-serif;
        display: flex;
      }
      .content {
        margin: 30pt;
        padding: 40pt;
        background: #ffffff;
        border-radius: 8pt;
      }
      h1 {
        color: #2d3748;
        font-size: 32pt;
      }
    </style>
  </head>
  <body>
    <div class="content">
      <h1>Recipe Title</h1>
      <ul>
        <li><b>Item:</b> Description</li>
      </ul>
      <div id="chart" class="placeholder" style="width: 350pt; height: 200pt;"></div>
    </div>
  </body>
</html>
```

## Using html2pptx Library

```javascript
const pptxgen = require("pptxgenjs");
const html2pptx = require("./html2pptx");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_16x9";

const { slide, placeholders } = await html2pptx("slide1.html", pptx);

// Add chart to placeholder area
if (placeholders.length > 0) {
  slide.addChart(pptx.charts.LINE, chartData, placeholders[0]);
}

await pptx.writeFile("output.pptx");
```

## Using PptxGenJS

### Critical Rules

**NEVER use `#` prefix** with hex colors in PptxGenJS - causes file corruption

- ✅ Correct: `color: "FF0000"`, `fill: { color: "0066CC" }`
- ❌ Wrong: `color: "#FF0000"`

### Adding Charts

```javascript
slide.addChart(
  pptx.charts.BAR,
  [
    {
      name: "Sales 2024",
      labels: ["Q1", "Q2", "Q3", "Q4"],
      values: [4500, 5500, 6200, 7100],
    },
  ],
  {
    ...placeholders[0],
    showTitle: true,
    title: "Quarterly Sales",
    showCatAxisTitle: true,
    catAxisTitle: "Quarter",
    showValAxisTitle: true,
    valAxisTitle: "Sales ($000s)",
    chartColors: ["4472C4"],
  },
);
```

### Adding Tables

```javascript
slide.addTable(
  [
    ["Header 1", "Header 2", "Header 3"],
    ["Row 1, Col 1", "Row 1, Col 2", "Row 1, Col 3"],
  ],
  {
    x: 0.5,
    y: 1,
    w: 9,
    h: 3,
    border: { pt: 1, color: "999999" },
    fill: { color: "F1F1F1" },
  },
);
```
