from backend.supabase_client import get_supabase

def get_basic_stats():
    supabase = get_supabase()

    users = supabase.table("profiles").select("id", count="exact").execute()
    orgs = supabase.table("organizations").select("id", count="exact").execute()
    logs = supabase.table("usage_logs").select("id", count="exact").execute()

    return {
        "users": users.count or 0,
        "orgs": orgs.count or 0,
        "jobs": logs.count or 0,
    }
