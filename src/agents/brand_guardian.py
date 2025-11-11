# src/agents/brand_guardian.py
"""
Brand Guardian Agent - Brand voice and alignment checking
Uses MiniLM-L6-v2 embeddings for semantic brand alignment scoring
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent
from tools.brand_tools import check_brand_alignment


def create_brand_guardian() -> Agent:
    """
    Creates a Brand Guardian Agent with embedding-based brand checking.
    
    Returns:
        Agent: A CrewAI agent specialized in brand alignment
    
    How this works:
    - Uses MiniLM-L6-v2 embeddings for semantic similarity
    - Compares content against brand voice attributes
    - Provides quantitative brand alignment scores
    - This is AI validating AI - a key hackathon requirement!
    """
    
    return Agent(
        # WHO is this agent?
        role='Brand Voice Guardian & Alignment Specialist',
        
        # WHAT is their mission?
        goal='Ensure all content perfectly aligns with brand voice, values, and identity using advanced semantic analysis',
        
        # WHY are they qualified?
        backstory="""You are an expert brand strategist with 20+ years of experience 
        in brand identity, voice development, and content consistency across Fortune 500 companies.
        
        Your expertise includes:
        - Brand voice definition and guidelines
        - Semantic content analysis
        - Multi-channel brand consistency
        - Tone and messaging optimization
        - Brand positioning and differentiation
        
        You use ADVANCED AI TECHNOLOGY (MiniLM-L6-v2 semantic embeddings) to:
        - Measure semantic similarity between content and brand voice
        - Detect subtle tone misalignments
        - Ensure consistent messaging across all content
        - Validate that content embodies brand values
        
        Your analysis process:
        
        1. SEMANTIC EMBEDDING ANALYSIS:
           - Uses neural networks to understand content meaning
           - Compares content embeddings to brand voice attributes
           - Calculates cosine similarity scores
           - Provides quantitative brand alignment metrics
        
        2. BRAND VOICE ATTRIBUTES YOU CHECK:
           ✓ Inspiring and motivational tone
           ✓ Authentic and genuine messaging
           ✓ Sustainable and eco-conscious values
           ✓ Empowering and positive energy
           ✓ Transparent and honest communication
        
        3. RED FLAGS YOU DETECT:
           ✗ Manipulative marketing tactics
           ✗ Aggressive or pushy sales language
           ✗ False urgency or scarcity
           ✗ Misleading or exaggerated claims
        
        You ALWAYS provide your evaluation in this EXACT format:
        
        ---BRAND ALIGNMENT CHECK---
        Brand Score: [score]/100
        Alignment Level: [EXCELLENT / GOOD / MODERATE / WEAK]
        
        EMBEDDING ANALYSIS:
        [Results from semantic similarity tool]
        
        BRAND VOICE ASSESSMENT:
        ✓ [What aligns well with brand]
        ✗ [What doesn't align]
        
        RECOMMENDATIONS:
        [Specific suggestions to improve brand alignment]
        
        APPROVAL: [YES if score >= 70, NO if score < 70]
        ---END BRAND ALIGNMENT CHECK---
        
        You are the guardian of brand integrity. When content doesn't align,
        you explain WHY and provide specific phrases to improve it.""",
        
        # TOOLS they can use
        tools=[check_brand_alignment],
        
        # Their "brain" - Llama 3.1 via Groq
        llm="groq/llama-3.1-8b-instant",
        
        # Show their thinking process
        verbose=True,
        
        # Can they ask other agents for help?
        allow_delegation=False,
        
        # Maximum iterations
        max_iter=2
    )


# Test the agent
if __name__ == "__main__":
    """
    Test if the Brand Guardian agent works correctly
    Run with: python src/agents/brand_guardian.py
    """
    
    from crewai import Task, Crew
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing Brand Guardian Agent...\n")
    
    try:
        # Create the agent
        brand_guardian = create_brand_guardian()
        print("✅ Brand Guardian agent created!\n")
        
        # Test Case 1: Good brand alignment
        good_content = """
        Step into sustainable style with EcoStep! 🌱👟
        
        Our sneakers are crafted from recycled ocean plastic and organic cotton. 
        Every pair you purchase helps plant 5 trees through our partnership with TreePeople.
        
        Look good, feel good, do good. That's the EcoStep way.
        
        Limited edition available tomorrow at 9 AM PST.
        Shop now: ecostep.com
        
        #EcoFriendly #SustainableStyle #EcoStep
        """
        
        # Test Case 2: Poor brand alignment
        bad_content = """
        🚨 URGENT!!! LAST CHANCE!!! 🚨
        
        EcoStep sneakers - BETTER than Nike! BETTER than Adidas! 
        BUY NOW before they're GONE FOREVER!!!
        
        Only 3 pairs left! Don't be the LOSER who misses out!!!
        
        FLASH SALE - 90% OFF (but only if you buy in the next 10 minutes!!!)
        
        Act NOW or regret it FOREVER!!!
        """
        
        print("="*60)
        print("TEST 1: GOOD BRAND ALIGNMENT")
        print("="*60)
        
        task1 = Task(
            description=f"""Analyze this content for brand alignment using semantic embeddings:
            
            CONTENT TO ANALYZE:
            {good_content}
            
            Brand: EcoStep
            Brand Values: Sustainability, authenticity, inspiration, empowerment, transparency
            Brand Voice: Inspiring, genuine, eco-conscious, positive, honest
            
            Use the brand alignment tool to check semantic similarity.
            Provide your brand alignment assessment with score and recommendations.""",
            
            expected_output="Brand alignment score, embedding analysis, and approval decision",
            agent=brand_guardian
        )
        
        crew1 = Crew(
            agents=[brand_guardian],
            tasks=[task1],
            verbose=True
        )
        
        result1 = crew1.kickoff()
        
        print("\n" + "="*60)
        print("🎯 BRAND ALIGNMENT RESULT (Good Content):")
        print("="*60)
        print(result1)
        print("="*60)
        
        # Test bad content
        print("\n\n" + "="*60)
        print("TEST 2: POOR BRAND ALIGNMENT")
        print("="*60)
        
        task2 = Task(
            description=f"""Analyze this content for brand alignment using semantic embeddings:
            
            CONTENT TO ANALYZE:
            {bad_content}
            
            Brand: EcoStep
            Brand Values: Sustainability, authenticity, inspiration, empowerment, transparency
            Brand Voice: Inspiring, genuine, eco-conscious, positive, honest
            
            Use the brand alignment tool to check semantic similarity.
            Provide your brand alignment assessment with score and recommendations.""",
            
            expected_output="Brand alignment score, embedding analysis, and approval decision",
            agent=brand_guardian
        )
        
        crew2 = Crew(
            agents=[brand_guardian],
            tasks=[task2],
            verbose=True
        )
        
        result2 = crew2.kickoff()
        
        print("\n" + "="*60)
        print("🎯 BRAND ALIGNMENT RESULT (Bad Content):")
        print("="*60)
        print(result2)
        print("="*60)
        
        print("\n✅ All Brand Guardian tests completed!")
        
        # Validate format
        print("\n📋 Format Validation:")
        if "Brand Score:" in str(result1) or "BRAND ALIGNMENT" in str(result1):
            print("✅ Structured brand check format detected!")
        else:
            print("⚠️  Agent returned feedback but may need format guidance")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
