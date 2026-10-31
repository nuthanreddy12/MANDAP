from typing import Optional
import logging
from backend.core.config import settings

logger = logging.getLogger(__name__)

supabase_client = None

def get_supabase_client():
    global supabase_client
    if supabase_client is not None:
        return supabase_client
    
    if settings.SUPABASE_URL and (settings.SUPABASE_ANON_KEY or settings.SUPABASE_SERVICE_ROLE_KEY):
        try:
            from supabase import create_client, Client
            key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
            supabase_client = create_client(settings.SUPABASE_URL, key)
            logger.info("Connected to Supabase client.")
            return supabase_client
        except Exception as e:
            logger.warning(f"Could not initialize Supabase client: {e}. Fallback to direct DB mode.")
            return None
    else:
        logger.info("Supabase credentials not configured in environment. Using direct SQLAlchemy database connection.")
        return None
