from backend.supabase_client import get_supabase_client

def get_basic_stats():
    supabase = get_supabase_client()

    engine_logs = supabase.table("engine_logs").select("*").execute()
    error_logs = supabase.table("error_logs").select("*").execute()

    total_jobs = len(engine_logs.data) if engine_logs.data else 0
    total_errors = len(error_logs.data) if error_logs.data else 0

    cloud_jobs = len([x for x in engine_logs.data if x.get("engine_type") == "cloud"]) if engine_logs.data else 0
    local_jobs = len([x for x in engine_logs.data if x.get("engine_type") == "local"]) if engine_logs.data else 0

    return {
        "total_jobs": total_jobs,
        "cloud_jobs": cloud_jobs,
        "local_jobs": local_jobs,
        "total_errors": total_errors
    }

# from backend.supabase_client import get_supabase_client

# def get_basic_stats():
#     supabase = get_supabase_client()

#     # Total jobs
#     engine_logs = supabase.table("engine_logs").select("*").execute()
#     total_jobs = len(engine_logs.data) if engine_logs.data else 0

#     # Errors
#     error_logs = supabase.table("error_logs").select("*").execute()
#     total_errors = len(error_logs.data) if error_logs.data else 0

#     # Cloud jobs
#     cloud_jobs = len([x for x in engine_logs.data if x.get("engine_type") == "cloud"]) if engine_logs.data else 0

#     # Local jobs
#     local_jobs = len([x for x in engine_logs.data if x.get("engine_type") == "local"]) if engine_logs.data else 0

#     return {
#         "total_jobs": total_jobs,
#         "cloud_jobs": cloud_jobs,
#         "local_jobs": local_jobs,
#         "total_errors": total_errors
#     }

# from backend.supabase_client import get_supabase

# def get_basic_stats():
#     supabase = get_supabase()

#     users = supabase.table("profiles").select("id", count="exact").execute()
#     orgs = supabase.table("organizations").select("id", count="exact").execute()
#     logs = supabase.table("usage_logs").select("id", count="exact").execute()

#     return {
#         "users": users.count or 0,
#         "orgs": orgs.count or 0,
#         "jobs": logs.count or 0,
#     }
