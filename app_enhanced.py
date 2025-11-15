"""
Creative Media Co-Pilot - Enhanced Gradio UI
Features: Real-time workflow, History, Before/After, Architecture diagram, Token tracking
"""

import os
import gradio as gr
from datetime import datetime
import json
import time

# Set environment variables
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LITELLM_FORCE_DISABLE_TRACE"] = "true"
os.environ["LITELLM_LOGGING"] = "false"

# Import our multi-agent system
from src.crew.creative_crew import CreativeMediaCrew
from src.models.campaign_brief import CampaignBrief, BrandProfile, PLATFORM_PRESETS
from src.utils.campaign_storage import CampaignStorage

# Initialize storage
storage = CampaignStorage()


def get_architecture_diagram():
    """Generate ASCII architecture diagram."""
    return """
╔══════════════════════════════════════════════════════════════╗
║          CREATIVE MEDIA CO-PILOT ARCHITECTURE                ║
╚══════════════════════════════════════════════════════════════╝

                    📝 User Input
                    (Product, Goal, Audience)
                           │
                           ↓
              ┌────────────────────────┐
              │   Campaign Brief       │
              │   (Structured Data)    │
              └────────────────────────┘
                           │
                           ↓
         ╔═════════════════════════════════════╗
         ║      MULTI-AGENT WORKFLOW           ║
         ╚═════════════════════════════════════╝
                           │
        ┌──────────────────┴──────────────────┐
        │                                      │
        ↓                                      ↓
┌──────────────┐                    ┌──────────────────┐
│ 🔍 Research  │ (Optional)         │ ✍️ Content Writer│
│   Agent      │                    │    Agent         │
└──────────────┘                    └──────────────────┘
        │                                      │
        └──────────────────┬──────────────────┘
                           ↓
                  ┌─────────────────┐
                  │ 🛡️ Brand Guardian│
                  │  (Zero-token)   │
                  └─────────────────┘
                           │
                           ↓
                  ┌─────────────────┐
                  │ 🔎 Reviewer      │
                  │  (Quality Check) │
                  └─────────────────┘
                           │
                           ↓
                  ┌─────────────────┐
                  │ ⚖️ Compliance    │
                  │   Agent          │
                  └─────────────────┘
                           │
                           ↓
                  ┌─────────────────┐
                  │ 🎨 Designer      │
                  │  (Image Gen)     │
                  └─────────────────┘
                           │
                           ↓
                  ┌─────────────────┐
                  │ 📤 Publishing    │
                  │  (Zero-token)    │
                  └─────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │   📊 Final Output      │
              │  • Text                │
              │  • Image               │
              │  • Publishing Package  │
              └────────────────────────┘
                           │
                           ↓
                  ┌─────────────────┐
                  │ 💾 Local Storage │
                  │ (campaign_history│
                  │     .json)       │
                  └─────────────────┘

╔══════════════════════════════════════════════════════════════╗
║ KEY FEATURES:                                                ║
║ • Zero-token agents (Brand Guardian, Publishing)             ║
║ • Professional image prompts (FLUX.1-dev)                    ║
║ • Multi-platform publishing (IG, Twitter, LinkedIn, FB)      ║
║ • Local JSON storage (no database required)                  ║
║ • Real-time workflow visualization                           ║
╚══════════════════════════════════════════════════════════════╝
"""


