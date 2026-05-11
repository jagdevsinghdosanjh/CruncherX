import fitz
from PIL import Image
import io, os

def compress_to_target(input_path, target_mb=7):
    base = os.path.splitext(os.path.basename(input_path))[0]
    output_path = f"{base}_local.pdf"

    doc = fitz.open(input_path)
    new_pdf = fitz.open()

    for page in doc:
        pix = page.get_pixmap(dpi=110)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=40, optimize=True)
        buf.seek(0)

        img_pdf = fitz.open()
        rect = fitz.Rect(0, 0, pix.width, pix.height)
        p = img_pdf.new_page(width=pix.width, height=pix.height)
        p.insert_image(rect, stream=buf.read())
        new_pdf.insert_pdf(img_pdf)

    new_pdf.save(output_path, deflate=True, garbage=4)
    new_pdf.close()

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    return output_path, size_mb, "Bulldozer"
