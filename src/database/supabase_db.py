"""
Campaign Database - Supabase cloud storage for campaign history
Stores generated campaigns, images, and metadata with real-time sync
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ Supabase not installed. Run: pip install supabase")


class SupabaseCampaignDB:
    """Cloud database for storing campaign history using Supabase."""
    
    def __init__(self):
        """Initialize Supabase connection."""
        self.client: Optional[Client] = None
        self.connected = False
        
        if not SUPABASE_AVAILABLE:
            print("❌ Supabase library not available")
            return
        
        # Get credentials from environment
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("⚠️ Supabase credentials not found in .env")
            print("   Add SUPABASE_URL and SUPABASE_KEY to your .env file")
            return
        
        try:
            self.client = create_client(supabase_url, supabase_key)
            self.connected = True
            print("✅ Connected to Supabase!")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            self.connected = False
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.connected and self.client is not None
    
    def save_campaign(self, campaign_data: Dict) -> Optional[int]:
        """
        Save a new campaign to Supabase.
        
        Args:
            campaign_data: Dictionary with campaign details
            
        Returns:
            campaign_id: ID of newly created campaign, or None if failed
        """
        if not self.is_connected():
            print("⚠️ Database not connected - campaign not saved")
            return None
        
        try:
            # Prepare data for insertion
            data = {
                'product_name': campaign_data.get('product_name'),
                'platform': campaign_data.get('platform'),
                'brand_preset': campaign_data.get('brand_preset'),
                'objective': campaign_data.get('objective'),
                'target_audience': campaign_data.get('target_audience'),
                'final_copy': campaign_data.get('final_copy'),
                'hashtags': campaign_data.get('hashtags'),
                'image_path': campaign_data.get('image_path'),
                'quality_score': campaign_data.get('quality_score'),
                'brand_score': campaign_data.get('brand_score'),
                'compliance_score': campaign_data.get('compliance_score'),
                'readability_score': campaign_data.get('readability_score'),
                'engagement_score': campaign_data.get('engagement_score'),
                'iteration_count': campaign_data.get('iteration_count'),
                'status': campaign_data.get('status', 'Generated'),
                'research_included': campaign_data.get('research_included', False),
                'research_data': campaign_data.get('research_data', {})
            }
            
            # Insert into Supabase
            response = self.client.table('campaigns').insert(data).execute()
            
            if response.data and len(response.data) > 0:
                campaign_id = response.data[0]['id']
                print(f"✅ Campaign saved to Supabase with ID: {campaign_id}")
                return campaign_id
            else:
                print("⚠️ Campaign saved but no ID returned")
                return None
                
        except Exception as e:
            print(f"❌ Failed to save campaign to Supabase: {e}")
            return None
    
    def get_recent_campaigns(self, limit: int = 20) -> List[Dict]:
        """Get recent campaigns sorted by date."""
        if not self.is_connected():
            return []
        
        try:
            response = self.client.table('campaigns')\
                .select('id, product_name, platform, objective, quality_score, brand_score, compliance_score, created_at, image_path, status')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Failed to fetch campaigns: {e}")
            return []
    
    def get_campaign_by_id(self, campaign_id: int) -> Optional[Dict]:
        """Get full campaign details by ID."""
        if not self.is_connected():
            return None
        
        try:
            response = self.client.table('campaigns')\
                .select('*')\
                .eq('id', campaign_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Failed to fetch campaign: {e}")
            return None
    
    def search_campaigns(self, query: str) -> List[Dict]:
        """Search campaigns by product name or objective."""
        if not self.is_connected():
            return []
        
        try:
            # Supabase uses ilike for case-insensitive search
            response = self.client.table('campaigns')\
                .select('id, product_name, platform, objective, quality_score, created_at, image_path')\
                .or_(f'product_name.ilike.%{query}%,objective.ilike.%{query}%')\
                .order('created_at', desc=True)\
                .limit(50)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get overall statistics."""
        if not self.is_connected():
            return {
                'total_campaigns': 0,
                'avg_quality': 0,
                'avg_brand': 0,
                'avg_compliance': 0,
                'approved_count': 0
            }
        
        try:
            # Get all campaigns for stats calculation
            response = self.client.table('campaigns')\
                .select('quality_score, brand_score, compliance_score, status')\
                .execute()
            
            if not response.data:
                return {
                    'total_campaigns': 0,
                    'avg_quality': 0,
                    'avg_brand': 0,
                    'avg_compliance': 0,
                    'approved_count': 0
                }
            
            campaigns = response.data
            total = len(campaigns)
            
            # Calculate averages
            avg_quality = sum(c.get('quality_score', 0) or 0 for c in campaigns) / total if total > 0 else 0
            avg_brand = sum(c.get('brand_score', 0) or 0 for c in campaigns) / total if total > 0 else 0
            avg_compliance = sum(c.get('compliance_score', 0) or 0 for c in campaigns) / total if total > 0 else 0
            approved = sum(1 for c in campaigns if c.get('status') == 'Approved')
            
            return {
                'total_campaigns': total,
                'avg_quality': avg_quality,
                'avg_brand': avg_brand,
                'avg_compliance': avg_compliance,
                'approved_count': approved
            }
            
        except Exception as e:
            print(f"❌ Failed to get stats: {e}")
            return {
                'total_campaigns': 0,
                'avg_quality': 0,
                'avg_brand': 0,
                'avg_compliance': 0,
                'approved_count': 0
            }
    
    def delete_campaign(self, campaign_id: int) -> bool:
        """Delete a campaign."""
        if not self.is_connected():
            return False
        
        try:
            response = self.client.table('campaigns')\
                .delete()\
                .eq('id', campaign_id)\
                .execute()
            
            print(f"✅ Campaign {campaign_id} deleted")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete campaign: {e}")
            return False


