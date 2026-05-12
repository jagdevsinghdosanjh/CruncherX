import fitz
from PIL import Image
import io, os, time
from backend.subscriptions import (
    get_user_plan,
    enforce_plan_rules,
    log_usage
)


def compress_to_target(input_path, user_id, org_id, supabase, is_bulk=False):
    """
    Local Bulldozer Engine with Subscription Enforcement
    """

    # -----------------------------
    # 1. Load user + plan
    # -----------------------------
    user = get_user_plan(user_id)
    rules = enforce_plan_rules(user)

    if not rules["allowed"]:
        return None, None, rules["reason"]  # return error message

    # -----------------------------
    # 2. Bulk restriction
    # -----------------------------
    if is_bulk and not rules.get("bulk"):
        return None, None, "Bulk compression is only available on Basic, Pro, and Business plans."

    # -----------------------------
    # 3. Start compression
    # -----------------------------
    start = time.time()

    base = os.path.splitext(os.path.basename(input_path))[0]
    output_path = f"{base}_local.pdf"

    doc = fitz.open(input_path)
    new_pdf = fitz.open()

    # Priority mode = higher DPI, better quality
    dpi = 130 if rules.get("priority") else 110
    jpeg_quality = 50 if rules.get("priority") else 40

    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
        buf.seek(0)

        img_pdf = fitz.open()
        rect = fitz.Rect(0, 0, pix.width, pix.height)
        p = img_pdf.new_page(width=pix.width, height=pix.height)
        p.insert_image(rect, stream=buf.read())
        new_pdf.insert_pdf(img_pdf)

    # -----------------------------
    # 4. Apply watermark (Free plan)
    # -----------------------------
    if rules.get("watermark"):
        for page in new_pdf:
            page.insert_text(
                (50, 50),
                "Compressed with CruncherX Free Plan",
                fontsize=18,
                color=(0.6, 0.6, 0.6),
                rotate=30,
                overlay=True,
            )

    # -----------------------------
    # 5. Save output
    # -----------------------------
    new_pdf.save(output_path, deflate=True, garbage=4)
    new_pdf.close()

    output_bytes = os.path.getsize(output_path)
    input_bytes = os.path.getsize(input_path)
    size_mb = output_bytes / (1024 * 1024)

    # -----------------------------
    # 6. Log usage
    # -----------------------------
    log_usage(
        user_id=user_id,
        org_id=org_id,
        action="compress",
        bytes_in=input_bytes,
        bytes_out=output_bytes
    )

    end = time.time()
    duration_ms = (end - start) * 1000

    return output_path, size_mb, "Bulldozer"


# import fitz
# from PIL import Image
# import io, os

# def compress_to_target(input_path, target_mb=7):
#     base = os.path.splitext(os.path.basename(input_path))[0]
#     output_path = f"{base}_local.pdf"

#     doc = fitz.open(input_path)
#     new_pdf = fitz.open()

#     for page in doc:
#         pix = page.get_pixmap(dpi=110)
#         img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

#         buf = io.BytesIO()
#         img.save(buf, format="JPEG", quality=40, optimize=True)
#         buf.seek(0)

#         img_pdf = fitz.open()
#         rect = fitz.Rect(0, 0, pix.width, pix.height)
#         p = img_pdf.new_page(width=pix.width, height=pix.height)
#         p.insert_image(rect, stream=buf.read())
#         new_pdf.insert_pdf(img_pdf)

#     new_pdf.save(output_path, deflate=True, garbage=4)
#     new_pdf.close()

#     size_mb = os.path.getsize(output_path) / (1024 * 1024)
#     return output_path, size_mb, "Bulldozer"
