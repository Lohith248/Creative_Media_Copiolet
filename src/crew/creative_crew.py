# src/crew/creative_crew.py
"""
Creative Media Co-Pilot Crew - Multi-Agent Orchestration System
Coordinates 5 specialized agents for automated content creation with validation
"""

import sys
import os
from datetime import datetime
import json
from pathlib import Path
import random
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Groq API Key Rotation
def get_groq_api_key():
    """Rotate between multiple Groq API keys to avoid rate limits."""
    keys = []
    for i in range(1, 5):  # Support up to 4 keys
        key_name = f"GROQ_API_KEY_{i}" if i > 1 else "GROQ_API_KEY"
        key = os.getenv(key_name)
        if key:
            keys.append(key)
    
    if not keys:
        raise ValueError("No Groq API keys found in environment!")
    
    # Randomly select a key to distribute load
    selected_key = random.choice(keys)
    os.environ["GROQ_API_KEY"] = selected_key
    print(f"🔑 Using Groq API Key #{keys.index(selected_key) + 1} of {len(keys)}")
    return selected_key

# Set initial key
get_groq_api_key()

from crewai import Task, Crew
from agents.content_writer import create_content_writer
from agents.designer import create_designer
from agents.reviewer import create_reviewer
from agents.compliance_agent import create_compliance_agent
from agents.brand_guardian import create_brand_guardian
from models.campaign_brief import CampaignBrief, PLATFORM_PRESETS, BRAND_PRESETS