# Global database instance
db = SupabaseCampaignDB()


# Helper functions for easy integration
def save_campaign(campaign_data: Dict) -> Optional[int]:
    """Save campaign to database."""
    return db.save_campaign(campaign_data)


def get_recent_campaigns(limit: int = 20) -> List[Dict]:
    """Get recent campaigns."""
    return db.get_recent_campaigns(limit)


def get_campaign_details(campaign_id: int) -> Optional[Dict]:
    """Get full campaign details."""
    return db.get_campaign_by_id(campaign_id)


def search_campaigns(query: str) -> List[Dict]:
    """Search campaigns."""
    return db.search_campaigns(query)


def get_campaign_stats() -> Dict:
    """Get statistics."""
    return db.get_stats()


def is_database_available() -> bool:
    """Check if database is available."""
    return db.is_connected()


if __name__ == "__main__":
    print("🧪 Testing Supabase Campaign Database...\n")
    
    if not db.is_connected():
        print("❌ Not connected to Supabase")
        print("\n📝 Setup Instructions:")
        print("1. Create account at https://supabase.com")
        print("2. Create a new project")
        print("3. Add to .env file:")
        print("   SUPABASE_URL=your_project_url")
        print("   SUPABASE_KEY=your_anon_key")
        print("4. Run SQL to create table (see SUPABASE_SETUP.md)")
        exit(1)
    
    print("✅ Connected to Supabase!")
    
    # Test saving a campaign
    test_campaign = {
        'product_name': 'Eco-Friendly Water Bottle',
        'platform': 'Instagram',
        'brand_preset': 'eco_brand',
        'objective': 'Increase brand awareness',
        'target_audience': 'Young professionals',
        'final_copy': '🌿 Stay hydrated, save the planet! Our reusable water bottle...',
        'hashtags': '#ecofriendly #sustainability #zerowaste',
        'image_path': 'generated_images/test.png',
        'quality_score': 8.5,
        'brand_score': 85,
        'compliance_score': 95,
        'readability_score': 9.0,
        'engagement_score': 8.3,
        'iteration_count': 2,
        'status': 'Approved',
        'research_included': True
    }
    
    print("\n📝 Testing save campaign...")
    campaign_id = save_campaign(test_campaign)
    
    if campaign_id:
        print(f"✅ Saved with ID: {campaign_id}")
        
        # Test getting recent campaigns
        print("\n📊 Testing get recent campaigns...")
        recent = get_recent_campaigns(5)
        print(f"✅ Found {len(recent)} campaigns")
        for c in recent[:3]:
            print(f"  - {c['product_name']} ({c['platform']}) - Score: {c.get('quality_score', 0)}/10")
        
        # Test stats
        print("\n📈 Testing statistics...")
        stats = get_campaign_stats()
        print(f"✅ Statistics:")
        print(f"  Total campaigns: {stats.get('total_campaigns', 0)}")
        print(f"  Avg quality: {stats.get('avg_quality', 0):.1f}/10")
        print(f"  Approved: {stats.get('approved_count', 0)}")
        
        print("\n✅ All tests passed!")
    else:
        print("❌ Failed to save campaign")
