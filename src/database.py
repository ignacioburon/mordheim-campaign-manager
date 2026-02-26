import os
from supabase import create_client, Client

def init_supabase() -> Client:
    """Initialize Supabase client using environment variables."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

db = init_supabase()
