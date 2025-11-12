"""Creative Media Co-Pilot - Gradio UI"""

import gradio as gr
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


def generate_campaign(
    product_name: str,
    campaign_goal: str,
    target_audience: str,
    platform: str,
    brand_preset: str,
    custom_brand_values: str = "",
    custom_tone: str = ""
):
    """Generate a complete campaign with AI validation."""
    
    try:
        if brand_preset and brand_preset in BRAND_PRESETS:
            brand = BRAND_PRESETS[brand_preset]
        else:
            brand = BrandProfile(
                name=product_name,
                values=custom_brand_values.split(",") if custom_brand_values else ["Quality", "Innovation"],
                tone=custom_tone if custom_tone else "Professional",
                voice_examples=[]
            )
        
        platform_constraints = PLATFORM_PRESETS.get(
            platform.lower(), 
            PLATFORM_PRESETS["instagram"]
        )
        
        brief = CampaignBrief(
            product_name=product_name,
            campaign_goal=campaign_goal,
            target_audience=target_audience,
            platform=platform,
            brand_profile=brand,
            platform_constraints=platform_constraints
        )
        
        result = crew.create_campaign(brief)
        
        copy_output = f"""
# 📝 Generated Campaign Copy

## Product: {product_name}
## Platform: {platform}
## Goal: {campaign_goal}

---

{result.get('final_copy', 'Copy generation in progress...')}

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
    ### AI-Powered Campaign Generation with Multi-Agent Validation
    
    Generate platform-optimized marketing campaigns with AI-validated quality assurance.
    """)
    
    with gr.Tabs():
        
        # TAB 1: Campaign Creator
        with gr.Tab("📝 Campaign Creator"):
            gr.Markdown("### Create Your Campaign")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### Campaign Details")
                    
                    product_name = gr.Textbox(
                        label="Product/Service Name",
                        placeholder="e.g., Eco-Friendly Water Bottle",
                        value="Eco-Friendly Water Bottle"
                    )
                    
                    campaign_goal = gr.Textbox(
                        label="Campaign Goal",
                        placeholder="e.g., Increase brand awareness, Drive sales",
                        value="Increase brand awareness among eco-conscious millennials"
                    )
                    
                    target_audience = gr.Textbox(
                        label="Target Audience",
                        placeholder="e.g., 25-40 year olds, environmentally conscious",
                        value="25-40 year old urban professionals who care about sustainability"
                    )
                    
                    platform = gr.Dropdown(
                        label="Platform",
                        choices=["Instagram", "Twitter", "LinkedIn", "Facebook"],
                        value="Instagram"
                    )
                    
                    gr.Markdown("#### Brand Voice")
                    
                    brand_preset = gr.Dropdown(
                        label="Brand Preset (Optional)",
                        choices=["", "tech_startup", "eco_brand", "luxury_fashion", "food_brand"],
                        value="eco_brand"
                    )
                    
                    with gr.Accordion("Custom Brand Settings", open=False):
                        custom_brand_values = gr.Textbox(
                            label="Brand Values (comma-separated)",
                            placeholder="e.g., Sustainability, Innovation, Quality"
                        )
                        
                        custom_tone = gr.Textbox(
                            label="Brand Tone",
                            placeholder="e.g., Friendly, Professional, Inspirational"
                        )
                    
                    generate_btn = gr.Button("🚀 Generate Campaign", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown("#### Generated Output")
                    
                    copy_output = gr.Markdown(
                        label="Campaign Copy",
                        value="*Click 'Generate Campaign' to create your content...*"
                    )
                    
                    image_output = gr.Image(
                        label="Generated Image",
                        type="filepath"
                    )
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 🛡️ Validation Report")
                    validation_output = gr.Markdown(
                        value="*Validation results will appear here...*"
                    )
                
                with gr.Column():
                    gr.Markdown("#### 📈 Iteration History")
                    iteration_output = gr.Markdown(
                        value="*Iteration details will appear here...*"
                    )
        
        # TAB 2: AI Validation Dashboard (Coming Soon)
        with gr.Tab("📊 AI Validation Dashboard"):
            gr.Markdown("""
            ### 🚧 Coming Soon!
            
            This tab will show:
            - Real-time validation scores
            - Brand alignment metrics with semantic embeddings
            - Compliance breakdown
            - Quality assessment details
            """)
        
        # TAB 3: Agent Communication Flow (Coming Soon)
        with gr.Tab("🔄 Agent Flow"):
            gr.Markdown("""
            ### 🚧 Coming Soon!
            
            This tab will show:
            - Visual agent workflow diagram
            - Real-time agent status
            - Communication logs
            - Iteration improvements
            """)
        
        # TAB 4: Research & Strategy (Coming Soon)
        with gr.Tab("🔍 Research & Strategy"):
            gr.Markdown("""
            ### 🚧 Coming Soon!
            
            This tab will show:
            - Market research insights
            - Competitor analysis
            - Target audience research
            - Strategic recommendations
            """)
        
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
            custom_tone
        ],
        outputs=[
            copy_output,
            image_output,
            validation_output,
            iteration_output
        ]
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
