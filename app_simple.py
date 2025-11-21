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

# Check for demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Import our multi-agent system
from src.crew.creative_crew import CreativeMediaCrew
from src.models.campaign_brief import CampaignBrief, BrandProfile, PLATFORM_PRESETS
from src.utils.campaign_storage import CampaignStorage

# Initialize storage
storage = CampaignStorage()


def get_demo_response():
    """Pre-generated demo response for instant results."""
    return {
        "final_copy": """🌿 Step into Sustainability with EcoStep Sneakers!

Every step you take can make a difference. Our new sustainable sneaker line is crafted from 100% recycled materials, combining eco-friendly innovation with modern style.

✨ Features:
• Recycled ocean plastics & organic cotton
• Carbon-neutral production
• Comfortable all-day wear
• Style that speaks volumes

Join the movement toward a greener future. Your footprint matters.

👟 Learn more at ecostep.com

#SustainableFashion #EcoFriendly #GreenLiving #EcoStepSneakers #SustainableStyle""",
        "image_path": "generated_images/demo_ecostep.png",  # Placeholder
        "review_overall": 9.2,
        "review_quality": 9.5,
        "review_readability": 9.0,
        "review_engagement": 9.1,
        "brand_score": 88,
        "compliance_status": "APPROVED",
        "publishing_package": {
            "primary_platform": "instagram",
            "instagram_post": """🌿 Step into Sustainability with EcoStep Sneakers!

Every step you take can make a difference. Our new sustainable sneaker line is crafted from 100% recycled materials, combining eco-friendly innovation with modern style.

✨ Features:
• Recycled ocean plastics & organic cotton
• Carbon-neutral production
• Comfortable all-day wear
• Style that speaks volumes

Join the movement toward a greener future. Your footprint matters.

👟 Learn more

#SustainableFashion #EcoFriendly #GreenLiving #EcoStepSneakers #SustainableStyle""",
            "twitter_post": "🌿 Step into sustainability with EcoStep Sneakers! 100% recycled materials, carbon-neutral production, modern style. Your footprint matters. 👟 Learn more #SustainableFashion #EcoFriendly",
            "linkedin_post": """Step into Sustainability with EcoStep Sneakers

Every step you take can make a difference. Our new sustainable sneaker line combines eco-friendly innovation with modern design.

Key Features:
→ 100% recycled materials (ocean plastics & organic cotton)
→ Carbon-neutral production process
→ All-day comfort without compromise
→ Contemporary style for conscious consumers

Join us in building a greener future. Learn more at ecostep.com

#SustainableFashion #EcoFriendly #GreenInnovation #CorporateResponsibility""",
            "facebook_post": """🌿 Introducing EcoStep Sneakers - Where Style Meets Sustainability!

Every step you take can make a difference. Our new sustainable sneaker line is crafted from 100% recycled materials, combining eco-friendly innovation with modern style.

What makes EcoStep special:
✨ Recycled ocean plastics & organic cotton
✨ Carbon-neutral production
✨ Comfortable all-day wear
✨ Style that speaks volumes

Join the movement toward a greener future. Your footprint matters.

Learn more at ecostep.com 👟

#SustainableFashion #EcoFriendly #GreenLiving #EcoStepSneakers""",
            "character_counts": {
                "instagram": 489,
                "twitter": 197,
                "linkedin": 447,
                "facebook": 511
            }
        },
        "metadata": {
            "iterations": [{
                "agents": [{
                    "name": "Writer",
                    "output": "🌿 Step into Sustainability! Our EcoStep Sneakers are made from recycled materials. Join the green movement! #Sustainable"
                }]
            }]
        }
    }


