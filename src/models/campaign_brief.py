# src/models/campaign_brief.py
"""
Campaign Brief - Unified data structure for campaign context
All agents reference this for consistency
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BrandProfile:
    """Brand identity and voice attributes"""
    name: str
    voice_attributes: list[str]  # e.g., ["professional", "friendly", "innovative"]
    industry: str  # e.g., "technology", "fashion", "food"
    values: list[str]  # e.g., ["sustainability", "innovation", "quality"]
    tone: str  # e.g., "casual", "formal", "enthusiastic"
    
    # Visual identity
    color_palette: Optional[list[str]] = None  # e.g., ["#FF5733", "#3498DB"]
    visual_style: Optional[str] = None  # e.g., "minimalist", "bold", "organic"


@dataclass
class PlatformConstraints:
    """Platform-specific requirements and best practices"""
    name: str  # "instagram", "twitter", "linkedin", "facebook"
    max_chars: int
    optimal_chars: int
    hashtag_limit: int
    image_ratio: str  # e.g., "1:1", "16:9", "9:16"
    best_practices: list[str]


# Platform presets
PLATFORM_PRESETS = {
    "instagram": PlatformConstraints(
        name="instagram",
        max_chars=2200,
        optimal_chars=150,
        hashtag_limit=30,
        image_ratio="1:1",
        best_practices=[
            "Use emojis to break up text",
            "Front-load key message in first 125 chars (before 'more' cutoff)",
            "Include strong call-to-action",
            "Use 3-5 relevant hashtags for reach",
            "Mobile-first visual design"
        ]
    ),
    "twitter": PlatformConstraints(
        name="twitter",
        max_chars=280,
        optimal_chars=240,
        hashtag_limit=2,
        image_ratio="16:9",
        best_practices=[
            "Be concise and punchy",
            "Use 1-2 hashtags maximum",
            "Include media for 2x engagement",
            "Ask questions to drive replies",
            "Use line breaks for readability"
        ]
    ),
    "linkedin": PlatformConstraints(
        name="linkedin",
        max_chars=3000,
        optimal_chars=150,
        hashtag_limit=5,
        image_ratio="1.91:1",
        best_practices=[
            "Professional yet conversational tone",
            "Open with hook question or bold statement",
            "Use bullet points or numbered lists",
            "Include industry insights or data",
            "End with clear CTA"
        ]
    ),
    "facebook": PlatformConstraints(
        name="facebook",
        max_chars=63206,
        optimal_chars=250,
        hashtag_limit=3,
        image_ratio="1.91:1",
        best_practices=[
            "Storytelling approach works best",
            "Use conversational tone",
            "Include emotional hooks",
            "Ask questions to drive comments",
            "Visual content is crucial"
        ]
    )
}


@dataclass
class CampaignBrief:
    """Complete campaign context shared across all agents"""
    brand: BrandProfile
    platform: PlatformConstraints
    objective: str  # e.g., "product launch", "brand awareness", "engagement"
    target_audience: str
    key_message: str
    call_to_action: str
    content_type: str  # e.g., "promotional", "educational", "entertainment"
    
    # Optional context
    product_name: Optional[str] = None
    special_requirements: Optional[str] = None
    avoid_topics: Optional[list[str]] = None
    
    def to_context_string(self) -> str:
        """Generate formatted context string for agent prompts"""
        context = f"""
CAMPAIGN CONTEXT:
================
Brand: {self.brand.name}
Industry: {self.brand.industry}
Brand Voice: {', '.join(self.brand.voice_attributes)}
Brand Values: {', '.join(self.brand.values)}
Tone: {self.brand.tone}

Platform: {self.platform.name.upper()}
Max Characters: {self.platform.max_chars}
Optimal Length: {self.platform.optimal_chars} chars
Hashtag Limit: {self.platform.hashtag_limit}
Image Ratio: {self.platform.image_ratio}

Objective: {self.objective}
Target Audience: {self.target_audience}
Key Message: {self.key_message}
Call-to-Action: {self.call_to_action}
Content Type: {self.content_type}
"""
        if self.product_name:
            context += f"Product: {self.product_name}\n"
        if self.special_requirements:
            context += f"Special Requirements: {self.special_requirements}\n"
        if self.avoid_topics:
            context += f"Avoid: {', '.join(self.avoid_topics)}\n"
            
        return context


# Brand presets for quick testing
BRAND_PRESETS = {
    "tech_startup": BrandProfile(
        name="TechStartup",
        voice_attributes=["innovative", "bold", "cutting-edge", "transparent"],
        industry="technology",
        values=["innovation", "transparency", "user-first"],
        tone="enthusiastic",
        color_palette=["#6C5CE7", "#00D2D3", "#FD79A8"],
        visual_style="modern minimalist"
    ),
    "tech_wellness": BrandProfile(
        name="NeuroPulse",
        voice_attributes=["innovative", "empowering", "supportive", "scientific"],
        industry="health tech",
        values=["mental wellness", "AI innovation", "stress reduction"],
        tone="inspiring and professional",
        color_palette=["#6C5CE7", "#00D2D3", "#FD79A8"],
        visual_style="modern tech minimalist"
    ),
    "eco_brand": BrandProfile(
        name="EcoLife",
        voice_attributes=["authentic", "sustainable", "caring", "educational"],
        industry="sustainability",
        values=["environmental care", "authenticity", "community"],
        tone="warm and inspiring",
        color_palette=["#27AE60", "#F39C12", "#ECF0F1"],
        visual_style="organic natural"
    ),
    "luxury_fashion": BrandProfile(
        name="Lumière",
        voice_attributes=["elegant", "sophisticated", "exclusive", "timeless"],
        industry="fashion",
        values=["craftsmanship", "elegance", "heritage"],
        tone="refined",
        color_palette=["#000000", "#D4AF37", "#FFFFFF"],
        visual_style="high-end editorial"
    ),
    "food_brand": BrandProfile(
        name="TasteHub",
        voice_attributes=["fun", "energetic", "appetizing", "friendly"],
        industry="food & beverage",
        values=["quality", "community", "joy"],
        tone="casual enthusiastic",
        color_palette=["#E74C3C", "#F39C12", "#2ECC71"],
        visual_style="vibrant appetizing"
    )
}
