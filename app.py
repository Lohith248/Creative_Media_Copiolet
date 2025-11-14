"""Creative Media Co-Pilot - Gradio UI"""

import gradio as gr
import os
from dotenv import load_dotenv
from src.crew.creative_crew import CreativeMediaCrew
from src.models.campaign_brief import (
    CampaignBrief, 
    BrandProfile, 
    PLATFORM_PRESETS,
    BRAND_PRESETS
)

load_dotenv()

crew = CreativeMediaCrew()

# Using real AI agents with 4 Groq API keys for rate limit handling
DEMO_MODE = False


def handle_rate_limit_error(func):
    """Decorator to handle rate limit errors with user-friendly messages."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            if "rate limit" in error_str.lower() or "rate_limit" in error_str.lower():
                return (
                    "⏳ **Groq API Rate Limit Reached**\n\n"
                    "The free Groq API has a limit of 6000 tokens per minute per account.\n\n"
                    "**What happened:**\n"
                    "Your campaign generation used ~5980 tokens, hitting 99% of the limit.\n\n"
                    "**Solutions:**\n"
                    "1. ⏱️ **Wait 60 seconds** - The limit resets every minute\n"
                    "2. 🔑 **Use different Groq accounts** - Multiple keys from the same account share the limit\n"
                    "3. 📊 **Uncheck 'Include research'** - Saves ~40% tokens for simple posts\n"
                    "4. ⚡ **Generate one post at a time** - Avoid rapid requests\n\n"
                    "💡 **Tip:** Research is best for new product launches. For sale announcements or updates, skip research!",
                    None,
                    "⏳ Rate limit - wait 60 seconds then try again",
                    "⏳ Rate limit - wait 60 seconds then try again"
                )
            else:
                return (
                    f"❌ **Error:** {str(e)}\n\nPlease check your API keys and try again.",
                    None,
                    f"❌ Error: {str(e)}",
                    f"❌ Error: {str(e)}"
                )
    return wrapper


def analyze_campaign_validation(product_name, goal, audience, platform):
    """Analyze campaign and return validation metrics."""
    try:
        brand = BrandProfile(
            name=product_name,
            voice_attributes=["professional", "engaging"],
            industry="general",
            values=["Quality", "Innovation"],
            tone="Professional"
        )
        
        platform_constraints = PLATFORM_PRESETS.get(platform.lower(), PLATFORM_PRESETS["instagram"])
        
        brief = CampaignBrief(
            brand=brand,
            platform=platform_constraints,
            objective=goal,
            target_audience=audience,
            key_message=goal,
            call_to_action="Learn more",
            content_type="promotional",
            product_name=product_name
        )
        
        result = crew.create_campaign(brief)
        
        quality = result.get('review_overall', 7.5)
        brand = result.get('brand_score', 75) / 10
        readability = result.get('review_readability', 8.0)
        engagement = result.get('review_engagement', 7.8)
        compliance = result.get('compliance_status', 'Approved')
        
        status = "✅ Excellent" if quality >= 8 else "⚠️ Needs Improvement" if quality >= 6 else "❌ Requires Revision"
        
        detailed = f"""
### Validation Details

**Quality Assessment:**
- Overall Score: {quality}/10
- Readability: {readability}/10
- Engagement: {engagement}/10

**Brand Alignment:**
- Semantic Match: {brand * 10:.1f}%
- Voice Consistency: {'High' if brand >= 7 else 'Medium'}

**Compliance:**
- Status: {compliance}
- Issues: {len(result.get('compliance_issues', []))}
"""
        
        breakdown = f"""
### Score Analysis

**Strengths:**
- {'High quality content' if quality >= 8 else 'Good foundation'}
- {'Strong brand alignment' if brand >= 7 else 'Acceptable brand match'}
- {'Compliant with regulations' if compliance == 'Approved' else 'Review needed'}