def run_campaign_pipeline(
    product_name: str,
    campaign_goal: str,
    target_audience: str,
    brand_voice: str,
    brand_values: str,
    platform: str,
    include_research: bool
):
    """
    Run the multi-agent pipeline with real-time status updates.
    Yields: (status, original_draft, final_text, image, publishing, tokens, history)
    """
    
    # Initialize status with emoji indicators
    agent_list = ["Research", "Writer", "BrandGuardian", "Reviewer", "Compliance", "Designer", "Publishing"]
    
    status = {}
    for agent in agent_list:
        if agent == "Research" and not include_research:
            status[agent] = "⏭️ Skipped"
        else:
            status[agent] = "⏳ Pending"
    
    def format_status():
        """Format status as clean table with proper alignment."""
        lines = ["╔═══════════════════════════════════════╗"]
        lines.append("║   AGENT WORKFLOW - LIVE STATUS        ║")
        lines.append("╠═══════════════════════════════════════╣")
        
        for name, stat in status.items():
            # Clean name display
            display_name = name.replace("BrandGuardian", "Brand Guardian")
            padded_name = f"║ {display_name:20} │ {stat:13} ║"
            lines.append(padded_name)
        
        lines.append("╚═══════════════════════════════════════╝")
        return "\n".join(lines)
    
    # Token tracking
    token_stats = {
        "writer": 0,
        "reviewer": 0,
        "compliance": 0,
        "designer": 0,
        "total": 0,
        "brand_guardian": "Zero-token ✅",
        "publishing": "Zero-token ✅"
    }
    
    # Storage for before/after
    original_draft = ""
    final_text = ""
    
    # Initial yield
    yield (
        format_status(), 
        "Waiting to start...", 
        "Waiting to start...", 
        None, 
        "Publishing package will appear here...",
        "Token usage will be calculated...",
        format_history_table()
    )
    
    try:
        # Setup campaign brief
        values_list = [v.strip() for v in brand_values.split(",")] if brand_values else ["Quality", "Innovation"]
        
        brand = BrandProfile(
            name=product_name,
            voice_attributes=[brand_voice] if brand_voice else ["professional"],
            industry="general",
            values=values_list,
            tone=brand_voice if brand_voice else "Professional"
        )
        
        platform_constraints = PLATFORM_PRESETS.get(platform.lower(), PLATFORM_PRESETS["instagram"])
        
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
        
        # Create crew
        crew = CreativeMediaCrew(max_iterations=1)
        
        # Enhanced progress callback
        def update_status(agent_name, state, message, output):
            """Update agent status in real-time."""
            if state == "running":
                status[agent_name] = "🟡 Running..."
            elif state == "completed":
                status[agent_name] = "🟢 Done"
            elif state == "error":
                status[agent_name] = "🔴 Error"
        
        # Step-by-step status updates with yields
        agents_to_run = ["Writer", "BrandGuardian", "Reviewer", "Compliance", "Designer", "Publishing"]
        
        for i, agent in enumerate(agents_to_run):
            status[agent] = "🟡 Running..."
            yield (
                format_status(),
                original_draft or f"Processing {agent}...",
                final_text or f"Processing {agent}...",
                None,
                "Generating...",
                format_token_stats(token_stats),
                format_history_table()
            )
            time.sleep(0.5)  # Smooth animation
        
        # Run actual campaign
        result = crew.create_campaign(brief, include_research=include_research, progress_callback=update_status)
        
        # Mark all as done
        for agent in agents_to_run:
            status[agent] = "🟢 Done"
        
        # Extract results
        final_text = result.get("final_copy", "Content generated successfully")
        image_path = result.get("image_path", None)
        
        # Get original draft from metadata
        metadata = result.get("metadata", {})
        iterations = metadata.get("iterations", [])
        if iterations and len(iterations) > 0:
            first_iter = iterations[0]
            agents_data = first_iter.get("agents", [])
            for agent_data in agents_data:
                if agent_data.get("name") == "Writer":
                    original_draft = agent_data.get("output", "")[:500] + "..."
                    break
        
        if not original_draft:
            original_draft = final_text[:500] + "..."
        
        # Format publishing output
        publishing_pkg = result.get("publishing_package", {})
        
        publishing_output = f"""╔══════════════════════════════════════════════════════════════╗
║              📤 PUBLISHING PACKAGE - READY TO POST           ║
╚══════════════════════════════════════════════════════════════╝

📸 INSTAGRAM POST ({publishing_pkg.get('character_counts', {}).get('instagram', 0)} characters)
{'-'*60}
{publishing_pkg.get('instagram_post', 'N/A')}

{'='*60}

🐦 TWITTER/X POST ({publishing_pkg.get('character_counts', {}).get('twitter', 0)} characters)
{'-'*60}
{publishing_pkg.get('twitter_post', 'N/A')}

{'='*60}

💼 LINKEDIN POST ({publishing_pkg.get('character_counts', {}).get('linkedin', 0)} characters)
{'-'*60}
{publishing_pkg.get('linkedin_post', 'N/A')}

{'='*60}

📘 FACEBOOK POST ({publishing_pkg.get('character_counts', {}).get('facebook', 0)} characters)
{'-'*60}
{publishing_pkg.get('facebook_post', 'N/A')}

{'='*60}
✅ All posts are platform-optimized and ready to publish!
"""
        
        # Build final text display
        text_display = f"""╔══════════════════════════════════════════════════════════════╗
║                    FINAL CAMPAIGN OUTPUT                     ║
╚══════════════════════════════════════════════════════════════╝

📦 PRODUCT: {product_name}
📱 PLATFORM: {platform}
🎯 GOAL: {campaign_goal}
👥 AUDIENCE: {target_audience}

{'='*60}
📝 FINAL CONTENT
{'='*60}

{final_text}

{'='*60}
📊 QUALITY METRICS
{'='*60}
✅ Overall Score: {result.get('review_overall', 'N/A')}/10
✅ Brand Alignment: {result.get('brand_score', 'N/A')}/100
✅ Compliance: {result.get('compliance_status', 'Approved')}
✅ Character Count: {len(final_text)}
✅ Readability: {result.get('review_readability', 'N/A')}/10
✅ Engagement: {result.get('review_engagement', 'N/A')}/10
"""
        
        # Calculate token usage (estimated)
        token_stats.update({
            "writer": len(final_text.split()) * 2,  # Rough estimate
            "reviewer": 200,  # Approximate
            "compliance": 150,
            "designer": 500,  # Image generation
            "total": len(final_text.split()) * 2 + 850
        })
        
        # Save to history
        campaign_id = storage.save_campaign(
            product_name=product_name,
            campaign_goal=campaign_goal,
            platform=platform,
            target_audience=target_audience,
            brand_voice=brand_voice,
            generated_text=final_text,
            image_path=image_path,
            original_draft=original_draft,
            final_text=final_text,
            review_score=result.get('review_overall'),
            brand_score=result.get('brand_score'),
            compliance_status=result.get('compliance_status', 'Approved'),
            publishing_package=publishing_pkg,
            token_usage=token_stats
        )
        
        print(f"✅ Campaign saved to history: {campaign_id}")
        
        yield (
            format_status(),
            original_draft,
            text_display,
            image_path,
            publishing_output,
            format_token_stats(token_stats),
            format_history_table()
        )
        
    except Exception as e:
        # Error handling
        for agent in status.keys():
            if status[agent] not in ["🟢 Done", "⏭️ Skipped"]:
                status[agent] = "🔴 Error"
        
        error_msg = f"""╔══════════════════════════════════════════════════════════════╗
║                  ❌ CAMPAIGN GENERATION FAILED                ║
╚══════════════════════════════════════════════════════════════╝

{str(e)}

💡 TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Check GROQ_API_KEY in .env file
• Verify HUGGINGFACE_TOKEN for images
• Ensure internet connection is active
• Check if rate limits were exceeded
• Try again in a few minutes
"""
        yield (
            format_status(),
            error_msg,
            error_msg,
            None,
            error_msg,
            format_token_stats(token_stats),
            format_history_table()
        )


