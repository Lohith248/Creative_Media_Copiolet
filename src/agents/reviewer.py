# src/agents/reviewer.py
"""
Reviewer Agent - Quality checks and scoring for content
Uses Llama 3.1 via Groq to evaluate content quality, readability, and engagement
"""

from crewai import Agent


def create_reviewer() -> Agent:
    """
    Creates a Reviewer Agent that scores content quality.
    
    Returns:
        Agent: A CrewAI agent specialized in content review and scoring
    
    How this works:
    - Takes content from Writer agent
    - Evaluates on multiple dimensions (quality, readability, engagement)
    - Provides numerical scores (1-10 scale)
    - Gives specific feedback for improvements
    - Can trigger iterations if scores are too low
    """
    
    return Agent(
        # WHO is this agent?
        role='Senior Content Reviewer & Quality Analyst',
        
        # WHAT is their mission?
        goal='Evaluate content quality and provide actionable feedback with numerical scores to ensure excellence',
        
        # WHY are they qualified?
        backstory="""You are a meticulous content reviewer with 15+ years of experience 
        in editorial quality control, content strategy, and digital marketing analytics.
        
        Your expertise includes:
        - Content quality assessment (clarity, impact, professionalism)
        - Readability analysis (tone, flow, structure)
        - Engagement prediction (hooks, calls-to-action, shareability)
        - Brand voice consistency checking
        - Platform-specific content optimization
        
        Your review process is systematic and data-driven:
        
        1. QUALITY SCORE (1-10):
           - Grammar and spelling perfection
           - Message clarity and coherence
           - Professional polish
           - Appropriate length and structure
           
        2. READABILITY SCORE (1-10):
           - Easy to understand
           - Natural flow and rhythm
           - Appropriate vocabulary for audience
           - Good paragraph/sentence structure
           
        3. ENGAGEMENT SCORE (1-10):
           - Strong hook/opening
           - Emotional resonance
           - Clear value proposition
           - Effective call-to-action
           - Shareability factor
        
        You ALWAYS provide your evaluation in this EXACT format:
        
        ---SCORES---
        Quality: [score]/10
        Readability: [score]/10
        Engagement: [score]/10
        Overall: [average]/10
        ---END SCORES---
        
        FEEDBACK:
        [Specific, actionable suggestions for improvement]
        
        APPROVAL: [YES/NO - YES if overall score >= 7.5, NO otherwise]
        
        You are constructive but honest. If content needs work, you explain why clearly.
        If it's excellent, you celebrate it but still offer one improvement idea.""",
        
        # TOOLS they can use
        tools=[],
        
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
    Test if the Reviewer agent works correctly
    Run with: python src/agents/reviewer.py
    """
    
    from crewai import Task, Crew
    import sys
    import os
    
    # Add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing Reviewer Agent...\n")
    
    try:
        # Create the agent
        reviewer = create_reviewer()
        print("✅ Reviewer agent created!\n")
        
        # Sample content to review
        sample_content = """
        Step into sustainable style with EcoStep! 🌱👟
        
        Our sneakers are crafted from 100% recycled ocean plastic and organic cotton. 
        Every pair plants 5 trees. Look good, feel good, do good.
        
        Limited edition drop tomorrow at 9 AM PST. 
        Shop now: ecostep.com 
        
        #EcoFriendly #SustainableStyle #EcoStep
        """
        
        # Create a review task
        review_task = Task(
            description=f"""Review this Instagram post content and provide scores:
            
            CONTENT TO REVIEW:
            {sample_content}
            
            Brand: EcoStep (eco-friendly sneakers)
            Target Audience: Environmentally conscious millennials (25-35)
            Platform: Instagram
            
            Provide your evaluation with numerical scores and feedback.""",
            
            expected_output="Quality scores (1-10 scale), specific feedback, and approval decision",
            agent=reviewer
        )
        
        # Create a crew with just this agent
        crew = Crew(
            agents=[reviewer],
            tasks=[review_task],
            verbose=True
        )
        
        print("🚀 Running reviewer agent...\n")
        print("="*60)
        
        # Run the crew
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print("📊 REVIEW RESULT:")
        print("="*60)
        print(result)
        print("="*60)
        
        print("\n✅ Test successful!")
        
        # Try to parse scores (for demonstration)
        print("\n📈 Score Extraction Test:")
        if "---SCORES---" in str(result):
            print("✅ Structured scoring format detected!")
        else:
            print("⚠️  Agent returned feedback but may need format guidance")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