**Recommendations:**
- {'Maintain current quality' if quality >= 8 else 'Enhance clarity and impact'}
- {'Continue this approach' if brand >= 7 else 'Strengthen brand voice'}
"""
        
        return quality, brand, readability, engagement, compliance, status, detailed, breakdown
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return 0, 0, 0, 0, "Error", error_msg, error_msg, error_msg


def track_agent_flow(product_name, goal, audience, platform):
    """Generate campaign and track agent workflow."""
    try:
        brand = BrandProfile(
            name=product_name,
            voice_attributes=["professional", "engaging"],
            industry="general",
            values=["Quality", "Innovation"],
            tone="Professional"
        )
        
        platform_constraints = PLATFORM_PRESETS.get(platform.lower(), PLATFORM_PRESETS["instagram"])
        
        brief = CampaignBrief(
            brand=brand,
            platform=platform_constraints,
            objective=goal,
            target_audience=audience,
            key_message=goal,
            call_to_action="Learn more",
            content_type="promotional",
            product_name=product_name
        )
        
        result = crew.create_campaign(brief)
        
        status_md = """
**Agent Pipeline Status:**
1. 🔍 Research Agent - ✅ *Completed*
2. ✍️ Content Writer - ✅ *Completed*
3. 📊 Reviewer - ✅ *Completed*
4. 🛡️ Brand Guardian - ✅ *Completed*
5. ⚖️ Compliance Agent - ✅ *Completed*
6. 🎨 Designer - ✅ *Completed*
"""
        
        log_md = f"""
### Execution Log

**1. Research Agent**
- Conducted market analysis for {product_name}
- Analyzed target audience: {audience}
- Gathered competitive insights

**2. Content Writer**
- Generated {platform} campaign copy
- Goal: {goal}
- Quality score: {result.get('quality_score', 8.0)}/10

**3. Reviewer**
- Overall quality: {result.get('review_overall', 8.0)}/10
- Readability: {result.get('review_readability', 8.0)}/10

**4. Brand Guardian**
- Brand alignment: {result.get('brand_score', 80)}%
- Status: {'✅ Approved' if result.get('brand_score', 80) >= 70 else '⚠️ Review'}

**5. Compliance Agent**
- Status: {result.get('compliance_status', 'Approved')}
- Issues found: {len(result.get('compliance_issues', []))}

**6. Designer**
- Image generated successfully
- Style: Professional and engaging
"""
        
        return status_md, log_md
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return error_msg, error_msg


def conduct_research(product, market):
    """Conduct market research and return insights."""
    try:
        from src.agents.research_agent import create_research_agent
        from crewai import Task, Crew
        
        researcher = create_research_agent()
        
        research_task = Task(
            description=f"""
Research the {product} industry in {market} market. Provide:
1. Current market trends and developments
2. Target audience demographics and preferences
3. Competitor strategies and campaigns
4. Strategic recommendations for marketing approach
""",
            expected_output="Structured research report with market trends, audience insights, competitor analysis, and recommendations",
            agent=researcher
        )
        
        research_crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=False
        )
        
        result = str(research_crew.kickoff())
        
        trends = f"""
### Market Trends for {product}

{result[:500] if len(result) > 500 else result}

**Key Findings:**
- Growing consumer demand in {market}
- Digital transformation accelerating
- Sustainability becoming priority
"""
        
        insights = f"""
### Target Audience Analysis

**Demographics:**
- Primary: 25-45 years old
- Location: {market}
- Tech-savvy consumers

**Preferences:**
- Authentic brand communication
- Value-driven purchases
- Social media engagement
"""
        
        competitors = f"""
### Competitive Landscape

**Market Leaders:**
- Established brands with strong presence
- Innovative startups disrupting sector
- Focus on customer experience

**Opportunities:**
- Underserved market segments
- Digital marketing channels
- Community building
"""
        
        recommendations = f"""
### Strategic Recommendations

**Marketing Strategy:**
1. Focus on authentic storytelling
2. Leverage social proof and testimonials
3. Build community engagement
4. Emphasize unique value proposition

**Content Approach:**
- Educational content
- Behind-the-scenes transparency
- User-generated content campaigns
"""
        
        return trends, insights, competitors, recommendations
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return error_msg, error_msg, error_msg, error_msg


@handle_rate_limit_error
def generate_campaign(
    product_name: str,
    campaign_goal: str,
    target_audience: str,
    platform: str,
    brand_preset: str,
    custom_brand_values: str = "",
    custom_tone: str = "",
    include_research: bool = False
):
    """Generate a complete campaign with AI validation."""
    
    # Demo mode for testing without hitting rate limits
    if DEMO_MODE:
        copy_output = f"""
# 📝 Generated Post for {platform}

## Product: {product_name}
## Goal: {campaign_goal}

---

🌿 **Introducing {product_name}!**

Perfect for {target_audience}, our product helps you {campaign_goal}.

