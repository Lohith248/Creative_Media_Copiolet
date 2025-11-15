# 🎨 NNet - Multi-Agent Creative Campaign System

**AI-powered marketing campaign generator using multi-agent collaboration**

Generate complete marketing campaigns with **TEXT + DESIGN + PUBLISHING** automation using CrewAI agents and Groq LLM.

---

## 🌟 Features

### ✅ Complete Workflow
1. **TEXT Generation**: Content Writer → Reviewer → Compliance Agent
2. **DESIGN Creation**: AI Designer with FLUX.1-dev image generation
3. **PUBLISHING**: Platform-specific formatting (Instagram, Twitter, LinkedIn, Facebook)

### 🤖 Multi-Agent System
- **Content Writer**: Creates engaging marketing copy
- **Reviewer**: Quality scoring and feedback (10-point scale)
- **Compliance Agent**: Legal/policy validation (95+ score required)
- **Designer**: Commercial-style image generation
- **Local Brand Guardian**: Zero-token brand alignment checker (embeddings-based)
- **Publishing Agent**: Zero-token platform formatter

### ⚡ Optimized Performance
- **Zero-token agents**: LocalBrandGuardian + PublishingAgent = no LLM overhead
- **Global embedding model**: Load once, reuse everywhere
- **Token efficiency**: max_iterations=1, simplified prompts
- **Rate-limit handling**: 5-key rotation, intelligent delays

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.9+
python --version

# Virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac
```

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Add your API keys to .env:
# - GROQ_API_KEY through GROQ_API_KEY_5
# - HUGGINGFACEHUB_API_TOKEN
```

### Run
```bash
python app_simple.py
```

Open browser to `http://127.0.0.1:7860`

---

## 📦 Project Structure

```
NNet/
├── app_simple.py              # Main Gradio UI (HuggingFace compatible)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── DEPLOYMENT_CHECKLIST.md   # Deployment guide
│
├── src/
│   ├── agents/
│   │   ├── base_agent.py              # Base agent with Groq config
│   │   ├── content_writer.py          # Marketing copy generator
│   │   ├── designer.py                # Image generation coordinator
│   │   ├── reviewer.py                # Content quality evaluator
│   │   ├── compliance_agent.py        # Legal/policy checker
│   │   ├── local_brand_guardian.py    # Zero-token brand aligner
│   │   └── publishing_agent.py        # Zero-token platform formatter
│   │
│   ├── crew/
│   │   └── creative_crew.py           # Multi-agent orchestration
│   │
│   ├── models/
│   │   └── campaign_brief.py          # Campaign data models
│   │
│   ├── tools/
│   │   ├── brand_tools.py             # Brand research tools
│   │   └── image_tools.py             # FLUX.1-dev image generation
│   │
│   └── utils/
│       └── safe_types.py              # Type validation utilities
│
├── outputs/                   # Generated campaigns (auto-created)
└── generated_images/          # AI-generated images (auto-created)
```

---

## 🔑 Environment Variables

Create `.env` file with:

```env
# Groq API Keys (for LLM agents)
GROQ_API_KEY=gsk_...
GROQ_API_KEY_2=gsk_...
GROQ_API_KEY_3=gsk_...
GROQ_API_KEY_4=gsk_...
GROQ_API_KEY_5=gsk_...

# HuggingFace Token (for image generation)
HUGGINGFACEHUB_API_TOKEN=hf_...
```

Get API keys:
- Groq: https://console.groq.com/keys
- HuggingFace: https://huggingface.co/settings/tokens

---

## 🎯 Usage Example

### Input
```
Product: EcoBottle Pro - Smart Water Bottle
Brand Values: Sustainability, Innovation, Health
Target Audience: Fitness enthusiasts 25-40
Campaign Goal: Product launch
Platform: Instagram
```

### Output
1. **Marketing Copy**: Engaging post with hook, value prop, CTA, hashtags
2. **AI Image**: Professional product photography (commercial style)
3. **Publishing Package**: 4 platform-specific posts with character counts

---

## 🛠️ Technology Stack

- **LLM**: Groq API (llama-3.1-8b-instant)
- **Multi-Agent**: CrewAI framework
- **Image Generation**: FLUX.1-dev via HuggingFace
- **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2)
- **UI**: Gradio
- **Language**: Python 3.9+

---

## 📊 Performance

- **Token Usage**: ~15K tokens/campaign (70% reduction from baseline)
- **Generation Time**: 45-90 seconds depending on research option
- **Zero-Token Components**: Brand Guardian + Publishing Agent
- **Rate Limits**: Handled via 5-key rotation + intelligent delays

---

## 🚢 Deployment

### Local
```bash
python app_simple.py
```

### HuggingFace Spaces
1. Create new Space (Gradio SDK)
2. Upload: `app_simple.py`, `src/`, `requirements.txt`
3. Add secrets: API keys
4. Deploy automatically

See `DEPLOYMENT_CHECKLIST.md` for detailed instructions.

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Submit pull request

---

## 📧 Contact

For questions or support, open an issue on GitHub.

---

**Built with ❤️ using CrewAI, Groq, and HuggingFace**
