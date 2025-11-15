"""
Creative Media Co-Pilot - Lightweight Gradio UI
Single-page, HuggingFace-compatible interface
"""

import os
import gradio as gr
from datetime import datetime
import json

# Set environment variables
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["LITELLM_FORCE_DISABLE_TRACE"] = "true"
os.environ["LITELLM_LOGGING"] = "false"

# Import our multi-agent system
from src.crew.creative_crew import CreativeMediaCrew
from src.models.campaign_brief import CampaignBrief, BrandProfile, PLATFORM_PRESETS, BRAND_PRESETS


def run_campaign_pipeline(
    product_name: str,
    campaign_goal: str,
    target_audience: str,
    brand_voice: str,
    brand_values: str,
    platform: str,
    include_research: bool,
    iterations: int
):
    """
    Run the multi-agent pipeline with real-time status updates.
    Yields: (agent_status, final_text, image_path, publishing_output)
    """
    
    # Initialize status
    status = {
        "Research": "⏭️ Skipped" if not include_research else "🟦 Waiting",
        "Writer": "🟦 Waiting",
        "BrandGuardian": "🟦 Waiting",
        "Reviewer": "🟦 Waiting",
        "Compliance": "🟦 Waiting",
        "Designer": "🟦 Waiting",
        "Publishing": "🟦 Waiting"
    }
    
    def format_status():
        # Clean monospace format
        lines = []
        for name, stat in status.items():
            lines.append(f"{name:15} {stat}")
        return "\n".join(lines)
    
    # Initial yield
    yield format_status(), "Initializing...", None, ""
    
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
        crew = CreativeMediaCrew(max_iterations=iterations)
        
        # Update status callback
        def update_status(agent_name, state, message, output):
            if state == "running":
                status[agent_name] = "🟡 Running..."
            elif state == "completed":
                status[agent_name] = "🟢 Done"
            # Don't yield here, let main flow control yields
        
        # Run campaign (this blocks until complete)
        status["Writer"] = "🟡 Running..."
        yield format_status(), "Writer agent creating content...", None, ""
        
        result = crew.create_campaign(brief, include_research=include_research, progress_callback=update_status)
        
        # Mark all as done
        status["Writer"] = "🟢 Done"
        status["BrandGuardian"] = "🟢 Done"
        status["Reviewer"] = "🟢 Done"
        status["Compliance"] = "🟢 Done"
        status["Designer"] = "🟢 Done"
        status["Publishing"] = "🟢 Done"
        
        # Extract results
        final_text = result.get("final_copy", "Content generated successfully")
        image_path = result.get("image_path", None)
        
        # Format publishing output
        publishing_pkg = result.get("publishing_package", {})
        
        publishing_output = f"""📱 PUBLISHING PACKAGE

📸 INSTAGRAM ({publishing_pkg.get('character_counts', {}).get('instagram', 0)} chars)
{publishing_pkg.get('instagram_post', 'N/A')}

{'─'*60}

🐦 TWITTER/X ({publishing_pkg.get('character_counts', {}).get('twitter', 0)} chars)
{publishing_pkg.get('twitter_post', 'N/A')}

{'─'*60}

💼 LINKEDIN ({publishing_pkg.get('character_counts', {}).get('linkedin', 0)} chars)
{publishing_pkg.get('linkedin_post', 'N/A')}

{'─'*60}

📘 FACEBOOK ({publishing_pkg.get('character_counts', {}).get('facebook', 0)} chars)
{publishing_pkg.get('facebook_post', 'N/A')}
"""
        
        # Build final text display
        text_display = f"""PRODUCT: {product_name}
PLATFORM: {platform}
GOAL: {campaign_goal}

{'='*60}
GENERATED CONTENT
{'='*60}

{final_text}

{'='*60}
QUALITY METRICS
{'='*60}
Overall Score: {result.get('review_overall', 'N/A')}/10
Brand Alignment: {result.get('brand_score', 'N/A')}/100
Compliance: {result.get('compliance_status', 'Approved')}
Character Count: {len(final_text)}
"""
        
        yield format_status(), text_display, image_path, publishing_output
        
    except Exception as e:
        status = {k: "❌ Error" for k in status.keys()}
        error_msg = f"""❌ Campaign Generation Failed

{str(e)}

💡 Troubleshooting:
- Check GROQ_API_KEY in .env file
- Verify HUGGINGFACE_TOKEN for images
- Ensure internet connection is active
- Check if rate limits were exceeded"""
        yield format_status(), error_msg, None, error_msg


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


