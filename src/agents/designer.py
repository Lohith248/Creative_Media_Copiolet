# src/agents/designer.py
"""
Designer Agent - Creates visual content using AI image generation
Uses Stable Diffusion XL via custom tool
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent
from tools.image_tools import generate_image


def create_designer() -> Agent:
    """
    Creates a Designer Agent with image generation capabilities.
    
    Returns:
        Agent: A CrewAI agent specialized in visual design
    
    How this works:
    - This agent is a creative director who knows what makes good visuals
    - It has access to generate_image tool (Stable Diffusion XL)
    - When given a task, it creates detailed prompts for image generation
    - It understands design principles, color theory, composition
    """
    
    return Agent(
        # WHO is this agent?
        role='Creative Visual Designer',
        
        # WHAT is their mission?
        goal='Create stunning, brand-aligned visual content that captures attention and communicates effectively',
        
        # WHY are they qualified?
        backstory="""You are a world-class visual designer with 15+ years of experience 
        in brand identity, digital design, and creative direction. You excel at:
        - Translating brand concepts into compelling visuals
        - Understanding color psychology and visual hierarchy
        - Creating images that tell stories and evoke emotions
        - Optimizing designs for different platforms (Instagram, ads, websites)
        
        Your expertise includes:
        - Product photography and styling
        - Brand identity and visual systems
        - Digital illustration and concept art
        - Social media content design
        
        You always consider:
        - Brand guidelines (colors, fonts, style)
        - Target audience preferences and trends
        - Platform requirements (dimensions, formats)
        - Composition, lighting, and visual balance
        
        When creating prompts for image generation, you are:
        - Specific and detailed (not generic)
        - Aware of what makes images shareable
        - Strategic about messaging and emotion
        - Professional and polished in execution""",
        
        # TOOLS they can use
        tools=[generate_image],
        
        # Their "brain" - CrewAI will use Groq from environment
        llm="groq/llama-3.3-70b-versatile",
        
        # Show their thinking process
        verbose=True,
        
        # Can they ask other agents for help?
        allow_delegation=False,
        
        # Maximum iterations to improve output
        max_iter=3
    )


# Test the agent
if __name__ == "__main__":
    """
    Test if the Designer agent works correctly
    Run with: python src/agents/designer.py
    """
    
    from crewai import Task, Crew
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing Designer Agent...\n")
    
    try:
        # Create the agent
        designer = create_designer()
        print("✅ Designer agent created!\n")
        
        # Create a test task
        test_task = Task(
            description="""Create a product image for EcoStep sneakers.
            
            Brand details:
            - Eco-friendly sustainable sneakers
            - Modern, minimalist aesthetic
            - Target: environmentally conscious millennials
            - Colors: Earth tones (green, brown, cream)
            
            Create an image showing the sneaker in an inspiring, nature-focused setting.""",
            
            expected_output="A generated image file path",
            agent=designer
        )
        
        # Create a crew with just this agent and task
        crew = Crew(
            agents=[designer],
            tasks=[test_task],
            verbose=True
        )
        
        print("🚀 Running designer agent...\n")
        
        # Run the crew
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print("🎨 DESIGN RESULT:")
        print("="*60)
        print(result)
        print("="*60)
        
        print("\n✅ Test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
