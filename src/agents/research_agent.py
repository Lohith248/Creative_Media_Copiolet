"""
Research Agent - Market Intelligence & Strategic Analysis

This agent conducts market research, competitor analysis, and provides
strategic insights to inform campaign creation. It runs FIRST in the workflow,
gathering context before content generation begins.

Model: Qwen3-14B via OpenRouter (FREE tier)
Why this approach:
- Qwen3-14B: Specifically optimized for agentic tasks and function calling
- OpenRouter: Provides FREE unlimited access via :free tier
- Superior to Llama for research and analytical reasoning
- Perfect for hackathon (100% free, no usage limits)
- Better web search integration and tool use
"""

from crewai import Agent
from crewai_tools import SerperDevTool
from typing import Optional
import os


def create_research_agent(
    api_key: Optional[str] = None,
    serper_api_key: Optional[str] = None
) -> Agent:
    """
    Create a Research Agent for market intelligence gathering.
    
    This agent:
    1. Conducts web searches for market trends
    2. Analyzes competitor content strategies
    3. Identifies target audience insights
    4. Provides strategic framework recommendations
    5. Gathers real-time data to inform content creation
    
    Args:
        api_key: OpenRouter API key for Qwen3-14B (free tier)
        serper_api_key: Serper API key for web search (optional but recommended)
        
    Returns:
        Configured CrewAI Agent for research tasks
        
    Note:
        - Uses Qwen3-14B via OpenRouter (FREE unlimited access)
        - Qwen is optimized for agentic reasoning and function calling
        - Superior to Llama for research and analytical tasks
        - OpenAI-compatible API format
        - Web search is optional but enhances capabilities
        - Outputs structured research reports
    """
    
    # Get API keys from environment if not provided
    # Note: Groq API key is read automatically by CrewAI from GROQ_API_KEY env var
    serper_key = serper_api_key or os.getenv("SERPER_API_KEY")
    
    # Initialize web search tool if API key available
    tools = []
    if serper_key:
        search_tool = SerperDevTool(api_key=serper_key)
        tools.append(search_tool)
        tool_note = "with web search capabilities"
    else:
        tool_note = "using LLM knowledge (web search disabled - add SERPER_API_KEY for live data)"
    
    return Agent(
        role="Market Research Analyst",
        
        goal=(
            "Conduct comprehensive market research and competitive analysis "
            "to provide strategic insights that inform creative campaign development"
        ),
        
        backstory=(
            "You are an expert market research analyst with deep expertise in "
            "digital marketing trends, consumer behavior, and competitive intelligence. "
            "Your research uncovers valuable insights about target audiences, market "
            "positioning, and content strategies that drive engagement. You analyze "
            "data objectively and present findings in clear, actionable formats.\n\n"
            f"Current capabilities: {tool_note}"
        ),
        
        verbose=True,
        allow_delegation=False,
        
        # Use Qwen3-14B via OpenRouter (FREE tier)
        # This model is specifically optimized for:
        # - Function calling and tool use (perfect for web search)
        # - Agentic reasoning and research tasks
        # - Structured output generation
        # - Better performance than Llama models for research
        # OpenRouter provides FREE unlimited access via :free tier
        llm="openrouter/qwen/qwen3-14b:free",
        
        tools=tools,
        
        # Research agent focuses on comprehensive, analytical outputs
        max_iter=15,  # Allow more iterations for thorough research
        memory=True,
    )


def format_research_output(research_result: str) -> dict:
    """
    Parse research agent output into structured format.
    
    Expected output structure from research agent:
    - Market Trends: Current trends in the industry
    - Target Audience Insights: Demographics, psychographics, pain points
    - Competitor Analysis: What competitors are doing
    - Strategic Recommendations: Suggested approaches
    - Key Messages: Core messages to emphasize
    
    Args:
        research_result: Raw output from research agent
        
    Returns:
        Structured dictionary with research findings
    """
    
    # Initialize structure
    parsed = {
        "market_trends": "",
        "audience_insights": "",
        "competitor_analysis": "",
        "strategic_recommendations": "",
        "key_messages": "",
        "raw_research": research_result
    }
    
    # Try to parse structured sections
    sections = {
        "market trends": "market_trends",
        "target audience insights": "audience_insights",
        "audience insights": "audience_insights",
        "competitor analysis": "competitor_analysis",
        "strategic recommendations": "strategic_recommendations",
        "recommendations": "strategic_recommendations",
        "key messages": "key_messages",
        "messaging": "key_messages"
    }
    
    current_section = None
    lines = research_result.split('\n')
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check if this line is a section header
        for trigger, key in sections.items():
            if trigger in line_lower and ':' in line_lower:
                current_section = key
                # Extract content after colon if present
                if ':' in line:
                    content = line.split(':', 1)[1].strip()
                    if content:
                        parsed[current_section] += content + "\n"
                break
        else:
            # Add line to current section
            if current_section and line.strip():
                parsed[current_section] += line.strip() + "\n"
    
    # Clean up sections
    for key in parsed:
        if key != "raw_research":
            parsed[key] = parsed[key].strip()
    
    return parsed


# Example usage and testing
if __name__ == "__main__":
    """
    Test the research agent with a sample query.
    """
    
    from crewai import Task, Crew
    
    # Create research agent
    researcher = create_research_agent()
    
    # Define a research task
    research_task = Task(
        description=(
            "Research the current state of sustainable fashion marketing. "
            "Provide insights on:\n"
            "1. Latest trends in eco-friendly fashion advertising\n"
            "2. Target audience (demographics, values, pain points)\n"
            "3. Successful competitor campaigns\n"
            "4. Recommended messaging strategies\n"
            "5. Key messages that resonate with conscious consumers\n\n"
            "Format your output with clear sections for each topic."
        ),
        expected_output=(
            "Structured research report with sections on market trends, "
            "audience insights, competitor analysis, strategic recommendations, "
            "and key messaging points"
        ),
        agent=researcher
    )
    
    # Execute research
    print("🔍 Starting Market Research...\n")
    
    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=True
    )
    
    result = crew.kickoff()
    
    print("\n" + "="*50)
    print("📊 RESEARCH RESULTS:")
    print("="*50)
    print(result)
    
    # Parse output
    parsed = format_research_output(str(result))
    
    print("\n" + "="*50)
    print("📋 PARSED RESEARCH:")
    print("="*50)
    for key, value in parsed.items():
        if key != "raw_research" and value:
            print(f"\n{key.upper().replace('_', ' ')}:")
            print(value)
