from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    """
    Returns an instance of the Supabase Client.
    In a real-world scenario, you might want to initialize this once
    or attach it to app state.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
