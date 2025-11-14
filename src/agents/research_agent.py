"""
Research Agent - Market Intelligence & Strategic Analysis

Conducts market research, competitor analysis, and provides strategic insights
to inform campaign creation. Runs first in the workflow.
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
    
    Args:
        api_key: OpenRouter API key for Qwen3-14B
        serper_api_key: Serper API key for web search
        
    Returns:
        Configured CrewAI Agent for research tasks
    """
    
    serper_key = serper_api_key or os.getenv("SERPER_API_KEY")
    
    tools = []
    if serper_key:
        search_tool = SerperDevTool(api_key=serper_key)
        tools.append(search_tool)
        tool_note = "with web search capabilities"
    else:
        tool_note = "using LLM knowledge (add SERPER_API_KEY for live data)"
    
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
        llm="openrouter/qwen/qwen-2.5-72b-instruct:free",
        tools=tools,
        max_iter=15,
        memory=True,
    )


def format_research_output(research_result: str) -> dict:
    """
    Parse research agent output into structured format.
    
    Args:
        research_result: Raw output from research agent
        
    Returns:
        Structured dictionary with research findings
    """
    
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
        
        for trigger, key in sections.items():
            if trigger in line_lower and ':' in line_lower:
                current_section = key
                if ':' in line:
                    content = line.split(':', 1)[1].strip()
                    if content:
                        parsed[current_section] += content + "\n"
                break
        else:
            if current_section and line.strip():
                parsed[current_section] += line.strip() + "\n"
    
    for key in parsed:
        if key != "raw_research":
            parsed[key] = parsed[key].strip()
    
    return parsed


if __name__ == "__main__":
    from crewai import Task, Crew
    
    researcher = create_research_agent()
    
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
    
    parsed = format_research_output(str(result))
    
    print("\n" + "="*50)
    print("📋 PARSED RESEARCH:")
    print("="*50)
    for key, value in parsed.items():
        if key != "raw_research" and value:
            print(f"\n{key.upper().replace('_', ' ')}:")
            print(value)
