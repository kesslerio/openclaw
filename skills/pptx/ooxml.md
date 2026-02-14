# Office Open XML Technical Reference for PowerPoint

**Important: Read this entire document before starting.**

## Technical Guidelines

### Schema Compliance

- **Element ordering in `<p:txBody>`**: `<a:bodyPr>`, `<a:lstStyle>`, `<a:p>`
- **Whitespace**: Add `xml:space='preserve'` to `<a:t>` elements with leading/trailing spaces
- **Unicode**: Escape characters in ASCII content: `"` becomes `&#8220;`
- **Images**: Add to `ppt/media/`, reference in slide XML, set dimensions to fit slide bounds
- **Relationships**: Update `ppt/slides/_rels/slideN.xml.rels` for each slide's resources
- **Dirty attribute**: Add `dirty="0"` to `<a:rPr>` and `<a:endParaRPr>` elements

## Presentation Structure

### Basic Slide Structure

```xml
<p:sld>
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>...</p:nvGrpSpPr>
      <p:grpSpPr>...</p:grpSpPr>
      <!-- Shapes go here -->
    </p:spTree>
  </p:cSld>
</p:sld>
```

### Text Box / Shape with Text

```xml
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="2" name="Title"/>
    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
    <p:nvPr><p:ph type="ctrTitle"/></p:nvPr>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="838200" y="365125"/>
      <a:ext cx="7772400" cy="1470025"/>
    </a:xfrm>
  </p:spPr>
  <p:txBody>
    <a:bodyPr/>
    <a:lstStyle/>
    <a:p>
      <a:r><a:t>Slide Title</a:t></a:r>
    </a:p>
  </p:txBody>
</p:sp>
```

### Text Formatting

```xml
<!-- Bold -->
<a:r><a:rPr b="1"/><a:t>Bold Text</a:t></a:r>
<!-- Italic -->
<a:r><a:rPr i="1"/><a:t>Italic Text</a:t></a:r>
<!-- Font and Size -->
<a:r>
  <a:rPr sz="2400" typeface="Arial">
    <a:solidFill><a:srgbClr val="FF0000"/></a:solidFill>
  </a:rPr>
  <a:t>Colored Arial 24pt</a:t>
</a:r>
```

### Lists

```xml
<!-- Bullet list -->
<a:p>
  <a:pPr lvl="0"><a:buChar char="•"/></a:pPr>
  <a:r><a:t>First bullet point</a:t></a:r>
</a:p>

<!-- Numbered list -->
<a:p>
  <a:pPr lvl="0"><a:buAutoNum type="arabicPeriod"/></a:pPr>
  <a:r><a:t>First numbered item</a:t></a:r>
</a:p>
```

## File Updates

When adding content, update these files:

**`ppt/_rels/presentation.xml.rels`:**

```xml
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
```

**`[Content_Types].xml`:**

```xml
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
```

## Slide Operations

### Adding a New Slide

1. Create the slide file (`ppt/slides/slideN.xml`)
2. Update `[Content_Types].xml`
3. Update `ppt/_rels/presentation.xml.rels`
4. Update `ppt/presentation.xml`: Add slide ID to `<p:sldIdLst>`

### Reordering Slides

Update `ppt/presentation.xml`: Reorder `<p:sldId>` elements in `<p:sldIdLst>`

### Deleting a Slide

1. Remove from `ppt/presentation.xml`
2. Remove from `ppt/_rels/presentation.xml.rels`
3. Remove from `[Content_Types].xml`
4. Delete slide files
