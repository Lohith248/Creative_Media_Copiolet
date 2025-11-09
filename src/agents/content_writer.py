# src/agents/content_writer.py
"""
Content Writer Agent - Creates engaging written content
Uses CrewAI framework to generate brand-aligned copy
"""

from crewai import Agent


def create_content_writer() -> Agent:
    """
    Creates a Content Writer Agent.
    
    Returns:
        Agent: A CrewAI agent specialized in content writing
    
    How this works:
    - CrewAI's Agent class creates a specialized AI assistant
    - The role/goal/backstory guide how it behaves
    - CrewAI will automatically use Groq if GROQ_API_KEY is in environment
    - When given a task, it generates content based on these instructions
    """
    
    return Agent(
        # WHO is this agent?
        role='Professional Content Writer',
        
        # WHAT is their mission?
        goal='Create engaging, brand-aligned content that resonates with target audiences',
        
        # WHY are they qualified? (This guides their behavior!)
        backstory="""You are an award-winning content writer with 10+ years of experience 
        in digital marketing and brand storytelling. You excel at:
        - Crafting compelling narratives that drive engagement
        - Adapting tone and style to match brand voice
        - Writing clear, concise, and creative copy
        - Understanding what makes content shareable and memorable
        
        You always consider:
        - Target audience preferences and pain points
        - Brand guidelines and voice consistency
        - Platform-specific best practices (Instagram, Twitter, LinkedIn, etc.)
        - SEO and engagement optimization
        
        Your writing is never generic - it's always thoughtful, strategic, and impactful.""",
        
        # TOOLS they can use (none needed for pure writing)
        tools=[],
        
        # Their "brain" - CrewAI will use Groq from environment
        # We specify the model we want from Groq
        llm="groq/llama-3.1-8b-instant",
        
        # Show their thinking process (helpful for debugging)
        verbose=True,
        
        # Can they ask other agents for help? (We'll set to True later)
        allow_delegation=False,
        
        # Maximum iterations to try improving their output
        max_iter=3
    )


# Test the agent
if __name__ == "__main__":
    """
    Test if the agent works correctly
    Run with: python src/agents/content_writer.py
    """
    
    from crewai import Task, Crew
    import sys
    import os
    
    # Add parent directory to path so we can import llm_loader
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load environment variables for GROQ_API_KEY
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing Content Writer Agent...\n")
    
    try:
        # Create the agent (it will use Groq automatically)
        writer = create_content_writer()
        print("✅ Content Writer agent created!\n")
        
        # 3. Create a test task
        test_task = Task(
            description="""Write an engaging Instagram caption (max 150 characters) 
            for a new eco-friendly sneaker brand called 'EcoStep'.
            
            Brand voice: Inspiring and authentic
            Key message: Sustainability meets style
            Include 2-3 relevant hashtags""",
            
            agent=writer,
            expected_output="Instagram caption with hashtags"
        )
        
        # 4. Create a crew with just this one agent
        test_crew = Crew(
            agents=[writer],
            tasks=[test_task],
            verbose=True
        )
        
        # 5. Run it!
        print("🚀 Running agent...\n")
        result = test_crew.kickoff()
        
        print("\n" + "="*60)
        print("📝 GENERATED CONTENT:")
        print("="*60)
        print(result)
        print("="*60)
        print("\n✅ Test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()