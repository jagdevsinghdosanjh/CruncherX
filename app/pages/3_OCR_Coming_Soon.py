import streamlit as st
from components.sidebar import render_sidebar
from components.footer import render_footer
from pdf2image import convert_from_path
import pytesseract
import fitz
import os
import tempfile

st.set_page_config(page_title="OCR Engine", layout="wide")

render_sidebar()
st.title("🔍 OCR Engine — Searchable PDF Generator")

st.write("Convert scanned PDFs into **searchable, OCR‑enabled PDFs** using Tesseract OCR.")

uploaded_file = st.file_uploader("Upload scanned PDF", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        input_path = tmp.name

    st.info("Extracting pages…")
    images = convert_from_path(input_path, dpi=300)

    st.info("Running OCR on pages…")
    ocr_pdf = fitz.open()

    for idx, img in enumerate(images):
        st.write(f"OCR processing page {idx+1}/{len(images)}…")

        # Convert PIL image → bytes
        img_bytes = img.tobytes()

        # OCR text
        text = pytesseract.image_to_string(img)

        # Create PDF page
        rect = fitz.Rect(0, 0, img.width, img.height)
        page = ocr_pdf.new_page(width=img.width, height=img.height)

        # Insert original image
        page.insert_image(rect, pixmap=fitz.Pixmap(fitz.csRGB, img.width, img.height, img_bytes))

        # Insert invisible OCR text layer
        page.insert_textbox(rect, text, fontsize=12, overlay=False)

    output_path = "ocr_output.pdf"
    ocr_pdf.save(output_path)
    ocr_pdf.close()

    st.success("OCR complete — your searchable PDF is ready!")

    with open(output_path, "rb") as f:
        st.download_button(
            label="Download Searchable PDF",
            data=f.read(),
            file_name="ocr_output.pdf",
            mime="application/pdf"
        )

render_footer()
