import fitz
from PIL import Image
import io
import os
import time
from backend.usage_logger import log_engine_run


def compress_to_target(input_path, supabase, user_id, org_id, target_mb=7):
    start = time.time()

    try:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"{base}_cloud.pdf"

        doc = fitz.open(input_path)
        new_pdf = fitz.open()

        for page in doc:
            pix = page.get_pixmap(dpi=72)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=50, optimize=True)
            buf.seek(0)

            img_pdf = fitz.open()
            rect = fitz.Rect(0, 0, pix.width, pix.height)
            p = img_pdf.new_page(width=pix.width, height=pix.height)
            p.insert_image(rect, stream=buf.read())
            new_pdf.insert_pdf(img_pdf)

        new_pdf.save(output_path, deflate=True, garbage=3)
        new_pdf.close()

        output_bytes = os.path.getsize(output_path)
        status = "success"

    except Exception as e:
        status = "error"
        output_bytes = None

        supabase.table("error_logs").insert({
            "error_message": str(e),
            "error_type": type(e).__name__
        }).execute()

        return None, None, "CloudError"

    end = time.time()
    duration_ms = (end - start) * 1000

    # Log latency
    supabase.table("latency_stats").insert({
        "engine_type": "cloud",
        "duration_ms": duration_ms,
        "stage": "compress"
    }).execute()

    # Log engine run
    log_engine_run(
        user_id=user_id,
        org_id= org_id if org_id else None,
        engine_type="cloud",
        input_bytes=os.path.getsize(input_path),
        output_bytes=output_bytes,
        status=status
    )

    size_mb = output_bytes / (1024 * 1024)
    return output_path, size_mb, "CloudSafe"