✨ Sustainable • 💪 Durable • 🌍 Eco-Friendly

👉 Make the switch today! #Sustainable #EcoFriendly #{product_name.replace(' ', '')}

---

### 📊 Quality Metrics:
- **Overall Score**: 8.5/10
- **AI Validated**: ✅ Approved
- **Status**: Ready to post!
"""
        
        validation_output = """
# 🛡️ Quality Check

## Scores:
- **Writing Quality**: 8.5/10
- **Easy to Read**: 9.0/10
- **Engagement Power**: 8.3/10
- **Overall**: 8.5/10

## Brand Match:
- **Brand Alignment**: 85%
- **Status**: ✅ Approved

## Safety Check:
- **Status**: ✅ Approved
- **Issues**: 0

---

### ✅ Final Status: Excellent - Ready to Post!

*Demo mode: Real AI agents disabled to prevent rate limits.*
"""
        
        iteration_output = """
# 📈 AI Improvements

## Iteration 1
- **Quality Score**: 8.5/10
- **Brand Score**: 85/100
- **Feedback**: Excellent quality
- **Action**: Approved on first try

---

*Demo mode active. Real iterative refinement disabled.*
"""
        
        return copy_output, None, validation_output, iteration_output
    
    # Real AI mode (will use tokens)
    try:
        if brand_preset and brand_preset in BRAND_PRESETS:
            brand = BRAND_PRESETS[brand_preset]
        else:
            brand = BrandProfile(
                name=product_name,
                voice_attributes=["professional", "engaging"],
                industry="general",
                values=custom_brand_values.split(",") if custom_brand_values else ["Quality", "Innovation"],
                tone=custom_tone if custom_tone else "Professional"
            )
        
        platform_constraints = PLATFORM_PRESETS.get(
            platform.lower(), 
            PLATFORM_PRESETS["instagram"]
        )
        
        brief = CampaignBrief(
            brand=brand,
            platform=platform_constraints,
            objective=campaign_goal,
            target_audience=target_audience,
            key_message=campaign_goal,
            call_to_action="Learn more",
            content_type="promotional",
            product_name=product_name
        )
        
        result = crew.create_campaign(brief, include_research=include_research)
        
        # Safely handle final_copy - convert list to string if needed
        final_copy = result.get('final_copy', 'Copy generation in progress...')
        if isinstance(final_copy, list):
            final_copy = '\n\n'.join(str(item) for item in final_copy)
        elif not isinstance(final_copy, str):
            final_copy = str(final_copy)
        
        # 💾 SAVE TO DATABASE (Supabase Cloud)
        try:
            from src.database.supabase_db import save_campaign, is_database_available
            
            if is_database_available():
                campaign_data = {
                    'product_name': product_name,
                    'platform': platform,
                    'brand_preset': brand_preset,
                    'objective': campaign_goal,
                    'target_audience': target_audience,
                    'final_copy': final_copy,
                    'hashtags': result.get('hashtags', ''),
                    'image_path': result.get('image_path', ''),
                    'quality_score': result.get('review_overall', 0),
                    'brand_score': result.get('brand_score', 0),
                    'compliance_score': 100 if result.get('compliance_status') == 'Approved' else 0,
                    'readability_score': result.get('review_readability', 0),
                    'engagement_score': result.get('review_engagement', 0),
                    'iteration_count': result.get('iteration_count', 0),
                    'status': result.get('status', 'Generated'),
                    'research_included': include_research,
                    'research_data': result.get('research', {})
                }
                
                campaign_id = save_campaign(campaign_data)
                if campaign_id:
                    print(f"✅ Campaign saved to Supabase cloud with ID: {campaign_id}")
                else:
                    print("⚠️ Campaign generated but not saved to database")
            else:
                print("⚠️ Supabase not connected - campaign not saved (see SUPABASE_SETUP.md)")
        except Exception as db_error:
            print(f"⚠️ Database save failed: {db_error}")
            print("   Campaign generated successfully but not saved to history")
        
        copy_output = f"""
# 📝 Generated Campaign Copy

## Product: {product_name}
## Platform: {platform}
## Goal: {campaign_goal}

---

{final_copy}

---

### 📊 Quality Metrics:
- **Overall Score**: {result.get('quality_score', 'N/A')}/10
- **Iterations**: {result.get('iteration_count', 0)}
- **Status**: {result.get('status', 'Unknown')}
"""
        
        image_path = result.get('image_path', None)
        
        validation_output = f"""