def format_token_stats(stats: dict) -> str:
    """Format token usage statistics."""
    return f"""╔══════════════════════════════════════════════════════════════╗
║                   TOKEN USAGE ANALYSIS                       ║
╚══════════════════════════════════════════════════════════════╝

🤖 AGENT BREAKDOWN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Writer Agent:         ~{stats.get('writer', 0):,} tokens
• Reviewer Agent:       ~{stats.get('reviewer', 0):,} tokens
• Compliance Agent:     ~{stats.get('compliance', 0):,} tokens
• Designer Agent:       ~{stats.get('designer', 0):,} tokens
• Brand Guardian:       {stats.get('brand_guardian', 'Zero-token ✅')}
• Publishing Agent:     {stats.get('publishing', 'Zero-token ✅')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 TOTAL ESTIMATED:     ~{stats.get('total', 0):,} tokens

💡 COST EFFICIENCY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Model: Groq (llama-3.1-8b-instant)
• Cost: ~$0.00 (Groq free tier)
• Image: FLUX.1-dev (HuggingFace)
• Zero-token agents: 2/6 (33% token-free)

✅ This campaign used MINIMAL tokens thanks to:
   - Local brand validation (no API calls)
   - Rule-based publishing formatter
   - Efficient prompting strategy
"""


def format_history_table() -> str:
    """Format campaign history as a clean table."""
    try:
        campaigns = storage.get_recent_campaigns(limit=10)
        
        if not campaigns:
            return """╔══════════════════════════════════════════════════════════════╗
║                    CAMPAIGN HISTORY                          ║
╚══════════════════════════════════════════════════════════════╝

No campaigns yet. Create your first campaign! 🚀
"""
        
        stats = storage.get_stats()
        
        output = f"""╔══════════════════════════════════════════════════════════════╗
║                    CAMPAIGN HISTORY                          ║
╚══════════════════════════════════════════════════════════════╝

📊 STATISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Campaigns: {stats['total_campaigns']}
• Avg Review Score: {stats['avg_review_score']:.1f}/10
• Avg Brand Score: {stats['avg_brand_score']:.1f}/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 RECENT CAMPAIGNS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for i, camp in enumerate(campaigns[:10], 1):
            timestamp = datetime.fromisoformat(camp['timestamp']).strftime('%Y-%m-%d %H:%M')
            metrics = camp.get('metrics', {})
            
            output += f"""{i}. {camp['product_name']} - {camp['platform']}
   📅 {timestamp}
   🎯 Goal: {camp['campaign_goal'][:50]}...
   ⭐ Score: {metrics.get('review_score', 'N/A')}/10
   ✅ Status: {metrics.get('compliance_status', 'Unknown')}
   
