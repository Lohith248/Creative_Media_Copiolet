# src/agents/compliance_agent.py
"""
Compliance Agent - Legal, ethical, and copyright checks for content
Uses Llama 3.1 via Groq to detect potential compliance issues
"""

from crewai import Agent


def create_compliance_agent() -> Agent:
    """
    Creates a Compliance Agent that checks for legal/ethical issues.
    
    Returns:
        Agent: A CrewAI agent specialized in compliance checking
    
    How this works:
    - Scans content for copyright violations
    - Checks for misleading claims or false advertising
    - Identifies ethical concerns
    - Ensures legal compliance (disclaimers, regulations)
    - Returns structured compliance status
    """
    
    return Agent(
        # WHO is this agent?
        role='Legal Compliance & Ethics Officer',
        
        # WHAT is their mission?
        goal='Identify and flag potential legal, ethical, and copyright issues in content to ensure compliance and minimize risk',
        
        # WHY are they qualified?
        backstory="""You are a meticulous compliance officer with 12+ years of experience 
        in digital media law, intellectual property, advertising regulations, and ethical standards.
        
        Your expertise includes:
        - Copyright and trademark law
        - FTC advertising guidelines
        - GDPR and privacy regulations
        - Truth in advertising standards
        - Social media platform policies
        - Ethical content guidelines
        - Risk assessment and mitigation
        
        Your compliance check process is thorough and systematic:
        
        1. COPYRIGHT CHECK:
           - Identifies potential trademark violations
           - Checks for copyrighted terms or phrases
           - Flags unauthorized brand mentions
           - Detects plagiarism indicators
        
        2. LEGAL CHECK:
           - Verifies claims are substantiated
           - Checks for required disclaimers
           - Identifies misleading statements
           - Ensures regulatory compliance
        
        3. ETHICAL CHECK:
           - Detects greenwashing or false eco-claims
           - Identifies discriminatory language
           - Checks for manipulative tactics
           - Ensures transparent messaging
        
        4. PLATFORM COMPLIANCE:
           - Verifies adherence to platform rules
           - Checks content guidelines compliance
           - Identifies potential violations
        
        You ALWAYS provide your evaluation in this EXACT format:
        
        ---COMPLIANCE CHECK---
        Status: [APPROVED / NEEDS REVIEW / REJECTED]
        Compliance Score: [score]/100
        
        ISSUES FOUND:
        [List each issue with severity: CRITICAL / MAJOR / MINOR]
        [If no issues: "No compliance issues detected."]
        
        IMPORTANT: Keep output short and concise.
        
        CHECKS PERFORMED:
        ✓ Copyright & Trademark
        ✓ Legal & Regulatory
        ✓ Ethical Standards
        ✓ Platform Policies
        
        RECOMMENDATIONS:
        [Specific actions to address issues, or "Content is compliant" if approved]
        ---END COMPLIANCE CHECK---
        
        You are protective but practical. Critical issues require immediate fixes.
        Minor issues are noted but don't block approval. You explain WHY something is a concern.""",
        
        # TOOLS they can use
        tools=[],
        
        # Their "brain" - Llama 3.1 8B (faster, lower TPM)
        llm="groq/llama-3.1-8b-instant",
        
        # Show their thinking process
        verbose=True,
        
        # Can they ask other agents for help?
        allow_delegation=False,
        
        # Maximum iterations
        max_iter=1
    )


# Test the agent
if __name__ == "__main__":
    """
    Test if the Compliance agent works correctly
    Run with: python src/agents/compliance_agent.py
    """
    
    from crewai import Task, Crew
    import sys
    import os
    
    # Add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing Compliance Agent...\n")
    
    try:
        # Create the agent
        compliance = create_compliance_agent()
        print("✅ Compliance agent created!\n")
        
        # Test Case 1: Clean content (should pass)
        clean_content = """
        Step into sustainable style with EcoStep! 🌱👟
        
        Our sneakers use recycled materials and organic cotton. 
        Every pair supports reforestation efforts.
        
        Limited edition available tomorrow at 9 AM PST.
        Shop now: ecostep.com
        
        #EcoFriendly #SustainableStyle #EcoStep
        """
        
        # Test Case 2: Content with issues (for demonstration)
        problematic_content = """
        EcoStep sneakers are 100% carbon neutral and will save the planet!
        
        Better than Nike and Adidas combined! Our shoes cure foot pain and 
        are scientifically proven to make you run 50% faster!
        
        Buy now before Greta Thunberg takes them all! 
        
        *Results may vary. No medical claims intended.
        """
        
        print("="*60)
        print("TEST 1: CLEAN CONTENT")
        print("="*60)
        
        # Create compliance check task
        task1 = Task(
            description=f"""Perform a comprehensive compliance check on this content:
            
            CONTENT TO CHECK:
            {clean_content}
            
            Brand: EcoStep (eco-friendly sneakers)
            Platform: Instagram
            Target Market: United States
            
            Check for legal, ethical, and copyright issues.""",
            
            expected_output="Compliance status, issues list (if any), and recommendations",
            agent=compliance
        )
        
        # Create a crew with just this agent
        crew1 = Crew(
            agents=[compliance],
            tasks=[task1],
            verbose=True
        )
        
        # Run the check
        result1 = crew1.kickoff()
        
        print("\n" + "="*60)
        print("🔍 COMPLIANCE RESULT (Clean Content):")
        print("="*60)
        print(result1)
        print("="*60)
        
        # Test problematic content
        print("\n\n" + "="*60)
        print("TEST 2: PROBLEMATIC CONTENT")
        print("="*60)
        
        task2 = Task(
            description=f"""Perform a comprehensive compliance check on this content:
            
            CONTENT TO CHECK:
            {problematic_content}
            
            Brand: EcoStep (eco-friendly sneakers)
            Platform: Instagram
            Target Market: United States
            
            Check for legal, ethical, and copyright issues.""",
            
            expected_output="Compliance status, issues list, and recommendations",
            agent=compliance
        )
        
        crew2 = Crew(
            agents=[compliance],
            tasks=[task2],
            verbose=True
        )
        
        result2 = crew2.kickoff()
        
        print("\n" + "="*60)
        print("🔍 COMPLIANCE RESULT (Problematic Content):")
        print("="*60)
        print(result2)
        print("="*60)
        
        print("\n✅ All tests completed!")
        
        # Check if structured format is present
        print("\n📋 Format Validation:")
        if "---COMPLIANCE CHECK---" in str(result1) or "Status:" in str(result1):
            print("✅ Structured compliance format detected!")
        else:
            print("⚠️  Agent returned feedback but may need format guidance")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
