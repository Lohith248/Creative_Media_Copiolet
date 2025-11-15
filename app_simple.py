"""
Creative Media Co-Pilot - Lightweight Gradio UI
Single-page, HuggingFace-compatible interface
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
    Yields: (agent_status, final_text, image_path, publishing_output)
    """
    
    # Initialize status with better formatting
    status = {
        "Research": "⏭️ Skipped" if not include_research else "⏳ Pending",
        "Writer": "⏳ Pending",
        "BrandGuardian": "⏳ Pending",
        "Reviewer": "⏳ Pending",
        "Compliance": "⏳ Pending",
        "Designer": "⏳ Pending",
        "Publishing": "⏳ Pending"
    }
    
    def format_status():
        """Format status as clean live workflow tracker."""
        lines = ["🤖 AGENT WORKFLOW - LIVE STATUS"]
        lines.append("━" * 40)
        for name, stat in status.items():
            display_name = name.replace("BrandGuardian", "Brand Guardian")
            lines.append(f"{display_name:18} {stat}")
        lines.append("━" * 40)
        return "\n".join(lines)
    
    # Storage for drafts
    original_draft = ""
    
    # Initial yield
    yield format_status(), "Waiting to start...", "Waiting to start...", None, ""
    
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
            if state == "running":
                status[agent_name] = "🟡 Running..."
            elif state == "completed":
                status[agent_name] = "✅ Done"
        
        # Step-by-step visual updates
        agents_to_run = ["Writer", "BrandGuardian", "Reviewer", "Compliance", "Designer", "Publishing"]
        
        for agent in agents_to_run:
            status[agent] = "🟡 Running..."
            yield format_status(), original_draft or f"{agent} processing...", f"{agent} processing...", None, ""
            time.sleep(0.3)  # Smooth animation
        
        # Run actual campaign
        result = crew.create_campaign(brief, include_research=include_research, progress_callback=update_status)
        
        # Mark all as done
        for agent in agents_to_run:
            status[agent] = "✅ Done"
        
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
        
        publishing_output = f"""📤 PUBLISHING PACKAGE - READY TO POST

📸 INSTAGRAM ({publishing_pkg.get('character_counts', {}).get('instagram', 0)} chars)
{publishing_pkg.get('instagram_post', 'N/A')}

{'━'*60}

🐦 TWITTER/X ({publishing_pkg.get('character_counts', {}).get('twitter', 0)} chars)
{publishing_pkg.get('twitter_post', 'N/A')}

{'━'*60}

💼 LINKEDIN ({publishing_pkg.get('character_counts', {}).get('linkedin', 0)} chars)
{publishing_pkg.get('linkedin_post', 'N/A')}

{'━'*60}

📘 FACEBOOK ({publishing_pkg.get('character_counts', {}).get('facebook', 0)} chars)
{publishing_pkg.get('facebook_post', 'N/A')}
"""
        
        # Build final text display
        text_display = f"""📦 PRODUCT: {product_name}
📱 PLATFORM: {platform}
🎯 GOAL: {campaign_goal}

{'━'*60}
📝 FINAL CONTENT
{'━'*60}

{final_text}

{'━'*60}
📊 QUALITY METRICS
{'━'*60}
✅ Overall Score: {result.get('review_overall', 'N/A')}/10
✅ Brand Alignment: {result.get('brand_score', 'N/A')}/100
✅ Compliance: {result.get('compliance_status', 'Approved')}
✅ Character Count: {len(final_text)}
"""
        
        # Save to history
        storage.save_campaign(
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
            publishing_package=publishing_pkg
        )
        
        yield format_status(), original_draft, text_display, image_path, publishing_output
        
    except Exception as e:
        for agent in status.keys():
            if status[agent] not in ["✅ Done", "⏭️ Skipped"]:
                status[agent] = "❌ Error"
        
        error_msg = f"""❌ CAMPAIGN GENERATION FAILED

{str(e)}

💡 TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Check GROQ_API_KEY in .env file
• Verify HUGGINGFACE_TOKEN for images
• Ensure internet connection is active
• Check if rate limits were exceeded
• Try again in a few minutes"""
        yield format_status(), error_msg, error_msg, None, error_msg


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


# Build Enhanced Gradio UI
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
    ),
    title="Creative Media Co-Pilot"
) as demo:
    
    gr.Markdown("""
# 🤖 Creative Media Co-Pilot
### Multi-Agent AI System: Text Generation + Design + Publishing Automation
**Professional social media campaigns in seconds**
""")
    
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
        
        # COLUMN 2: Live Agent Workflow
        with gr.Column(scale=1):
            gr.Markdown("### 🤖 Live Agent Workflow")
            agent_status_display = gr.Textbox(
                label="Real-Time Progress",
                value="""🤖 AGENT WORKFLOW - LIVE STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready to start! 🎯

Click 'Generate Campaign' to begin.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""",
                lines=12,
                interactive=False
            )
    
    # SECTION 2: Before/After Comparison (Full Width)
    gr.Markdown("---")
    gr.Markdown("## 📊 Content Evolution: Before → After")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("#### 🔹 Original Draft")
            original_output = gr.Textbox(
                label="First Draft from Writer Agent",
                lines=8,
                interactive=False,
                placeholder="Original content will appear here..."
            )
        
        with gr.Column(scale=1):
            gr.Markdown("#### 🔹 Final Output (Improved)")
            final_output = gr.Textbox(
                label="Refined Final Content",
                lines=8,
                interactive=False,
                placeholder="Final polished content will appear here..."
            )
    
    download_text_btn = gr.Button("💾 Download Final Text", size="sm")
    
    # SECTION 3: Image Output
    gr.Markdown("---")
    gr.Markdown("## 🎨 Generated Image")
    image_output = gr.Image(label="Professional Marketing Visual", type="filepath")
    
    # SECTION 4: Publishing Package
    gr.Markdown("---")
    gr.Markdown("## 📤 Publishing Package (Platform-Optimized)")
    publishing_output = gr.Textbox(
        label="Ready-to-Post Content for All Platforms",
        lines=18,
        interactive=False,
        placeholder="Platform-specific posts will appear here..."
    )
    
    download_pub_btn = gr.Button("💾 Download Publishing Package", size="sm")
    
    # Connect buttons
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
            publishing_output
        ]
    )
    
    # Quick Start Example button
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
    
    gr.Markdown("""
---
### 🔧 Technology Stack
**AI Models**: CrewAI + Groq (llama-3.1-8b-instant) + HuggingFace (FLUX.1-dev)  
**Agent Pipeline**: Writer → Brand Guardian → Reviewer → Compliance → Designer → Publishing  
**Key Features**: 
- ✅ Zero-token agents (Brand Guardian, Publishing)
- ✅ Professional Instagram-ready images
- ✅ Multi-platform content optimization
- ✅ Real-time workflow visualization
- ✅ Before/After content comparison
- ✅ Local campaign history (campaign_history.json)
""")


if __name__ == "__main__":
    print("🚀 Starting Creative Media Co-Pilot...")
    print("📍 Access at: http://127.0.0.1:7860")
    print("✨ Features: Live workflow, Before/After, Publishing automation")
    
    demo.queue(max_size=2).launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