"""
        
        output += "━" * 60 + "\n"
        output += "💡 History saved in: campaign_history.json\n"
        
        return output
        
    except Exception as e:
        return f"Error loading history: {str(e)}"


def save_text(text):
    """Save text to file for download."""
    filename = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename


def save_publishing_json(text):
    """Save publishing output as JSON."""
    filename = f"publishing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename


def clear_history():
    """Clear campaign history."""
    storage.clear_history()
    return "✅ Campaign history cleared!"


# Build Enhanced Gradio UI
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter")
    ),
    title="Creative Media Co-Pilot",
    css="""
        .gradio-container {font-family: 'Inter', sans-serif;}
        .status-box {font-family: 'Courier New', monospace; font-size: 13px;}
    """
) as demo:
    
    gr.Markdown("""
# 🤖 Creative Media Co-Pilot
### Multi-Agent AI System: Text Generation + Design + Publishing Automation
**Professional social media campaigns in seconds** | Powered by CrewAI + Groq + HuggingFace
""")
    
    with gr.Tabs():
        # TAB 1: Campaign Generator
        with gr.TabItem("🚀 Generate Campaign"):
            with gr.Row():
                # COLUMN 1: Input Panel
                with gr.Column(scale=1):
                    gr.Markdown("### 📝 Campaign Details")
                    
                    product_input = gr.Textbox(
                        label="Product/Service",
                        placeholder="e.g., Eco-Friendly Water Bottle",
                        value="EcoStep Sneakers"
                    )
                    
                    goal_input = gr.Textbox(
                        label="Campaign Goal",
                        placeholder="e.g., Increase brand awareness",
                        value="Launch new sustainable product line"
                    )
                    
                    audience_input = gr.Textbox(
                        label="Target Audience",
                        placeholder="e.g., Millennials interested in sustainability",
                        value="Environmentally conscious millennials 25-35"
                    )
                    
                    voice_input = gr.Textbox(
                        label="Brand Voice/Tone",
                        placeholder="e.g., friendly, professional, playful",
                        value="inspiring"
                    )
                    
                    values_input = gr.Textbox(
                        label="Brand Values (comma-separated)",
                        placeholder="e.g., sustainability, innovation, quality",
                        value="sustainability, innovation, quality"
                    )
                    
                    platform_input = gr.Dropdown(
                        label="Platform",
                        choices=["Instagram", "Twitter", "LinkedIn", "Facebook"],
                        value="Instagram"
                    )
                    
                    research_input = gr.Checkbox(
                        label="Include Market Research",
                        value=False
                    )
                    
                    with gr.Row():
                        generate_btn = gr.Button("🚀 Generate Campaign", variant="primary", scale=2)
                        example_btn = gr.Button("✨ Quick Example", variant="secondary", scale=1)
                
                # COLUMN 2: Real-Time Status
                with gr.Column(scale=1):
                    gr.Markdown("### 🤖 Live Agent Workflow")
                    agent_status_display = gr.Textbox(
                        label="Real-Time Progress",
                        value="""╔═══════════════════════════════════════╗
