"""
Campaign History Storage - Lightweight Local JSON Storage
No database required - HuggingFace compatible
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class CampaignStorage:
    """Manages local campaign history in JSON format."""
    
    def __init__(self, storage_file: str = "campaign_history.json"):
        """Initialize storage with file path."""
        self.storage_file = storage_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create storage file if it doesn't exist."""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({"campaigns": []}, f, indent=2)
    
    def save_campaign(
        self,
        product_name: str,
        campaign_goal: str,
        platform: str,
        target_audience: str,
        brand_voice: str,
        generated_text: str,
        image_path: Optional[str],
        original_draft: Optional[str] = None,
        final_text: Optional[str] = None,
        review_score: Optional[float] = None,
        brand_score: Optional[float] = None,
        compliance_status: str = "Approved",
        publishing_package: Optional[Dict] = None,
        token_usage: Optional[Dict] = None
    ) -> str:
        """
        Save campaign to history.
        Returns campaign ID.
        """
        
        # Load existing data
        with open(self.storage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create campaign entry
        campaign_id = f"camp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        campaign = {
            "id": campaign_id,
            "timestamp": datetime.now().isoformat(),
            "product_name": product_name,
            "campaign_goal": campaign_goal,
            "platform": platform,
            "target_audience": target_audience,
            "brand_voice": brand_voice,
            "generated_text": generated_text,
            "image_path": image_path,
            "original_draft": original_draft,
            "final_text": final_text or generated_text,
            "metrics": {
                "review_score": review_score,
                "brand_score": brand_score,
                "compliance_status": compliance_status,
                "character_count": len(generated_text)
            },
            "publishing_package": publishing_package,
            "token_usage": token_usage
        }
        
        # Append to campaigns
        data["campaigns"].append(campaign)
        
        # Save back to file
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return campaign_id
    
    def get_all_campaigns(self) -> List[Dict]:
        """Get all campaigns from history."""
        with open(self.storage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("campaigns", [])
    
    def get_campaign_by_id(self, campaign_id: str) -> Optional[Dict]:
        """Get specific campaign by ID."""
        campaigns = self.get_all_campaigns()
        for campaign in campaigns:
            if campaign.get("id") == campaign_id:
                return campaign
        return None
    
    def get_recent_campaigns(self, limit: int = 10) -> List[Dict]:
        """Get most recent campaigns."""
        campaigns = self.get_all_campaigns()
        return sorted(campaigns, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
    
    def get_stats(self) -> Dict:
        """Get campaign statistics."""
        campaigns = self.get_all_campaigns()
        
        if not campaigns:
            return {
                "total_campaigns": 0,
                "platforms": {},
                "avg_review_score": 0,
                "avg_brand_score": 0
            }
        
        platforms = {}
        review_scores = []
        brand_scores = []
        
        for camp in campaigns:
            # Count platforms
            platform = camp.get("platform", "Unknown")
            platforms[platform] = platforms.get(platform, 0) + 1
            
            # Collect scores
            metrics = camp.get("metrics", {})
            if metrics.get("review_score"):
                review_scores.append(metrics["review_score"])
            if metrics.get("brand_score"):
                brand_scores.append(metrics["brand_score"])
        
        return {
            "total_campaigns": len(campaigns),
            "platforms": platforms,
            "avg_review_score": sum(review_scores) / len(review_scores) if review_scores else 0,
            "avg_brand_score": sum(brand_scores) / len(brand_scores) if brand_scores else 0
        }
    
    def clear_history(self):
        """Clear all campaign history."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump({"campaigns": []}, f, indent=2)
