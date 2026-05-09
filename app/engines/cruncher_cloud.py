import fitz
from PIL import Image
import io, os

def compress_to_target(input_path, target_mb=7):
    base = os.path.splitext(input_path)[0]
    output = f"{base}_cloud.pdf"

    doc = fitz.open(input_path)
    new = fitz.open()

    for page in doc:
        pix = page.get_pixmap(dpi=72)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=50)
        buf.seek(0)

        img_pdf = fitz.open()
        rect = fitz.Rect(0, 0, pix.width, pix.height)
        p = img_pdf.new_page(width=pix.width, height=pix.height)
        p.insert_image(rect, stream=buf.read())
        new.insert_pdf(img_pdf)

    new.save(output)
    new.close()

    size = os.path.getsize(output) / (1024*1024)
    return output, size, "CloudSafe"
