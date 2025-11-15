"""
Local Brand Guardian - Zero-Token Brand Alignment Checker
Uses only embeddings and rule-based checks (NO LLM calls)
"""

import re
from typing import Dict, List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np


class LocalBrandGuardian:
    """Brand alignment checker using local embeddings and rules (no LLM tokens)."""
    
    # Tone keywords mapping
    TONE_KEYWORDS = {
        "playful": ["fun", "enjoy", "exciting", "love", "wow", "amazing", "awesome", "yay", "cool"],
        "professional": ["streamline", "optimize", "efficient", "strategic", "innovative", "robust", "solution"],
        "casual": ["hey", "you", "your", "let's", "check out", "pretty", "really", "super"],
        "formal": ["therefore", "furthermore", "consequently", "accordingly", "respectively", "pertaining"],
        "friendly": ["welcome", "happy", "glad", "thanks", "great", "wonderful", "appreciate"],
        "inspiring": ["transform", "achieve", "empower", "breakthrough", "elevate", "unlock", "potential"],
        "urgent": ["now", "today", "limited", "hurry", "fast", "quick", "immediately", "don't miss"],
        "trustworthy": ["proven", "trusted", "certified", "guaranteed", "secure", "reliable", "authentic"]
    }
    
    # Forbidden phrases (red flags)
    FORBIDDEN_PHRASES = [
        "100% guaranteed", "instant cure", "miracle", "get rich quick",
        "free forever", "no risk", "proven to work", "doctors hate",
        "one weird trick", "shocking results", "lose weight fast",
        "make money fast", "too good to be true", "limited time only"
    ]
    
    def __init__(self, embedding_model: Optional[SentenceTransformer] = None):
        """Initialize with embedding model (shared from main app)."""
        self.embedding_model = embedding_model
        
    def check_brand_alignment(
        self,
        content: str,
        brand_voice_attributes: List[str],
        brand_values: List[str],
        brand_tone: str
    ) -> Dict:
        """
        Check brand alignment using embeddings + rules.
        Returns score 0-100 and detailed analysis.
        """
        
        # Clean content
        content_lower = content.lower()
        
        # 1. Semantic similarity with brand values
        values_score = self._check_values_alignment(content, brand_values)
        
        # 2. Tone matching
        tone_score = self._check_tone_match(content_lower, brand_tone, brand_voice_attributes)
        
        # 3. Voice attributes match
        voice_score = self._check_voice_attributes(content_lower, brand_voice_attributes)
        
        # 4. Forbidden phrases check
        forbidden_issues = self._check_forbidden_phrases(content_lower)
        
        # Calculate overall score
        overall_score = int((values_score * 0.4) + (tone_score * 0.3) + (voice_score * 0.3))
        
        # Penalties
        if forbidden_issues:
            overall_score -= len(forbidden_issues) * 15
            overall_score = max(0, overall_score)
        
        # Determine approval
        approved = overall_score >= 70 and len(forbidden_issues) == 0
        
        # Build recommendations
        recommendations = []
        if tone_score < 70:
            recommendations.append(f"Adjust tone to be more {brand_tone}")
        if voice_score < 70:
            recommendations.append(f"Strengthen voice attributes: {', '.join(brand_voice_attributes[:2])}")
        if values_score < 70:
            recommendations.append(f"Incorporate brand values: {', '.join(brand_values[:2])}")
        if forbidden_issues:
            recommendations.append(f"Remove problematic phrases: {', '.join(forbidden_issues[:2])}")
        
        return {
            "brand_score": overall_score,
            "tone_score": int(tone_score),
            "voice_score": int(voice_score),
            "values_score": int(values_score),
            "issues": forbidden_issues + ([f"Low tone match ({int(tone_score)}/100)"] if tone_score < 70 else []),
            "recommendations": recommendations,
            "approved": approved,
            "alignment_level": "STRONG" if overall_score >= 85 else "MODERATE" if overall_score >= 70 else "WEAK"
        }
    
    def _check_values_alignment(self, content: str, brand_values: List[str]) -> float:
        """Check semantic similarity between content and brand values."""
        if not self.embedding_model or not brand_values:
            return 75.0  # Default neutral score
        
        try:
            # Encode content and values
            content_embedding = self.embedding_model.encode(content, convert_to_tensor=False)
            values_text = " ".join(brand_values)
            values_embedding = self.embedding_model.encode(values_text, convert_to_tensor=False)
            
            # Cosine similarity
            similarity = np.dot(content_embedding, values_embedding) / (
                np.linalg.norm(content_embedding) * np.linalg.norm(values_embedding)
            )
            
            # Convert to 0-100 score
            score = float((similarity + 1) / 2 * 100)  # Normalize from [-1,1] to [0,100]
            return min(100, max(0, score))
            
        except Exception as e:
            print(f"⚠️ Embedding similarity failed: {e}")
            return 75.0
    
    def _check_tone_match(self, content_lower: str, brand_tone: str, voice_attrs: List[str]) -> float:
        """Check if content matches expected tone using keyword matching."""
        tone_lower = brand_tone.lower()
        
        # Get expected keywords for this tone
        expected_keywords = self.TONE_KEYWORDS.get(tone_lower, [])
        
        # Also check voice attributes for tone keywords
        for attr in voice_attrs:
            attr_lower = attr.lower()
            if attr_lower in self.TONE_KEYWORDS:
                expected_keywords.extend(self.TONE_KEYWORDS[attr_lower])
        
        if not expected_keywords:
            return 75.0  # Neutral if no keywords defined
        
        # Count matches
        matches = sum(1 for keyword in expected_keywords if keyword in content_lower)
        
        # Score based on percentage of keywords found
        score = (matches / len(set(expected_keywords))) * 100
        
        # Bonus for emoji (playful/casual tones)
        if tone_lower in ["playful", "casual", "friendly"]:
            emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
            if re.search(emoji_pattern, content_lower):
                score += 10
        
        return min(100, score + 50)  # Add base score
    
    def _check_voice_attributes(self, content_lower: str, voice_attrs: List[str]) -> float:
        """Check if content matches voice attributes."""
        if not voice_attrs:
            return 75.0
        
        total_score = 0
        for attr in voice_attrs:
            attr_lower = attr.lower()
            
            # Get keywords for this attribute
            keywords = self.TONE_KEYWORDS.get(attr_lower, [attr_lower])
            
            # Check presence
            matches = sum(1 for kw in keywords if kw in content_lower)
            attr_score = min(100, (matches / len(keywords)) * 100 + 60)
            total_score += attr_score
        
        return total_score / len(voice_attrs) if voice_attrs else 75.0
    
    def _check_forbidden_phrases(self, content_lower: str) -> List[str]:
        """Check for forbidden/spammy phrases."""
        issues = []
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase.lower() in content_lower:
                issues.append(phrase)
        return issues
    
    def format_report(self, result: Dict) -> str:
        """Format brand check result as readable text."""
        report = f"""Brand Score: {result['brand_score']}/100
Alignment Level: {result['alignment_level']}

SEMANTIC ANALYSIS:
• Values Alignment: {result['values_score']}/100
• Voice Match: {result['voice_score']}/100
• Tone Consistency: {result['tone_score']}/100

"""
        if result['issues']:
            report += "ISSUES DETECTED:\n"
            for issue in result['issues']:
                report += f"• {issue}\n"
            report += "\n"
        
        if result['recommendations']:
            report += "RECOMMENDATIONS:\n"
            for rec in result['recommendations']:
                report += f"• {rec}\n"
            report += "\n"
        
        report += f"APPROVAL: {'APPROVED' if result['approved'] else 'NEEDS REVISION'}"
        
        return report