class CreativeMediaCrew:
    """
    Multi-agent creative workflow orchestrator.
    
    Workflow:
    1. Writer creates content
    2. Designer creates visual
    3. Reviewer scores content (quality, readability, engagement)
    4. Compliance checks for legal/ethical issues
    5. Brand Guardian validates brand alignment
    6. If any checks fail → iterate (max 3 times)
    7. Bundle outputs with metadata
    """
    
    def __init__(self, max_iterations=3):
        """
        Initialize the crew with all agents.
        
        Args:
            max_iterations: Maximum refinement cycles (default: 3)
        """
        self.max_iterations = max_iterations
        self.current_iteration = 0
        
        # Initialize all 5 agents
        print("🤖 Initializing Creative Media Crew...")
        self.writer = create_content_writer()
        self.designer = create_designer()
        self.reviewer = create_reviewer()
        self.compliance = create_compliance_agent()
        self.brand_guardian = create_brand_guardian()
        print("✅ All 5 agents initialized!\n")
        
        # Metadata tracking
        self.campaign_metadata = {
            "agents_used": [],
            "iterations": [],
            "scores": {},
            "start_time": None,
            "end_time": None
        }
    
    def create_campaign(self, brief: CampaignBrief, include_research: bool = False) -> dict:
        """
        Create a complete campaign with multi-agent collaboration.
        
        Args:
            brief: CampaignBrief object with all campaign context
            include_research: Whether to run market research before content creation
        
        Returns:
            dict with content, image_path, scores, metadata
        """
        
        self.campaign_metadata["start_time"] = datetime.now().isoformat()
        self.campaign_metadata["brand"] = brief.brand.name
        self.campaign_metadata["platform"] = brief.platform.name
        self.current_iteration = 0
        
        print("="*70)
        print("🚀 STARTING MULTI-AGENT CREATIVE WORKFLOW")
        print("="*70)
        print(f"Campaign: {brief.objective}")
        print(f"Brand: {brief.brand.name} ({brief.brand.industry})")
        print(f"Audience: {brief.target_audience}")
        print(f"Platform: {brief.platform.name.upper()}\n")
        
        # Optional market research
        research_insights = ""
        if include_research:
            print("🔍 STEP 0: Market Research Agent")
            print("-" * 70)
            try:
                from agents.research_agent import create_research_agent
                researcher = create_research_agent()
                
                research_task = Task(
                    description=f"""
Research the {brief.product_name} industry and {brief.target_audience} market. Provide:
1. Current market trends and consumer behavior
2. Competitor strategies on {brief.platform.name}
3. Target audience preferences and pain points
4. Recommended messaging approach

Keep it concise - 3-4 key insights.""",
                    expected_output="Concise market research with trends, competitors, audience insights, and recommendations",
                    agent=researcher
                )
                
                research_crew = Crew(
                    agents=[researcher],
                    tasks=[research_task],
                    verbose=False
                )
                
                research_result = str(research_crew.kickoff())
                research_insights = f"\n\nMARKET RESEARCH INSIGHTS:\n{research_result}\n"
                self.campaign_metadata["research"] = research_result
                print("✅ Research complete!\n")
            except Exception as e:
                print(f"⚠️ Research failed: {e}\n")
                research_insights = ""
        
        # Iteration loop
        content = None
        image_path = None
        approved = False
        feedback_history = []
        
        while self.current_iteration < self.max_iterations and not approved:
            self.current_iteration += 1
            iteration_data = {
                "iteration": self.current_iteration,
                "timestamp": datetime.now().isoformat(),
                "agents": []
            }
            
            print(f"\n{'='*70}")
            print(f"🔄 ITERATION {self.current_iteration}/{self.max_iterations}")
            print(f"{'='*70}\n")
            
            # Build feedback string from previous iteration
            previous_feedback = ""
            if self.current_iteration > 1 and feedback_history:
                previous_feedback = "\n\nPREVIOUS ITERATION FEEDBACK:\n" + "\n".join(feedback_history[-1:])
            
            # STEP 1: Content Writer
            print("📝 STEP 1: Content Writer Agent")
            print("-" * 70)
            
            writer_task = Task(
                description=f"""{brief.to_context_string()}

PLATFORM BEST PRACTICES:
{chr(10).join(f"• {bp}" for bp in brief.platform.best_practices)}
{research_insights}

🎯 YOUR MISSION:
Create {brief.platform.name} content that makes people STOP scrolling and TAKE ACTION.

📝 CONTENT REQUIREMENTS:
1. CHARACTER LIMIT: {brief.platform.optimal_chars} chars (MAX {brief.platform.max_chars})
2. OPENING HOOK: First 5-10 words must grab attention immediately
3. BRAND VOICE: {', '.join(brief.brand.voice_attributes)}
4. CALL-TO-ACTION: {brief.call_to_action}
5. HASHTAGS: {brief.platform.hashtag_limit} or fewer, highly relevant
6. TARGET AUDIENCE: {brief.target_audience}
7. KEY MESSAGE: {brief.key_message}

🧠 PSYCHOLOGY TRIGGERS TO USE:
- Curiosity gap (make them want to learn more)
- Emotion (joy, inspiration, surprise, urgency)
- Social proof (community, belonging)
- Value proposition (what's in it for them?)

✍️ WRITING FRAMEWORK:
Line 1: HOOK - Stop the scroll (question, bold statement, or surprising fact)
Line 2-3: PROBLEM/BENEFIT - Why this matters to them
Line 4-5: SOLUTION/VALUE - What you're offering
Line 6: CALL-TO-ACTION - Clear next step
Hashtags: Relevant and discoverable

TONE: {brief.brand.tone}
CONTENT TYPE: {brief.content_type}
{previous_feedback}

⚠️ AVOID:
- Generic openings like "Hey there!" or "Check this out"
- Salesy language that feels pushy
- Too many emojis (2-4 max for {brief.platform.name})
- Vague calls-to-action

REQUIRED OUTPUT FORMAT:
[Main Content]
(Your engaging post text here - make every word count!)

[Hashtags]
#hashtag1 #hashtag2 #hashtag3

[Character Count]
Total: XXX characters""",
                
                expected_output="Formatted social media post with compelling hook, emotional resonance, clear value proposition, and strategic hashtags",
                agent=self.writer
            )
            
            writer_crew = Crew(
                agents=[self.writer],
                tasks=[writer_task],
                verbose=False
            )
            
            max_retries = 4  # Try all 4 keys if needed
            for attempt in range(max_retries):
                try:
                    content = str(writer_crew.kickoff())
                    break  # Success!
                except Exception as e:
                    if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                        print(f"⚠️ Rate limit hit on key #{attempt + 1}! Switching to next Groq API key...")
                        get_groq_api_key()  # Switch to different key
                        # Recreate the agent with new key
                        self.writer = create_content_writer()
                        writer_crew = Crew(
                            agents=[self.writer],
                            tasks=[writer_task],
                            verbose=False
                        )
                    else:
                        raise e
            print("✅ Content created!\n")
            iteration_data["agents"].append({
                "name": "Content Writer",
                "output": str(content)[:200] + "..."
            })
            
            # STEP 2: Designer
            print("🎨 STEP 2: Designer Agent")
            print("-" * 70)
            
            # Build visual style description
            visual_desc = f"{brief.brand.visual_style}" if brief.brand.visual_style else "professional and engaging"
            color_desc = f"Color palette: {', '.join(brief.brand.color_palette)}" if brief.brand.color_palette else ""
            
            designer_task = Task(
                description=f"""{brief.to_context_string()}

🎨 VISUAL DESIGN BRIEF:
• Platform: {brief.platform.name}
• Image Ratio: {brief.platform.image_ratio}
• Visual Style: {visual_desc}
• {color_desc}
• Mood: {brief.brand.tone}
• Brand: {brief.brand.name} ({brief.brand.industry})

📝 CONTENT CONTEXT:
{content}

🎯 YOUR MISSION:
Create a scroll-stopping visual that instantly communicates the message and drives engagement.

✨ DESIGN REQUIREMENTS:
1. COMPOSITION: {brief.platform.image_ratio} ratio optimized for {brief.platform.name}
2. FOCAL POINT: Clear main subject that draws the eye
3. BRAND ALIGNMENT: Reflects {visual_desc} aesthetic
4. COLOR PSYCHOLOGY: Use colors that evoke {brief.brand.tone} emotions
5. PLATFORM OPTIMIZATION: Mobile-first design (most users on phone)
6. MESSAGE: Visually represents "{brief.key_message}"

🧠 VISUAL PSYCHOLOGY:
- Create emotional connection through imagery
- Use negative space for breathing room
- Ensure text readability if any overlays
- Follow rule of thirds for composition
- Make it thumb-stopping worthy

🎨 STYLE GUIDELINES:
- Professional quality, not stock-photo generic
- {visual_desc} aesthetic throughout
- Consistent with brand identity
- Platform-native look and feel
- High contrast for mobile screens

⚠️ AVOID:
- Cluttered compositions
- Hard-to-read text
- Off-brand colors or styles
- Generic stock photo vibes
- Poor mobile viewing experience

Generate the image using your image generation tool. Make it memorable!""",
                
                expected_output="Generated image file path",
                agent=self.designer
            )
            
            designer_crew = Crew(
                agents=[self.designer],
                tasks=[designer_task],
                verbose=False
            )
            
            image_result = designer_crew.kickoff()
            image_path = str(image_result)
            print("✅ Image created!\n")
            iteration_data["agents"].append({
                "name": "Designer",
                "output": image_path
            })
            
            # STEP 3: Reviewer (Quality Scoring)
            print("📊 STEP 3: Reviewer Agent (Quality Scoring)")
            print("-" * 70)
            
            reviewer_task = Task(
                description=f"""{brief.to_context_string()}

CONTENT TO REVIEW:
{content}

YOUR TASK:
Evaluate this content across multiple dimensions and provide numerical scores with specific feedback.

REQUIRED OUTPUT FORMAT:
Quality Score: X/10
Readability Score: X/10
Engagement Score: X/10
Overall Score: X.X/10

STRENGTHS:
• [Specific strength 1]
• [Specific strength 2]

IMPROVEMENTS NEEDED:
• [Specific improvement 1]
• [Specific improvement 2]

APPROVAL: [APPROVED if Overall ≥7.5, otherwise NEEDS REVISION]

SCORING CRITERIA:
1. QUALITY (1-10):
   - Grammar and spelling perfection
   - Message clarity and coherence
   - Professional polish
   - Appropriate length ({brief.platform.optimal_chars} chars optimal)

2. READABILITY (1-10):
   - Easy to understand for target audience
   - Natural flow and rhythm
   - Appropriate vocabulary
   - Good structure and formatting

3. ENGAGEMENT (1-10):
   - Strong hook in first line
   - Emotional resonance
   - Clear call-to-action: {brief.call_to_action}
   - Platform-appropriate style for {brief.platform.name}
   - Shareability potential

Be specific and actionable in your feedback.""",
                
                expected_output="Structured scores with strengths and improvements",
                agent=self.reviewer
            )
            
            reviewer_crew = Crew(
                agents=[self.reviewer],
                tasks=[reviewer_task],
                verbose=False
            )
            
            max_retries = 4
            for attempt in range(max_retries):
                try:
                    review_result = reviewer_crew.kickoff()
                    break
                except Exception as e:
                    if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                        print("⚠️ Rate limit hit on reviewer! Switching to next Groq API key...")
                        get_groq_api_key()
                        self.reviewer = create_reviewer()
                        reviewer_crew = Crew(
                            agents=[self.reviewer],
                            tasks=[reviewer_task],
                            verbose=False
                        )
                    else:
                        raise e
            print("✅ Review complete!\n")
            
            # Parse scores from review
            review_scores = self._parse_review_scores(str(review_result))
            iteration_data["agents"].append({
                "name": "Reviewer",
                "scores": review_scores,
                "output": str(review_result)[:200] + "..."
            })
            
            # STEP 4: Compliance Check
            print("⚖️ STEP 4: Compliance Agent (Legal/Ethical Check)")
            print("-" * 70)
            
            avoid_list = brief.avoid_topics if brief.avoid_topics else ["None specified"]
            
            compliance_task = Task(
                description=f"""{brief.to_context_string()}

CONTENT TO CHECK:
{content}

YOUR TASK:
Perform thorough compliance analysis and identify any potential issues.

REQUIRED OUTPUT FORMAT:
Compliance Status: [APPROVED / NEEDS REVIEW / REJECTED]
Compliance Score: XXX/100

COPYRIGHT ISSUES:
• [Issue or "None detected"]

LEGAL ISSUES:
• [Issue or "None detected"]

ETHICAL CONCERNS:
• [Issue or "None detected"]

PLATFORM POLICY:
• [Issue or "None detected"]

SEVERITY: [CRITICAL / MAJOR / MINOR / NONE]

RECOMMENDATIONS:
• [Specific fix if needed]

CHECK CATEGORIES:
1. COPYRIGHT:
   - Trademark violations
   - Copyrighted terms/phrases
   - Unauthorized brand mentions

2. LEGAL:
   - Unsubstantiated claims
   - Required disclaimers
   - Misleading statements
   - {brief.platform.name} advertising policies

3. ETHICAL:
   - False eco-claims (greenwashing)
   - Manipulative tactics
   - Inappropriate content for {brief.target_audience}
   - Respect for diversity and inclusion

4. PLATFORM POLICY:
   - {brief.platform.name} community guidelines
   - Content restrictions
   - Prohibited content types

TOPICS TO AVOID: {', '.join(avoid_list)}

Score 90-100: APPROVED
Score 70-89: NEEDS REVIEW
Score <70: REJECTED""",
                
                expected_output="Structured compliance report with status and issues",
                agent=self.compliance
            )
            
            compliance_crew = Crew(
                agents=[self.compliance],
                tasks=[compliance_task],
                verbose=False
            )
            
            max_retries = 4
            for attempt in range(max_retries):
                try:
                    compliance_result = compliance_crew.kickoff()
                    break
                except Exception as e:
                    if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                        print("⚠️ Rate limit hit on compliance! Switching to next Groq API key...")
                        get_groq_api_key()
                        self.compliance = create_compliance_agent()
                        compliance_crew = Crew(
                            agents=[self.compliance],
                            tasks=[compliance_task],
                            verbose=False
                        )
                    else:
                        raise e
            print("✅ Compliance check complete!\n")
            
            # Parse compliance
            compliance_status = self._parse_compliance(str(compliance_result))
            iteration_data["agents"].append({
                "name": "Compliance",
                "status": compliance_status["status"],
                "score": compliance_status["score"],
                "output": str(compliance_result)[:200] + "..."
            })
            
            # STEP 5: Brand Guardian (AI Embeddings)
            print("🛡️ STEP 5: Brand Guardian Agent (Semantic Alignment)")
            print("-" * 70)
            
            brand_task = Task(
                description=f"""{brief.to_context_string()}

CONTENT TO ANALYZE:
{content}

YOUR TASK:
Use semantic embedding similarity (MiniLM-L6-v2) to measure brand alignment.

BRAND VOICE ATTRIBUTES TO CHECK:
{chr(10).join(f"• {attr}" for attr in brief.brand.voice_attributes)}

BRAND VALUES:
{chr(10).join(f"• {val}" for val in brief.brand.values)}

REQUIRED OUTPUT FORMAT:
Brand Score: XXX/100
Alignment Level: [STRONG / MODERATE / WEAK]

SEMANTIC ANALYSIS:
• Voice Match: [Analysis of tone/voice alignment]
• Values Alignment: [How well values are embodied]
• Consistency: [Brand identity consistency]

EMBEDDING SIMILARITY SCORES:
• [Attribute 1]: XX% match
• [Attribute 2]: XX% match

RECOMMENDATIONS:
• [How to improve brand alignment if needed]

APPROVAL: [APPROVED if score ≥70, otherwise NEEDS REVISION]

Use your check_brand_alignment tool to calculate semantic similarity between the content and brand attributes.""",
                
                expected_output="Brand alignment analysis with semantic similarity scores",
                agent=self.brand_guardian
            )
            
            brand_crew = Crew(
                agents=[self.brand_guardian],
                tasks=[brand_task],
                verbose=False
            )
            
            brand_result = brand_crew.kickoff()
            print("✅ Brand check complete!\n")
            
            # Parse brand score
            brand_score = self._parse_brand_score(str(brand_result))
            iteration_data["agents"].append({
                "name": "Brand Guardian",
                "score": brand_score,
                "output": str(brand_result)[:200] + "..."
            })
            
            # Collect feedback for next iteration
            current_feedback = []
            if review_scores.get('overall', 0) < 7.5:
                current_feedback.append(f"• Reviewer: Quality too low ({review_scores.get('overall', 0)}/10) - improve clarity and engagement")
            if compliance_status['score'] < 90:
                current_feedback.append(f"• Compliance: Issues detected (score {compliance_status['score']}/100) - review legal/ethical concerns")
            if brand_score < 70:
                current_feedback.append(f"• Brand Guardian: Weak alignment ({brand_score}/100) - strengthen brand voice")
            
            if current_feedback:
                feedback_history.append(current_feedback)
            
            # DECISION: Check if approved
            print(f"\n{'='*70}")
            print("📋 ITERATION SUMMARY")
            print(f"{'='*70}")
            print(f"Quality Score: {review_scores.get('overall', 0)}/10")
            print(f"Compliance Score: {compliance_status['score']}/100")
            print(f"Brand Alignment: {brand_score}/100")
            
            # Approval thresholds
            quality_ok = review_scores.get('overall', 0) >= 7.5
            compliance_ok = compliance_status['score'] >= 90
            brand_ok = brand_score >= 70
            
            approved = quality_ok and compliance_ok and brand_ok
            
            if approved:
                print("\n✅ ALL CHECKS PASSED! Campaign approved!")
            else:
                print("\n⚠️ Some checks failed:")
                if not quality_ok:
                    print(f"   - Quality score too low ({review_scores.get('overall', 0)}/10, need >= 7.5)")
                if not compliance_ok:
                    print(f"   - Compliance issues detected ({compliance_status['score']}/100, need >= 90)")
                if not brand_ok:
                    print(f"   - Brand alignment weak ({brand_score}/100, need >= 70)")
                
                if self.current_iteration < self.max_iterations:
                    print(f"\n🔄 Starting iteration {self.current_iteration + 1}...")
                else:
                    print("\n⚠️ Max iterations reached. Using best available version.")
            
            # Store iteration data
            iteration_data["scores"] = {
                "quality": review_scores.get('overall', 0),
                "compliance": compliance_status['score'],
                "brand": brand_score
            }
            iteration_data["approved"] = approved
            self.campaign_metadata["iterations"].append(iteration_data)
        
        # Final output
        self.campaign_metadata["end_time"] = datetime.now().isoformat()
        self.campaign_metadata["final_iteration"] = self.current_iteration
        self.campaign_metadata["approved"] = approved
        
        result = {
            "content": str(content),
            "image_path": image_path,
            "scores": {
                "quality": review_scores.get('overall', 0),
                "compliance": compliance_status['score'],
                "brand": brand_score
            },
            "approved": approved,
            "iterations": self.current_iteration,
            "metadata": self.campaign_metadata
        }
        
        # Save to outputs folder
        self._save_campaign(result, brief.brand.name)
        
        print(f"\n{'='*70}")
        print("🎉 CAMPAIGN GENERATION COMPLETE!")
        print(f"{'='*70}\n")
        
        return result
    
    def _parse_review_scores(self, review_text: str) -> dict:
        """Extract scores from reviewer output"""
        import re
        scores = {"quality": 0, "readability": 0, "engagement": 0, "overall": 0}
        
        # Try to extract scores
        quality_match = re.search(r'Quality:\s*(\d+(?:\.\d+)?)', review_text, re.IGNORECASE)
        readability_match = re.search(r'Readability:\s*(\d+(?:\.\d+)?)', review_text, re.IGNORECASE)
        engagement_match = re.search(r'Engagement:\s*(\d+(?:\.\d+)?)', review_text, re.IGNORECASE)
        overall_match = re.search(r'Overall:\s*(\d+(?:\.\d+)?)', review_text, re.IGNORECASE)
        
        if quality_match:
            scores["quality"] = float(quality_match.group(1))
        if readability_match:
            scores["readability"] = float(readability_match.group(1))
        if engagement_match:
            scores["engagement"] = float(engagement_match.group(1))
        if overall_match:
            scores["overall"] = float(overall_match.group(1))
        
        # Calculate overall if not found
        if scores["overall"] == 0 and any([scores["quality"], scores["readability"], scores["engagement"]]):
            scores["overall"] = (scores["quality"] + scores["readability"] + scores["engagement"]) / 3
        
        return scores
    
    def _parse_compliance(self, compliance_text: str) -> dict:
        """Extract compliance status and score"""
        import re
        result = {"status": "APPROVED", "score": 100}
        
        # Check for status
        if "REJECTED" in compliance_text.upper():
            result["status"] = "REJECTED"
        elif "NEEDS REVIEW" in compliance_text.upper():
            result["status"] = "NEEDS REVIEW"
        
        # Try to extract score
        score_match = re.search(r'Compliance Score:\s*(\d+)', compliance_text, re.IGNORECASE)
        if score_match:
            result["score"] = int(score_match.group(1))
        elif result["status"] == "REJECTED":
            result["score"] = 60
        elif result["status"] == "NEEDS REVIEW":
            result["score"] = 80
        
        return result
    
    def _parse_brand_score(self, brand_text: str) -> int:
        """Extract brand alignment score"""
        import re
        score_match = re.search(r'Brand Score:\s*(\d+)', brand_text, re.IGNORECASE)
        if score_match:
            return int(score_match.group(1))
        return 50  # Default if not found
    
    def _save_campaign(self, result: dict, brand_name: str):
        """Save campaign outputs to folder"""
        # Create outputs directory
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Create campaign folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_brand = "".join(c for c in brand_name if c.isalnum() or c in (' ', '-', '_')).strip()
        campaign_dir = output_dir / f"{safe_brand}_{timestamp}"
        campaign_dir.mkdir(exist_ok=True)
        
        # Save content
        (campaign_dir / "content.txt").write_text(result["content"], encoding="utf-8")
        
        # Save metadata
        (campaign_dir / "metadata.json").write_text(
            json.dumps(result["metadata"], indent=2),
            encoding="utf-8"
        )
        
        # Save report
        report = f"""
CREATIVE MEDIA CO-PILOT - CAMPAIGN REPORT
{'='*70}

Campaign Generated: {result['metadata']['start_time']}
Brand: {brand_name}
Iterations: {result['iterations']}/{self.max_iterations}
Status: {'✅ APPROVED' if result['approved'] else '⚠️ NEEDS REVIEW'}

FINAL SCORES:
{'='*70}
Quality Score: {result['scores']['quality']}/10
Compliance Score: {result['scores']['compliance']}/100
Brand Alignment: {result['scores']['brand']}/100

AGENTS USED:
{'='*70}
✓ Content Writer (Llama 3.1 via Groq)
✓ Designer (FLUX.1 via HuggingFace)
✓ Reviewer (Llama 3.1 via Groq)
✓ Compliance Officer (Llama 3.1 via Groq)
✓ Brand Guardian (MiniLM-L6-v2 Embeddings)

GENERATED CONTENT:
{'='*70}
{result['content']}

IMAGE:
{'='*70}
{result['image_path']}

"""
        (campaign_dir / "report.txt").write_text(report, encoding="utf-8")
        
        print(f"💾 Campaign saved to: {campaign_dir}")


