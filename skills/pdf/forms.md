**CRITICAL: You MUST complete these steps in order. Do not skip ahead to writing code.**

If you need to fill out a PDF form, first check to see if the PDF has fillable form fields. Run this script from this file's directory:
`python scripts/check_fillable_fields <file.pdf>`, and depending on the result go to either the "Fillable fields" or "Non-fillable fields" and follow those instructions.

# Fillable fields

If the PDF has fillable form fields:

- Run this script from this file's directory: `python scripts/extract_form_field_info.py <input.pdf> <field_info.json>`. It will create a JSON file with a list of fields.
- Convert the PDF to PNGs: `python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
- Create a `field_values.json` file with the values to be entered for each field
- Run the `fill_fillable_fields.py` script: `python scripts/fill_fillable_fields.py <input pdf> <field_values.json> <output pdf>`

# Non-fillable fields

If the PDF doesn't have fillable form fields, you'll need to visually determine where the data should be added and create text annotations.

## Step 1: Visual Analysis (REQUIRED)

- Convert the PDF to PNG images: `python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
- Examine each PNG image and identify all form fields

## Step 2: Create fields.json and validation images (REQUIRED)

- Create a file named `fields.json` with information for the form fields and bounding boxes
- Create validation images: `python scripts/create_validation_image.py <page_number> <path_to_fields.json> <input_image_path> <output_image_path>`

## Step 3: Validate Bounding Boxes (REQUIRED)

- Check the fields.json file: `python scripts/check_bounding_boxes.py <JSON file>`
- Visually inspect validation images
- Red rectangles must ONLY cover input areas
- Blue rectangles should contain label text

## Step 4: Add annotations to the PDF

Run this script to create a filled-out PDF:
`python scripts/fill_pdf_form_with_annotations.py <input_pdf_path> <path_to_fields.json> <output_pdf_path>`
