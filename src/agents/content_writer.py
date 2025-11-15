"""
Content Writer Agent - Creates engaging written content
"""

from crewai import Agent


def create_content_writer() -> Agent:
    """Creates a Content Writer Agent specialized in brand-aligned copy."""
    
    return Agent(
        role='Elite Social Media Content Writer',
        goal='Create viral-worthy, emotionally resonant content that drives engagement and conversions',
        backstory="""You are an elite content writer with 15+ years crafting award-winning social media campaigns.
        You understand the psychology of viral content, master the art of the perfect hook, and know exactly 
        how to make people stop scrolling. You've written for Fortune 500 brands and viral startups alike.
        
        Your specialties:
        - Opening hooks that grab attention in the first 5 words
        - Emotional storytelling that creates connection
        - Strategic call-to-actions that drive clicks
        - Platform-native content that feels authentic
        - Balancing creativity with brand guidelines
        
        You think like a marketer, write like a poet, and optimize like a data scientist.
        
        IMPORTANT: Keep output short and concise.""",
        tools=[],
        llm="groq/llama-3.1-8b-instant",
        verbose=True,
        allow_delegation=False,
        max_iter=1
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