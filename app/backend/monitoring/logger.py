from backend.supabase_client import get_supabase
from datetime import datetime

def log_usage(user_id, org_id, action, bytes_in, bytes_out):
    """
    Records a usage event in the Supabase 'usage_logs' table.
    """
    supabase = get_supabase()
    data = {
        "user_id": user_id,
        "org_id": org_id,
        "action": action,
        "bytes_in": bytes_in,
        "bytes_out": bytes_out,
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table("usage_logs").insert(data).execute()