# Test the crew
if __name__ == "__main__":
    """
    Test the full multi-agent workflow with enhanced prompts
    Run with: python src/crew/creative_crew.py
    """
    
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing Enhanced Creative Media Crew...\n")
    
    try:
        # Create the crew
        crew = CreativeMediaCrew(max_iterations=2)  # Limit to 2 for testing
        
        # Create campaign brief using presets
        brief = CampaignBrief(
            brand=BRAND_PRESETS["tech_startup"],
            platform=PLATFORM_PRESETS["instagram"],
            objective="product launch",
            target_audience="tech-savvy millennials aged 25-35 interested in productivity tools",
            key_message="Revolutionary AI-powered productivity that adapts to your workflow",
            call_to_action="Download now and get 30 days free!",
            content_type="promotional",
            product_name="FlowAI",
            special_requirements="Emphasize time-saving benefits and modern design"
        )
        
        # Test campaign
        result = crew.create_campaign(brief)
        
        print("\n" + "="*70)
        print("📊 FINAL RESULT:")
        print("="*70)
        print(f"Brand: {brief.brand.name}")
        print(f"Platform: {brief.platform.name}")
        print(f"Approved: {result['approved']}")
        print(f"Iterations: {result['iterations']}")
        print(f"Quality: {result['scores']['quality']}/10")
        print(f"Compliance: {result['scores']['compliance']}/100")
        print(f"Brand: {result['scores']['brand']}/100")
        print(f"\nContent preview: {result['content'][:150]}...")
        print(f"Image: {result['image_path']}")
        print("="*70)
        
        print("\n✅ Enhanced multi-agent workflow test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
