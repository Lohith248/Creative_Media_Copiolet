"""
Publishing Agent - Platform-Specific Content Formatter
Formats approved content for Instagram, Twitter, LinkedIn, Facebook
NO LLM calls - pure formatting and rule enforcement
"""

import re
from typing import Dict, Optional


class PublishingAgent:
    """Formats content for platform-specific publishing requirements."""
    
    # Platform constraints
    PLATFORM_LIMITS = {
        "instagram": {
            "max_caption": 2200,
            "max_hashtags": 30,
            "recommended_hashtags": "5-10",
            "image_ratio": "1:1 or 4:5",
            "line_breaks": True
        },
        "twitter": {
            "max_chars": 280,
            "max_hashtags": 3,
            "recommended_hashtags": "1-2",
            "image_ratio": "16:9 or 2:1",
            "line_breaks": False
        },
        "linkedin": {
            "max_chars": 3000,
            "max_hashtags": 5,
            "recommended_hashtags": "3-5",
            "image_ratio": "1.91:1",
            "line_breaks": True
        },
        "facebook": {
            "max_chars": 63206,
            "max_hashtags": 10,
            "recommended_hashtags": "2-5",
            "image_ratio": "1.91:1 or 1:1",
            "line_breaks": True
        }
    }
    
    def __init__(self):
        """Initialize publishing agent."""
        pass
    
    def create_publishing_package(
        self,
        content: str,
        platform: str,
        call_to_action: str = "Learn more",
        product_url: Optional[str] = None,
        brand_hashtags: Optional[list] = None
    ) -> Dict[str, str]:
        """
        Create platform-specific versions of approved content.
        Returns dict with formatted posts for each platform.
        """
        
        platform_lower = platform.lower()
        
        # Extract components from content
        components = self._parse_content(content)
        
        # Generate for each platform
        package = {
            "primary_platform": platform_lower,
            "instagram_post": self._format_instagram(components, call_to_action, brand_hashtags),
            "twitter_post": self._format_twitter(components, call_to_action, brand_hashtags),
            "linkedin_post": self._format_linkedin(components, call_to_action, product_url, brand_hashtags),
            "facebook_post": self._format_facebook(components, call_to_action, product_url, brand_hashtags),
            "character_counts": {
                "instagram": len(self._format_instagram(components, call_to_action, brand_hashtags)),
                "twitter": len(self._format_twitter(components, call_to_action, brand_hashtags)),
                "linkedin": len(self._format_linkedin(components, call_to_action, product_url, brand_hashtags)),
                "facebook": len(self._format_facebook(components, call_to_action, product_url, brand_hashtags))
            }
        }
        
        return package
    
    def _parse_content(self, content: str) -> Dict:
        """Parse content into components (hook, body, CTA, hashtags)."""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Extract hashtags
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, content)
        
        # Remove hashtags from main text
        text_without_hashtags = re.sub(hashtag_pattern, '', content).strip()
        lines_clean = [line.strip() for line in text_without_hashtags.split('\n') if line.strip()]
        
        # First line = hook
        hook = lines_clean[0] if lines_clean else ""
        
        # Body = middle lines
        body_lines = lines_clean[1:-1] if len(lines_clean) > 2 else lines_clean[1:] if len(lines_clean) > 1 else []
        body = "\n".join(body_lines)
        
        # Last line might be CTA
        cta = lines_clean[-1] if lines_clean and any(word in lines_clean[-1].lower() for word in ['learn', 'visit', 'shop', 'discover', 'click', 'join', 'get', 'try']) else ""
        
        return {
            "hook": hook,
            "body": body,
            "cta": cta,
            "hashtags": hashtags,
            "full_text": text_without_hashtags
        }
    
    def _format_instagram(self, components: Dict, cta: str, brand_hashtags: Optional[list]) -> str:
        """Format for Instagram (max 2200 chars, line breaks, hashtags)."""
        post = f"{components['hook']}\n\n"
        
        if components['body']:
            post += f"{components['body']}\n\n"
        
        # Add CTA
        if components['cta']:
            post += f"{components['cta']}\n"
        elif cta:
            post += f"{cta}\n"
        
        # Add hashtags
        all_hashtags = components['hashtags'][:20]  # Limit to 20
        if brand_hashtags:
            all_hashtags.extend([f"#{tag}" if not tag.startswith('#') else tag for tag in brand_hashtags[:5]])
        
        if all_hashtags:
            post += f"\n{' '.join(all_hashtags)}"
        
        # Enforce limit
        if len(post) > 2200:
            post = post[:2197] + "..."
        
        return post
    
    def _format_twitter(self, components: Dict, cta: str, brand_hashtags: Optional[list]) -> str:
        """Format for Twitter/X (max 280 chars, concise, 1-2 hashtags)."""
        # Twitter needs to be VERY concise
        hook = components['hook'][:150]  # Shorten hook if needed
        
        # Select top 2 hashtags
        hashtags = components['hashtags'][:2]
        if brand_hashtags and len(hashtags) < 2:
            hashtags.append(f"#{brand_hashtags[0]}" if not brand_hashtags[0].startswith('#') else brand_hashtags[0])
        
        # Build tweet
        post = f"{hook}"
        
        # Add hashtags
        if hashtags:
            post += f" {' '.join(hashtags)}"
        
        # Enforce 280 limit
        if len(post) > 280:
            # Trim and add ellipsis
            available = 280 - len(' '.join(hashtags)) - 5
            post = f"{hook[:available]}... {' '.join(hashtags)}"
        
        return post
    
    def _format_linkedin(self, components: Dict, cta: str, url: Optional[str], brand_hashtags: Optional[list]) -> str:
        """Format for LinkedIn (professional, 3-5 hashtags, optional link)."""
        post = f"{components['hook']}\n\n"
        
        if components['body']:
            post += f"{components['body']}\n\n"
        
        # Professional CTA
        if components['cta']:
            post += f"{components['cta']}\n"
        elif cta:
            post += f"{cta}\n"
        
        # Add link if provided
        if url:
            post += f"\n🔗 {url}\n"
        
        # LinkedIn hashtags (3-5, professional)
        hashtags = components['hashtags'][:3]
        if brand_hashtags:
            for tag in brand_hashtags[:2]:
                hashtag = f"#{tag}" if not tag.startswith('#') else tag
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        if hashtags:
            post += f"\n{' '.join(hashtags[:5])}"
        
        # Enforce limit
        if len(post) > 3000:
            post = post[:2997] + "..."
        
        return post
    
    def _format_facebook(self, components: Dict, cta: str, url: Optional[str], brand_hashtags: Optional[list]) -> str:
        """Format for Facebook (longer text allowed, link preview)."""
        post = f"{components['hook']}\n\n"
        
        if components['body']:
            post += f"{components['body']}\n\n"
        
        # CTA
        if components['cta']:
            post += f"{components['cta']}\n"
        elif cta:
            post += f"{cta}\n"
        
        # Link
        if url:
            post += f"\n👉 {url}\n"
        
        # Hashtags (2-5)
        hashtags = components['hashtags'][:3]
        if brand_hashtags:
            for tag in brand_hashtags[:2]:
                hashtag = f"#{tag}" if not tag.startswith('#') else tag
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        if hashtags:
            post += f"\n{' '.join(hashtags[:5])}"
        
        return post
    
    def get_character_count(self, text: str) -> int:
        """Get character count."""
        return len(text)
    
    def enforce_platform_rules(self, text: str, platform: str) -> Dict:
        """Check if text meets platform requirements."""
        platform_lower = platform.lower()
        limits = self.PLATFORM_LIMITS.get(platform_lower, {})
        
        char_count = len(text)
        max_chars = limits.get("max_chars", limits.get("max_caption", 10000))
        
        # Count hashtags
        hashtags = re.findall(r'#\w+', text)
        hashtag_count = len(hashtags)
        max_hashtags = limits.get("max_hashtags", 30)
        
        return {
            "valid": char_count <= max_chars and hashtag_count <= max_hashtags,
            "character_count": char_count,
            "max_characters": max_chars,
            "hashtag_count": hashtag_count,
            "max_hashtags": max_hashtags,
            "within_limit": char_count <= max_chars,
            "hashtags_ok": hashtag_count <= max_hashtags
        }
    
    def shorten_if_needed(self, text: str, max_length: int) -> str:
        """Shorten text to fit within limit."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    def format_report(self, package: Dict) -> str:
        """Format publishing package as readable report."""
        report = f"""📱 PUBLISHING PACKAGE READY

PRIMARY PLATFORM: {package['primary_platform'].upper()}

{'='*70}
📸 INSTAGRAM ({package['character_counts']['instagram']} chars)
{'='*70}
{package['instagram_post']}

{'='*70}
🐦 TWITTER/X ({package['character_counts']['twitter']} chars)
{'='*70}
{package['twitter_post']}

{'='*70}
💼 LINKEDIN ({package['character_counts']['linkedin']} chars)
{'='*70}
{package['linkedin_post']}

{'='*70}
📘 FACEBOOK ({package['character_counts']['facebook']} chars)
{'='*70}
{package['facebook_post']}
"""
        return report