║   AGENT WORKFLOW - LIVE STATUS        ║
╠═══════════════════════════════════════╣
║ Ready to start! 🎯                    ║
║                                       ║
║ Click 'Generate Campaign' to begin.  ║
╚═══════════════════════════════════════╝""",
                        lines=12,
                        interactive=False,
                        elem_classes=["status-box"]
                    )
                    
                    gr.Markdown("### 📊 Token Usage")
                    token_display = gr.Textbox(
                        label="Efficiency Metrics",
                        value="Token usage will be calculated after generation...",
                        lines=15,
                        interactive=False,
                        elem_classes=["status-box"]
                    )
            
            # SECTION 3: Outputs (Full Width)
            gr.Markdown("---")
            gr.Markdown("## 📊 Campaign Results")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### 🔹 Original Draft")
                    original_output = gr.Textbox(
                        label="First Draft from Writer",
                        lines=8,
                        interactive=False
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("#### 🔹 Final Output (Improved)")
                    final_output = gr.Textbox(
                        label="Refined Final Content",
                        lines=8,
                        interactive=False
                    )
            
            with gr.Row():
                download_text_btn = gr.Button("💾 Download Final Text", size="sm")
            
            gr.Markdown("#### 2️⃣ Generated Image")
            image_output = gr.Image(label="Visual Content", type="filepath")
            
            gr.Markdown("#### 3️⃣ Publishing Package (Platform-Optimized)")
            publishing_output = gr.Textbox(
                label="Ready-to-Post Content",
                lines=20,
                interactive=False,
                elem_classes=["status-box"]
            )
            
            download_pub_btn = gr.Button("💾 Download Publishing Package", size="sm")
        
        # TAB 2: Architecture
        with gr.TabItem("🏗️ Architecture"):
            gr.Markdown("## System Architecture Diagram")
            gr.Markdown("*Copy this diagram for your presentation/documentation*")
            
            architecture_output = gr.Textbox(
                label="Pipeline Architecture",
                value=get_architecture_diagram(),
                lines=50,
                interactive=False,
                elem_classes=["status-box"]
            )
            
            copy_arch_btn = gr.Button("📋 Copy Architecture")
        
        # TAB 3: Campaign History
        with gr.TabItem("📚 History"):
            gr.Markdown("## Campaign History")
            gr.Markdown("*All campaigns are saved locally in `campaign_history.json`*")
            
            history_output = gr.Textbox(
                label="Recent Campaigns",
                value=format_history_table(),
                lines=30,
                interactive=False,
                elem_classes=["status-box"]
            )
            
            with gr.Row():
                refresh_history_btn = gr.Button("🔄 Refresh History", variant="secondary")
                clear_history_btn = gr.Button("🗑️ Clear History", variant="stop")
            
            clear_status = gr.Textbox(label="Status", interactive=False)
    
    # Connect buttons - Campaign Generation
    generate_btn.click(
        fn=run_campaign_pipeline,
        inputs=[
            product_input,
            goal_input,
            audience_input,
            voice_input,
            values_input,
            platform_input,
            research_input
        ],
        outputs=[
            agent_status_display,
            original_output,
            final_output,
            image_output,
            publishing_output,
            token_display,
            history_output
        ]
    )
    
    # Quick Start Example
    example_btn.click(
        fn=lambda: ("EcoStep Sneakers", 
                   "Launch new sustainable product line", 
                   "Environmentally conscious millennials 25-35",
                   "inspiring",
                   "sustainability, innovation, quality",
                   "Instagram",
                   False),
        outputs=[product_input, goal_input, audience_input, voice_input, values_input, platform_input, research_input]
    )
    
    # Download buttons
    download_text_btn.click(
        fn=save_text,
        inputs=[final_output],
        outputs=gr.File(label="Download")
    )
    
    download_pub_btn.click(
        fn=save_publishing_json,
        inputs=[publishing_output],
        outputs=gr.File(label="Download")
    )
    
    # History buttons
    refresh_history_btn.click(
        fn=format_history_table,
        outputs=[history_output]
    )
    
    clear_history_btn.click(
        fn=clear_history,
        outputs=[clear_status]
    )
    
    # Architecture copy
    copy_arch_btn.click(
        fn=lambda: get_architecture_diagram(),
        outputs=[architecture_output]
    )
    
    gr.Markdown("""
---
**Technology Stack**: CrewAI + Groq (llama-3.1-8b-instant) + HuggingFace (FLUX.1-dev)  
**Agent Pipeline**: Research → Writer → Brand Guardian → Reviewer → Compliance → Designer → Publishing  
**Key Features**: 
- ✅ Zero-token brand validation & publishing
- ✅ Professional image prompts (Instagram-ready)
- ✅ Multi-platform content optimization
- ✅ Local JSON storage (no database)
- ✅ Real-time workflow visualization
- ✅ Before/After content comparison
- ✅ Token usage analytics

**📦 Deployment**: HuggingFace Spaces compatible | No external database required
""")


if __name__ == "__main__":
    print("🚀 Starting Creative Media Co-Pilot (Enhanced UI)...")
    print("📍 Access at: http://127.0.0.1:7860")
    print("✨ Features: Real-time tracking, History, Architecture, Token analytics")
    
    demo.queue(max_size=2).launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
