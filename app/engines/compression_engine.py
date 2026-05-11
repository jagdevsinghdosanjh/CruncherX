from backend.monitoring.logger import log_usage

def compress_pdf(file_path, user_id=None, org_id=None):
    # your compression logic here
    original_size = os.path.getsize(file_path)
    compressed_size = run_compression(file_path)
    
    # log usage
    log_usage(user_id, org_id, "compress", original_size, compressed_size)