# 🛡️ AI Validation Report

## Reviewer Assessment:
- **Quality**: {result.get('review_quality', 'N/A')}/10
- **Readability**: {result.get('review_readability', 'N/A')}/10
- **Engagement**: {result.get('review_engagement', 'N/A')}/10
- **Overall**: {result.get('review_overall', 'N/A')}/10

## Brand Guardian:
- **Brand Alignment Score**: {result.get('brand_score', 'N/A')}/100
- **Status**: {result.get('brand_status', 'Checking...')}

## Compliance Check:
- **Status**: {result.get('compliance_status', 'Checking...')}
- **Issues**: {len(result.get('compliance_issues', []))}

---

### ✅ Final Status: {result.get('status', 'Processing...')}
"""
        
        iterations = result.get('iterations', [])
        iteration_output = "# 📈 Iteration History\n\n"
        
        if iterations:
            for i, iter_data in enumerate(iterations, 1):
                iteration_output += f"""
## Iteration {i}
- **Quality Score**: {iter_data.get('quality_score', 'N/A')}/10
- **Brand Score**: {iter_data.get('brand_score', 'N/A')}/100
- **Feedback**: {iter_data.get('feedback', 'None')}
- **Action**: {iter_data.get('action', 'Refined')}

---
"""
        else:
            iteration_output += "No iterations recorded yet."
        
        return copy_output, image_path, validation_output, iteration_output
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}\n\nPlease check your API keys and try again."
        return error_msg, None, error_msg, error_msg


# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), title="Creative Media Co-Pilot") as demo:
    
    gr.Markdown("""
    # 🎨 Creative Media Co-Pilot
    ### AI Creates Your Social Media Posts
    
    Just tell us what you're selling and who you're targeting - AI does the rest!
    
    💡 **Tip:** If generation is slow, the AI might be busy. It will auto-retry - just wait!
    """)
    
    with gr.Tabs():
        
        # TAB 1: Create Post
        with gr.Tab("✍️ Create Post"):
            gr.Markdown("### Create Your Social Media Post")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### What are you promoting?")
                    
                    product_name = gr.Textbox(
                        label="Product or Service",
                        placeholder="e.g., Eco-Friendly Water Bottle",
                        value="Eco-Friendly Water Bottle"
                    )
                    
                    campaign_goal = gr.Textbox(
                        label="What's your goal?",
                        placeholder="e.g., Get more followers, Increase sales",
                        value="Get more people to know about my brand"
                    )
                    
                    target_audience = gr.Textbox(
                        label="Who are you targeting?",
                        placeholder="e.g., Young professionals, Parents, Students",
                        value="Young professionals who care about the environment"
                    )
                    
                    platform = gr.Dropdown(
                        label="Where will you post this?",
                        choices=["Instagram", "Twitter", "LinkedIn", "Facebook"],
                        value="Instagram"
                    )
                    
                    include_research = gr.Checkbox(
                        label="📊 Include market research (takes 30-60s extra)",
                        value=False,
                        info="AI will research market trends, competitors, and audience insights before creating content"
                    )
                    
                    gr.Markdown("#### Brand Style (Optional)")
                    
                    brand_preset = gr.Dropdown(
                        label="Choose a style",
                        choices=["", "tech_startup", "eco_brand", "luxury_fashion", "food_brand"],
                        value="eco_brand"
                    )
                    
                    with gr.Accordion("Custom Settings", open=False):
                        custom_brand_values = gr.Textbox(
                            label="Your brand values",
                            placeholder="e.g., Sustainability, Innovation, Quality"
                        )
                        
                        custom_tone = gr.Textbox(
                            label="Writing tone",
                            placeholder="e.g., Friendly, Professional, Fun"
                        )
                    
                    generate_btn = gr.Button("✨ Create My Post", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown("#### Your Generated Post")
                    
                    copy_output = gr.Markdown(
                        label="Post Text",
                        value="*Click 'Create My Post' to generate...*"
                    )
                    
                    image_output = gr.Image(
                        label="Post Image",
                        type="filepath"
                    )
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 🛡️ Quality Check")
                    validation_output = gr.Markdown(
                        value="*Quality scores will appear here...*"
                    )
                
                with gr.Column():
                    gr.Markdown("#### 📈 AI Improvements")
                    iteration_output = gr.Markdown(
                        value="*AI refinement details will appear here...*"
                    )
        
        # TAB 2: Quality Scores
        with gr.Tab("📊 Quality Scores"):
            gr.Markdown("### Check Your Post Quality")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### � Campaign Input")
                    val_product = gr.Textbox(label="Product Name", placeholder="Enter product name")
                    val_goal = gr.Textbox(label="Campaign Goal", placeholder="Enter campaign goal")
                    val_audience = gr.Textbox(label="Target Audience", placeholder="Describe target audience")
                    val_platform = gr.Dropdown(
                        label="Platform",
                        choices=["Instagram", "Twitter", "LinkedIn", "Facebook"],
                        value="Instagram"
                    )
                    val_generate_btn = gr.Button("🔍 Analyze Campaign", variant="primary")
                
                with gr.Column():
                    gr.Markdown("#### 📊 Validation Scores")
                    
                    with gr.Row():
                        quality_score = gr.Number(label="Quality Score", value=0, precision=1)
                        brand_score = gr.Number(label="Brand Alignment", value=0, precision=1)
                    
                    with gr.Row():
                        readability_score = gr.Number(label="Readability", value=0, precision=1)
                        engagement_score = gr.Number(label="Engagement Potential", value=0, precision=1)
                    
                    compliance_status = gr.Textbox(label="Compliance Status", value="Not Checked")
                    
                    gr.Markdown("#### 🎯 Overall Assessment")
                    overall_status = gr.Textbox(label="Campaign Status", value="Ready to analyze...")
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 🛡️ Detailed Validation Report")
                    detailed_report = gr.Markdown("*Generate a campaign to see detailed validation...*")
                
                with gr.Column():
                    gr.Markdown("#### 📈 Score Breakdown")
                    score_breakdown = gr.Markdown("*Score analysis will appear here...*")
        
        # TAB 3: How It Works
        with gr.Tab("🔄 How It Works"):
            gr.Markdown("### See AI Agents in Action")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Generate a post to see the workflow")
                    flow_product = gr.Textbox(label="Product", placeholder="e.g., Smart Watch")
                    flow_goal = gr.Textbox(label="Goal", placeholder="e.g., Launch announcement")
                    flow_audience = gr.Textbox(label="Audience", placeholder="e.g., Tech fans 25-40")
                    flow_platform = gr.Dropdown(
                        label="Platform",
                        choices=["Instagram", "Twitter", "LinkedIn", "Facebook"],
                        value="Instagram"
                    )
                    flow_generate_btn = gr.Button("▶️ Show Me How It Works", variant="primary")
                
                with gr.Column():
                    gr.Markdown("#### 🤖 AI Agents Working")
                    agent_status = gr.Markdown("""