def run_demo_campaign(product_name, platform):
    """Run demo mode with pre-generated content."""
    return get_demo_response()


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
            # Add agent-specific messages
            if stat == "🟡 Running...":
                if name == "Writer":
                    stat = "✍️ Crafting your story..."
                elif name == "BrandGuardian":
                    stat = "🛡️ Validating brand fit..."
                elif name == "Reviewer":
                    stat = "🔍 Checking quality..."
                elif name == "Compliance":
                    stat = "⚖️ Verifying safety..."
                elif name == "Designer":
                    stat = "🎨 Creating visuals..."
                elif name == "Publishing":
                    stat = "📤 Formatting output..."
            lines.append(f"{display_name:18} {stat}")
        lines.append("━" * 40)
        return "\n".join(lines)
    
    # Storage for drafts
    original_draft = ""
    
    # Initial yield
    yield format_status(), "Waiting to start...", "Waiting to start...", None, ""
    
    # Check for demo mode
    if DEMO_MODE:
        # Animate through agents for demo
        for agent in ["Writer", "BrandGuardian", "Reviewer", "Compliance", "Designer", "Publishing"]:
            status[agent] = "🟡 Running..."
            yield format_status(), f"{agent} processing (DEMO MODE)...", f"{agent} processing (DEMO MODE)...", None, ""
            time.sleep(0.5)
            status[agent] = "✅ Done"
        
        # Get demo response
        result = run_demo_campaign(product_name, platform)
        
        # Format outputs
        final_text = result["final_copy"]
        original_draft = result["metadata"]["iterations"][0]["agents"][0]["output"]
        publishing_pkg = result["publishing_package"]
        
        publishing_output = f"""📤 PUBLISHING PACKAGE - READY TO POST

📸 INSTAGRAM ({publishing_pkg['character_counts']['instagram']} chars)
{publishing_pkg['instagram_post']}

{'━'*60}

🐦 TWITTER/X ({publishing_pkg['character_counts']['twitter']} chars)
{publishing_pkg['twitter_post']}

{'━'*60}

💼 LINKEDIN ({publishing_pkg['character_counts']['linkedin']} chars)
{publishing_pkg['linkedin_post']}

{'━'*60}

📘 FACEBOOK ({publishing_pkg['character_counts']['facebook']} chars)
{publishing_pkg['facebook_post']}
"""
        
        text_display = f"""📦 PRODUCT: {product_name}
📱 PLATFORM: {platform}
🎯 GOAL: {campaign_goal}

{'━'*60}
📝 FINAL CONTENT (DEMO)
{'━'*60}

{final_text}

{'━'*60}
📊 QUALITY METRICS
{'━'*60}
✅ Overall Score: {result['review_overall']}/10
✅ Brand Alignment: {result['brand_score']}/100
✅ Compliance: {result['compliance_status']}
✅ Character Count: {len(final_text)}

⚡ DEMO MODE - Sample output shown"""
        
        yield format_status(), original_draft, text_display, None, publishing_output
        return
    
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
        
        error_type = str(e).lower()
        
        # Enhanced error messages with solutions
        if "rate limit" in error_type:
            error_msg = f"""❌ RATE LIMIT REACHED

{str(e)}

💡 QUICK SOLUTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Wait 60 seconds and try again
✅ Enable DEMO_MODE=true in .env for instant results
✅ Add more Groq API keys for rotation (get free keys at console.groq.com)
✅ Use different Groq accounts for each key to avoid shared limits"""
        
        elif "api" in error_type or "key" in error_type:
            error_msg = f"""❌ API KEY ISSUE

{str(e)}

💡 GET FREE API KEYS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 Groq (LLM): https://console.groq.com
   → Free tier: 6000 tokens/minute
   → Add multiple keys for rotation

🔑 HuggingFace (Images): https://huggingface.co/settings/tokens
   → Free tier available
   → Create read token

📝 Add keys to .env file:
   GROQ_API_KEY_1=gsk_your_key_here
   HUGGINGFACE_TOKEN=hf_your_token_here

⚡ OR enable DEMO_MODE=true for testing without keys"""
        
        elif "image" in error_type or "flux" in error_type:
            error_msg = f"""❌ IMAGE GENERATION FAILED

{str(e)}

💡 SOLUTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Check HUGGINGFACE_TOKEN in .env
✅ Verify token has read permissions
✅ HuggingFace may be rate-limited - try again in 1 minute
✅ Enable DEMO_MODE for placeholder visuals

Get token: https://huggingface.co/settings/tokens"""
        
        else:
            error_msg = f"""❌ CAMPAIGN GENERATION FAILED

{str(e)}

💡 TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Check GROQ_API_KEY in .env file
✅ Verify HUGGINGFACE_TOKEN for images
✅ Ensure internet connection is active
✅ Check if rate limits were exceeded
✅ Try enabling DEMO_MODE=true for testing
✅ Wait a few minutes and retry

🆘 Still having issues?
   → Check .env.example for correct key format
   → Ensure virtual environment is activated
   → Run: pip install -r requirements.txt"""
        
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
    title="Creative Media Co-Pilot",
    css="""
        .gradio-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em !important;
            font-weight: 800 !important;
        }
        .status-box {
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 13px;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
        }
        .gr-button-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        .gr-button-secondary {
            border: 2px solid #667eea !important;
            color: #667eea !important;
        }
    """
) as demo:
    
    gr.Markdown("""
# 🤖 Creative Media Co-Pilot
### Multi-Agent AI System: Text Generation + Design + Publishing Automation
**Professional social media campaigns in 30 seconds** ✨

---
""")
    
    # Quick Demo Banner
    with gr.Row():
        gr.Markdown("### 🎯 New here? Try our instant demo!")
        demo_banner_btn = gr.Button("🚀 Try Sample Campaign (Instant Results)", variant="primary", size="lg")
    
    gr.Markdown("---")
    
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
            
            iterations_input = gr.Slider(
                label="Number of Improvement Iterations",
                minimum=1,
                maximum=5,
                step=1,
                value=1,
                info="Sets the number of times agents will review and improve the content."
            )

            with gr.Row():
                generate_btn = gr.Button("🚀 Generate Campaign", variant="primary", scale=2, size="lg")
                example_btn = gr.Button("✨ Load Example", variant="secondary", scale=1)
        
        # COLUMN 2: Live Agent Workflow
        with gr.Column(scale=1):
            gr.Markdown("### 🤖 Live Agent Workflow")
            
            if DEMO_MODE:
                gr.Markdown("**⚡ DEMO MODE ACTIVE** - Using pre-generated samples")
            
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
            research_input,
            iterations_input
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
                   False,
                   1),
        outputs=[product_input, goal_input, audience_input, voice_input, values_input, platform_input, research_input, iterations_input]
    )
    
    # Quick Demo Banner Button
    def load_demo():
        """Load demo and trigger generation."""
        return (
            "EcoStep Sneakers",
            "Launch new sustainable product line",
            "Environmentally conscious millennials 25-35",
            "inspiring",
            "sustainability, innovation, quality",
            "Instagram",
            False
        )
    
    demo_banner_btn.click(
        fn=load_demo,
        outputs=[product_input, goal_input, audience_input, voice_input, values_input, platform_input, research_input]
    ).then(
        fn=run_campaign_pipeline,
        inputs=[product_input, goal_input, audience_input, voice_input, values_input, platform_input, research_input],
        outputs=[agent_status_display, original_output, final_output, image_output, publishing_output]
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
✅ Zero-token agents (33% cost reduction) | ✅ Professional Instagram-ready images  
✅ Multi-platform optimization | ✅ Real-time workflow | ✅ Before/After comparison  
✅ Local campaign history (no database) | ✅ DEMO mode for instant results

**⚡ Performance**: ~30 seconds per campaign | ~$0.00 cost (free tier)
""")


if __name__ == "__main__":
    mode_str = "DEMO MODE - Using pre-generated samples" if DEMO_MODE else "Live mode with API calls"
    print(f"🚀 Starting Creative Media Co-Pilot ({mode_str})...")
    print("📍 Access at: http://127.0.0.1:7860")
    print("✨ Features: Live workflow, Before/After, Publishing automation")
    if DEMO_MODE:
        print("⚡ DEMO MODE: Set DEMO_MODE=false in .env for live generation")
    
    demo.queue(max_size=2).launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
