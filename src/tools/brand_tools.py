# src/tools/brand_tools.py
"""
Brand Tools - Embedding-based brand alignment checking
Uses MiniLM-L6-v2 for semantic similarity scoring
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from crewai.tools import tool
from typing import Dict, List


# Load the embedding model (MiniLM-L6-v2 - lightweight and fast)
print("Loading MiniLM-L6-v2 embedding model...")
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✅ Embedding model loaded!")


@tool("Check Brand Alignment with Embeddings")
def check_brand_alignment(content: str, brand_voice: str = "inspiring, authentic, sustainable, empowering") -> str:
    """
    Checks how well content aligns with brand voice using semantic embeddings.
    Returns a brand alignment score (0-100) and specific feedback.
    
    Args:
        content: The content to check
        brand_voice: Description of the desired brand voice/values
    
    Returns:
        String with alignment score and feedback
    """
    
    try:
        # Define brand guidelines (can be customized)
        brand_guidelines = {
            "voice_attributes": [
                "inspiring and motivational",
                "authentic and genuine", 
                "sustainable and eco-conscious",
                "empowering and positive",
                "transparent and honest"
            ],
            "avoid_terms": [
                "manipulative marketing",
                "aggressive sales tactics",
                "false urgency",
                "misleading claims"
            ]
        }
        
        # Generate embeddings
        content_embedding = embedding_model.encode([content])
        
        # Check alignment with positive brand attributes
        positive_scores = []
        for attribute in brand_guidelines["voice_attributes"]:
            attr_embedding = embedding_model.encode([attribute])
            similarity = cosine_similarity(content_embedding, attr_embedding)[0][0]
            positive_scores.append(similarity)
        
        # Check distance from negative attributes
        negative_scores = []
        for avoid_term in brand_guidelines["avoid_terms"]:
            avoid_embedding = embedding_model.encode([avoid_term])
            similarity = cosine_similarity(content_embedding, avoid_embedding)[0][0]
            negative_scores.append(similarity)
        
        # Calculate overall brand alignment score
        positive_avg = np.mean(positive_scores)
        negative_avg = np.mean(negative_scores)
        
        # Score formula: favor positive attributes, penalize negative ones
        brand_score = int((positive_avg * 100) - (negative_avg * 30))
        brand_score = max(0, min(100, brand_score))  # Clamp between 0-100
        
        # Determine alignment level
        if brand_score >= 85:
            alignment = "EXCELLENT"
        elif brand_score >= 70:
            alignment = "GOOD"
        elif brand_score >= 55:
            alignment = "MODERATE"
        else:
            alignment = "WEAK"
        
        # Generate detailed feedback
        result = f"""
🧠 BRAND ALIGNMENT CHECK (Semantic Embeddings)

Brand Score: {brand_score}/100
Alignment Level: {alignment}

SIMILARITY ANALYSIS:
✓ Inspiring & Motivational: {positive_scores[0]:.2f}
✓ Authentic & Genuine: {positive_scores[1]:.2f}
✓ Sustainable & Eco-conscious: {positive_scores[2]:.2f}
✓ Empowering & Positive: {positive_scores[3]:.2f}
✓ Transparent & Honest: {positive_scores[4]:.2f}

NEGATIVE ATTRIBUTE CHECK:
✗ Manipulative Marketing: {negative_scores[0]:.2f} (lower is better)
✗ Aggressive Sales Tactics: {negative_scores[1]:.2f} (lower is better)
✗ False Urgency: {negative_scores[2]:.2f} (lower is better)
✗ Misleading Claims: {negative_scores[3]:.2f} (lower is better)

RECOMMENDATION:
"""
        
        if brand_score >= 85:
            result += "✅ Content strongly aligns with brand voice. Approved!"
        elif brand_score >= 70:
            result += "✅ Content aligns well with brand. Minor refinements suggested."
        elif brand_score >= 55:
            result += "⚠️ Content moderately aligns. Consider strengthening brand voice."
        else:
            result += "❌ Content weakly aligns with brand. Significant revision needed."
        
        return result
        
    except Exception as e:
        return f"❌ Error in brand alignment check: {str(e)}"


@tool("Compare Content Similarity")
def compare_content_similarity(content1: str, content2: str) -> str:
    """
    Compares semantic similarity between two pieces of content.
    Useful for checking consistency across multiple posts.
    
    Returns similarity score (0-100).
    """
    
    try:
        # Generate embeddings
        embedding1 = embedding_model.encode([content1])
        embedding2 = embedding_model.encode([content2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(embedding1, embedding2)[0][0]
        similarity_score = int(similarity * 100)
        
        result = f"""
📊 CONTENT SIMILARITY ANALYSIS

Similarity Score: {similarity_score}/100

"""
        
        if similarity_score >= 80:
            result += "✅ Very similar content (may be too repetitive)"
        elif similarity_score >= 50:
            result += "✅ Moderately similar (good consistency)"
        else:
            result += "⚠️ Low similarity (check brand consistency)"
        
        return result
        
    except Exception as e:
        return f"❌ Error in similarity check: {str(e)}"


# Test the tools
if __name__ == "__main__":
    print("\n🧪 Testing Brand Tools with Embeddings...\n")
    
    # Test content 1: Good brand alignment
    good_content = """
    Step into sustainable style with EcoStep! 🌱
    Our sneakers are crafted from recycled materials and organic cotton.
    Every pair supports reforestation. Look good, feel good, do good.
    Shop now: ecostep.com
    """
    
    # Test content 2: Poor brand alignment
    bad_content = """
    HURRY!!! Only 3 left in stock!!!
    Buy NOW or miss out FOREVER!!!
    Our sneakers will make you RICH and FAMOUS!!!
    Limited time 90% OFF - Don't be stupid, BUY NOW!!!
    """
    
    print("="*60)
    print("TEST 1: GOOD BRAND ALIGNMENT")
    print("="*60)
    result1 = check_brand_alignment.run(good_content)
    print(result1)
    
    print("\n" + "="*60)
    print("TEST 2: POOR BRAND ALIGNMENT")
    print("="*60)
    result2 = check_brand_alignment.run(bad_content)
    print(result2)
    
    print("\n" + "="*60)
    print("TEST 3: CONTENT SIMILARITY")
    print("="*60)
    result3 = compare_content_similarity.run(good_content, bad_content)
    print(result3)
    
    print("\n✅ All embedding tests completed!")