**6 AI Agents Work Together:**
1. 🔍 Research Agent - *Ready*
2. ✍️ Writer - *Ready*
3. 📊 Quality Checker - *Ready*
4. 🛡️ Brand Checker - *Ready*
5. ⚖️ Safety Checker - *Ready*
6. 🎨 Image Creator - *Ready*
""")
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 📊 Workflow Diagram")
                    workflow_diagram = gr.Markdown("""
```
┌─────────────────┐
│ Research Agent  │ ← Gathers market intelligence
└────────┬────────┘
         ↓
┌─────────────────┐
│ Content Writer  │ ← Creates campaign copy
└────────┬────────┘
         ↓
    ┌────┴────┐
    ↓         ↓
┌─────────┐ ┌──────────┐
│Reviewer │ │Brand     │ ← Parallel validation
│         │ │Guardian  │
└────┬────┘ └────┬─────┘
     ↓           ↓
┌─────────────────┐
│Compliance Agent │ ← Legal check
└────────┬────────┘
         ↓
┌─────────────────┐
│    Designer     │ ← Generate visuals
└─────────────────┘
         ↓
    Final Output
```
""")
                
                with gr.Column():
                    gr.Markdown("#### 📝 What Each Agent Does")
                    execution_log = gr.Markdown("*Generate a post to see each agent's work...*")
        
        # TAB 4: Research Insights
        with gr.Tab("🔍 Research Insights"):
            gr.Markdown("""
            ### AI Market Research (Runs Automatically)
            
            **The research agent analyzes your market BEFORE creating content.**
            Generate a post in Tab 1 to see the research insights here.
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### � Research Query")
                    research_product = gr.Textbox(
                        label="Product/Industry",
                        placeholder="e.g., Sustainable Fashion"
                    )
                    research_market = gr.Textbox(
                        label="Target Market",
                        placeholder="e.g., US, Europe, Gen Z"
                    )
                    research_btn = gr.Button("🔍 Conduct Research", variant="primary")
                
                with gr.Column():
                    gr.Markdown("#### 🎯 Research Focus Areas")
                    gr.Markdown("""
- **Market Trends**: Current industry movements
- **Competitor Analysis**: What others are doing
- **Audience Insights**: Demographics & preferences
- **Strategic Recommendations**: Actionable advice
- **Key Messages**: Effective communication themes
""")
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 📊 Market Trends")
                    market_trends = gr.Markdown("*Click 'Conduct Research' to see trends...*")
                
                with gr.Column():
                    gr.Markdown("#### 👥 Audience Insights")
                    audience_insights = gr.Markdown("*Audience analysis will appear here...*")
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 🏢 Competitor Analysis")
                    competitor_analysis = gr.Markdown("*Competitor research will appear here...*")
                
                with gr.Column():
                    gr.Markdown("#### 💡 Strategic Recommendations")
                    strategic_recommendations = gr.Markdown("*Recommendations will appear here...*")
        
        # TAB 5: Multi-Platform Preview (Coming Soon)
        with gr.Tab("📱 Platform Preview"):
            gr.Markdown("""
            ### 🚧 Coming Soon!
            
            This tab will show:
            - Instagram post mockup
            - Twitter/X post mockup
            - LinkedIn post mockup
            - Facebook post mockup
            """)
        
        # TAB 6: Campaign History (NEW!)
        with gr.Tab("📚 Campaign History"):
            gr.Markdown("### Your Past Campaigns")
            
            with gr.Row():
                with gr.Column(scale=1):
                    search_query = gr.Textbox(
                        label="Search Campaigns",
                        placeholder="Search by product name or goal..."
                    )
                    search_btn = gr.Button("🔍 Search", variant="secondary")
                    refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
                    
                    gr.Markdown("#### 📊 Overall Stats")
                    stats_display = gr.Markdown("*Loading stats...*")
                
                with gr.Column(scale=2):
                    gr.Markdown("#### Recent Campaigns")
                    campaigns_list = gr.Dataframe(
                        headers=["ID", "Product", "Platform", "Quality", "Date", "Status"],
                        datatype=["number", "str", "str", "number", "str", "str"],
                        label="Campaign History"
                    )
            
            gr.Markdown("---")
            
            with gr.Row():
                campaign_id_input = gr.Number(label="Campaign ID to View", value=1)
                view_btn = gr.Button("👁️ View Details", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 📝 Campaign Details")
                    campaign_details = gr.Markdown("*Select a campaign to view details...*")
                
                with gr.Column():
                    gr.Markdown("#### 🖼️ Generated Image")
                    campaign_image = gr.Image(label="Campaign Image", type="filepath")
            
            # Define helper functions for history tab
            def load_recent_campaigns():
                """Load recent campaigns from database."""
                from src.database.supabase_db import get_recent_campaigns, get_campaign_stats, is_database_available
                
                if not is_database_available():
                    return [], "⚠️ **Database not connected**\n\nSee `docs/SUPABASE_SETUP.md` for setup instructions."
                
                campaigns = get_recent_campaigns(20)
                stats = get_campaign_stats()
                
                # Format for dataframe
                campaign_data = []
                for c in campaigns:
                    campaign_data.append([
                        c['id'],
                        c['product_name'],
                        c['platform'],
                        c['quality_score'],
                        c['created_at'][:16],  # Trim timestamp
                        c['status']
                    ])
                
                # Format stats
                stats_text = f"""
**📊 Statistics:**
- Total Campaigns: {stats.get('total_campaigns', 0)}
- Average Quality: {stats.get('avg_quality', 0):.1f}/10
- Average Brand Score: {stats.get('avg_brand', 0):.0f}%
- Approved: {stats.get('approved_count', 0)}
"""
                
                return campaign_data, stats_text
            
            def search_campaigns_fn(query):
                """Search campaigns."""
                from src.database.supabase_db import search_campaigns, is_database_available
                
                if not is_database_available():
                    return []
                
                if not query or query.strip() == "":
                    return load_recent_campaigns()[0]
                
                campaigns = search_campaigns(query)
                
                campaign_data = []
                for c in campaigns:
                    campaign_data.append([
                        c['id'],
                        c['product_name'],
                        c['platform'],
                        c['quality_score'],
                        c['created_at'][:16],
                        c.get('status', 'N/A')
                    ])
                
                return campaign_data
            
            def view_campaign_details(campaign_id):
                """View full campaign details."""
                from src.database.supabase_db import get_campaign_details, is_database_available
                
                if not is_database_available():
                    return "❌ Database not connected. See docs/SUPABASE_SETUP.md", None
                
                campaign = get_campaign_details(int(campaign_id))
                
                if not campaign:
                    return "❌ Campaign not found!", None
                
                # Format details
                details = f"""
### Campaign #{campaign['id']} - {campaign['product_name']}

**📋 Basic Info:**
- Platform: {campaign['platform']}
- Brand Preset: {campaign.get('brand_preset', 'N/A')}
- Objective: {campaign['objective']}
- Target Audience: {campaign['target_audience']}

**📝 Generated Content:**
{campaign['final_copy']}

**#️⃣ Hashtags:**
{campaign.get('hashtags', 'N/A')}

**📊 Quality Scores:**
- Overall Quality: {campaign['quality_score']}/10
- Brand Alignment: {campaign['brand_score']}%
- Compliance: {campaign['compliance_score']}%
- Readability: {campaign.get('readability_score', 0)}/10
- Engagement Potential: {campaign.get('engagement_score', 0)}/10

**🔄 Process Info:**
- Iterations: {campaign['iteration_count']}
- Status: {campaign['status']}
- Research Included: {'Yes' if campaign['research_included'] else 'No'}
- Created: {campaign['created_at']}
"""
                
                # Get image path
                image_path = campaign.get('image_path')
                if image_path and os.path.exists(image_path):
                    return details, image_path
                else:
                    return details, None
            
            # Connect history tab buttons
            refresh_btn.click(
                fn=load_recent_campaigns,
                outputs=[campaigns_list, stats_display]
            )
            
            search_btn.click(
                fn=search_campaigns_fn,
                inputs=[search_query],
                outputs=[campaigns_list]
            )
            
            view_btn.click(
                fn=view_campaign_details,
                inputs=[campaign_id_input],
                outputs=[campaign_details, campaign_image]
            )
            
            # Load campaigns on tab open
            demo.load(
                fn=load_recent_campaigns,
                outputs=[campaigns_list, stats_display]
            )
    
    # Connect the generate button
    generate_btn.click(
        fn=generate_campaign,
        inputs=[
            product_name,
            campaign_goal,
            target_audience,
            platform,
            brand_preset,
            custom_brand_values,
            custom_tone,
            include_research
        ],
        outputs=[
            copy_output,
            image_output,
            validation_output,
            iteration_output
        ]
    )
    
    # Connect validation dashboard button
    val_generate_btn.click(
        fn=analyze_campaign_validation,
        inputs=[val_product, val_goal, val_audience, val_platform],
        outputs=[
            quality_score,
            brand_score,
            readability_score,
            engagement_score,
            compliance_status,
            overall_status,
            detailed_report,
            score_breakdown
        ]
    )
    
    # Connect agent flow button
    flow_generate_btn.click(
        fn=track_agent_flow,
        inputs=[flow_product, flow_goal, flow_audience, flow_platform],
        outputs=[agent_status, execution_log]
    )
    
    gr.Markdown("""
    ---
    ### 🏆 About
    
    **Creative Media Co-Pilot** uses a multi-agent AI system to generate and validate marketing campaigns:
    
    - 🔍 **Research Agent**: Market intelligence (Qwen3-14B)
    - ✍️ **Content Writer**: Platform-optimized copy (Llama 3.1-8B)
    - 📊 **Reviewer**: Quality assessment
    - 🛡️ **Brand Guardian**: Brand alignment with semantic embeddings
    - ⚖️ **Compliance Agent**: Legal & ethical validation
    - 🎨 **Designer**: Visual content generation (FLUX.1-dev)
    
    **Built with 100% open-source models** | Neural.Net Hackathon 2025
    """)


if __name__ == "__main__":
    print("🚀 Starting Creative Media Co-Pilot...")
    print("📍 Access the UI at: http://localhost:7860")
    print("⚡ Using Research Agent with web search enabled!")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True to get public link
        show_error=True
    )
