"""
Content Writer Agent - Creates engaging written content
"""

from crewai import Agent


def create_content_writer() -> Agent:
    """Creates a Content Writer Agent specialized in brand-aligned copy."""
    
    return Agent(
        role='Professional Content Writer',
        goal='Create engaging, brand-aligned content that resonates with target audiences',
        backstory="""You are an award-winning content writer with 10+ years of experience 
        in digital marketing and brand storytelling. You excel at crafting compelling narratives,
        adapting tone to match brand voice, and writing clear, creative copy. You always consider
        target audience preferences, brand guidelines, platform-specific best practices, and
        engagement optimization. Your writing is thoughtful, strategic, and impactful.""",
        tools=[],
        llm="groq/llama-3.1-8b-instant",
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )

if __name__ == "__main__":
    from crewai import Task, Crew
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing Content Writer Agent...\n")
    
    try:
        writer = create_content_writer()
        print("✅ Content Writer agent created!\n")
        
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