# Build Gradio UI
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
    ),
    title="Creative Media Co-Pilot"
) as demo:
    
    gr.Markdown("""
# 🤖 Creative Media Co-Pilot
### Multi-Agent AI System: Text Generation + Design + Publishing
""")
    
    with gr.Row():
        # SECTION A: Input Panel (Left)
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
            
            iterations_input = gr.Slider(
                label="Number of Improvement Iterations",
                minimum=1,
                maximum=5,
                step=1,
                value=1,
                info="Sets the number of times agents will review and improve the content."
            )

            with gr.Row():
                generate_btn = gr.Button("🚀 Generate Campaign", variant="primary", scale=2)
                example_btn = gr.Button("✨ Quick Start Example", variant="secondary", scale=1)
        
        # SECTION B: Agent Status (Middle)
        with gr.Column(scale=1):
            gr.Markdown("### 🤖 Agent Workflow")
            agent_status_display = gr.Textbox(
                label="Real-Time Status",
                value="""Ready to start! 🎯

Click 'Generate Campaign' to begin.
Or try 'Quick Start Example' for a demo.""",
                lines=10,
                interactive=False
            )
        
        # SECTION C: Final Output (Right)
        with gr.Column(scale=2):
            gr.Markdown("### 📊 Final Output")
            
            gr.Markdown("#### 1️⃣ Generated Text")
            text_output = gr.Textbox(
                label="Campaign Copy",
                lines=10,
                interactive=False
            )
            
            download_text_btn = gr.Button("💾 Download Text", size="sm")
            
            gr.Markdown("#### 2️⃣ Generated Image")
            image_output = gr.Image(label="Visual Content", type="filepath")
            
            gr.Markdown("#### 3️⃣ Publishing Package")
            publishing_output = gr.Textbox(
                label="Platform-Specific Posts",
                lines=15,
                interactive=False
            )
            
            download_pub_btn = gr.Button("💾 Download Publishing Package", size="sm")
    
    # Connect button
    generate_btn.click(
        fn=run_campaign_pipeline,
        inputs=[
            product_input,
            goal_input,
            audience_input,
            voice_input,
            values_input,
            platform_input,
            research_input,
            iterations_input
        ],
        outputs=[
            agent_status_display,
            text_output,
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
                   False,
                   1),
        outputs=[product_input, goal_input, audience_input, voice_input, values_input, platform_input, research_input, iterations_input]
    )
    
    # Download buttons
    download_text_btn.click(
        fn=save_text,
        inputs=[text_output],
        outputs=gr.File(label="Download")
    )
    
    download_pub_btn.click(
        fn=save_publishing_json,
        inputs=[publishing_output],
        outputs=gr.File(label="Download")
    )
    
    gr.Markdown("""
---
**Powered by**: CrewAI + Groq (llama-3.1-8b-instant) + HuggingFace (FLUX.1-dev)  
**Agents**: Research → Writer → Brand Guardian → Reviewer → Compliance → Designer → Publishing  
**Features**: Zero-token brand validation, Multi-platform publishing, Real-time status updates
""")


if __name__ == "__main__":
    print("🚀 Starting Creative Media Co-Pilot (Lightweight UI)...")
    print("📍 Access at: http://127.0.0.1:7860")
    
    demo.queue(max_size=1).launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
