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
        backstory="""You are a world-class visual designer specialized in creating professional marketing visuals.

YOUR EXPERTISE:
- Product photography and commercial styling
- Brand-aligned visual content
- Platform-optimized design (Instagram, Twitter, LinkedIn, Facebook)
- Professional lighting and composition

PROMPT ENGINEERING RULES:
When creating image generation prompts, use this EXACT structure:

"High-quality [product/concept] marketing visual, [platform] format, 
professional studio lighting, [brand colors if specified], clean background,
sharp focus, modern aesthetic, [product] in center frame, no text overlay,
no watermarks, ultra realistic, commercial photography style, [specific mood/tone]"

EXAMPLE GOOD PROMPTS:
✅ "High-quality sustainable sneaker marketing visual, Instagram square format, 
professional studio lighting, earth tones (green, brown, cream), clean white background,
sharp focus, modern minimalist aesthetic, sneaker in center frame, no text overlay,
no watermarks, ultra realistic, commercial photography style, eco-friendly natural mood"

✅ "High-quality smartwatch product marketing visual, professional studio lighting,
tech blue and silver colors, clean gradient background, sharp focus, modern tech aesthetic,
watch in center frame displaying interface, no text overlay, ultra realistic, 
commercial photography style, innovative cutting-edge mood"

❌ AVOID generic prompts like: "a sneaker", "cool product", "nice image"

CRITICAL RULES:
- NO text/typography in generated images
- NO watermarks or logos
- ALWAYS specify "commercial photography style"
- ALWAYS mention lighting: "professional studio lighting"
- ALWAYS specify composition: "center frame" or "product focus"
- ALWAYS include mood/tone at end
        
IMPORTANT: Keep output short and concise.""",
        
        # TOOLS they can use
        tools=[generate_image],
        
        # Their "brain" - CrewAI will use Groq from environment
        llm="groq/llama-3.1-8b-instant",
        
        # Show their thinking process
        verbose=True,
        
        # Can they ask other agents for help?
        allow_delegation=False,
        
        # Maximum iterations to improve output
        max_iter=1
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
