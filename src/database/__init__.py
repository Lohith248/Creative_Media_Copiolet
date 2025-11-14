"""Database module for campaign storage using Supabase."""

from .supabase_db import (
    SupabaseCampaignDB,
    db,
    save_campaign,
    get_recent_campaigns,
    get_campaign_details,
    search_campaigns,
    get_campaign_stats,
    is_database_available
)

__all__ = [
    'SupabaseCampaignDB',
    'db',
    'save_campaign',
    'get_recent_campaigns',
    'get_campaign_details',
    'search_campaigns',
    'get_campaign_stats',
    'is_database_available'
]
