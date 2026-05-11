import fitz
from PIL import Image
import io, os, time, psutil

def compress_to_target(input_path, supabase, user_id, org_id, target_mb=7):
    start = time.time()

    try:
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

        output_bytes = os.path.getsize(output_path)
        status = "success"

    except Exception as e:
        status = "error"
        output_bytes = None

        supabase.table("error_logs").insert({
            "error_message": str(e),
            "error_type": type(e).__name__
        }).execute()

        return None, None, "LocalError"

    end = time.time()
    duration_ms = (end - start) * 1000

    # Log latency
    supabase.table("latency_stats").insert({
        "engine_type": "local",
        "duration_ms": duration_ms,
        "stage": "compress"
    }).execute()

    # Log engine run
    supabase.table("engine_logs").insert({
        "user_id": user_id,
        "org_id": org_id,
        "engine_type": "local",
        "input_bytes": os.path.getsize(input_path),
        "output_bytes": output_bytes,
        "compression_ratio": (output_bytes / os.path.getsize(input_path)) if output_bytes else None,
        "status": status
    }).execute()

    # Log CPU + RAM
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().used / (1024 * 1024)

    supabase.table("job_metrics").insert({
        "job_type": "pdf_compress",
        "cpu_usage": cpu,
        "memory_usage": mem
    }).execute()

    size_mb = output_bytes / (1024 * 1024)
    return output_path, size_mb, "Bulldozer"
