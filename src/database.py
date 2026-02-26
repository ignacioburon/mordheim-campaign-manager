import os
import logging
from supabase import create_client, Client

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() # This will show logs in your Hugging Face "Logs" tab
    ]
)
logger = logging.getLogger("mordheim_app")

def init_supabase() -> Client:
    """Initialize Supabase client with internal error logging."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        logger.error("SUPABASE_URL or SUPABASE_KEY missing from environment variables.")
        return None
    return create_client(url, key)

db = init_supabase()
