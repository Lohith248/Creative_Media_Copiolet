# Agent Workflow Architecture

## Complete Agent Flow (with Research Agent)

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMPAIGN BRIEF INPUT                      │
│  (Product, Audience, Goals, Brand Voice, Platform)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              🔍 RESEARCH AGENT (NEW!)                        │
│              Model: Llama 3.1-70b-versatile                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • Market Trend Analysis                              │    │
│  │ • Target Audience Research                           │    │
│  │ • Competitor Content Analysis                        │    │
│  │ • Strategic Framework Recommendations                │    │
│  │ • Key Messaging Insights                             │    │
│  │ • Web Search (via Serper API - optional)             │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────────────┘
                     │ Provides market context
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              ✍️ CONTENT WRITER AGENT                         │
│              Model: Llama 3.1-8b-instant                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • Uses research insights for informed writing        │    │
│  │ • Generates platform-optimized copy                  │    │
│  │ • Incorporates strategic recommendations             │    │
│  │ • Creates headlines, body, CTAs                      │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  VALIDATION LOOP      │
         │  (Up to 3 iterations) │
         └───────────┬───────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│  📊 REVIEWER     │      │  🛡️ BRAND         │
│  AGENT           │      │  GUARDIAN        │
│  Quality: 8.5/10 │      │  Alignment: 87%  │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  ⚖️ COMPLIANCE │
              │  AGENT         │
              │  Status: Pass  │
              └───────┬───────┘
                      │
          ┌───────────┴────────────┐
          │                        │
          ▼                        ▼
    [Score ≥ 7.5?]         [Score < 7.5?]
          │                        │
          │ YES                    │ NO
          │                        │
          │                        └──────┐
          │                               │
          │                               ▼
          │                    ┌──────────────────────┐
          │                    │ PROVIDE FEEDBACK     │
          │                    │ Loop back to Writer  │
          │                    │ (Iteration 2 or 3)   │
          │                    └──────────┬───────────┘
          │                               │
          │                               │
          │◄──────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              🎨 DESIGNER AGENT                               │
│              Model: FLUX.1-dev (HuggingFace)                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • Generates visual based on approved copy            │    │
│  │ • Platform-specific image dimensions                 │    │
│  │ • Brand-aligned visual style                         │    │
│  │ • High-quality image output                          │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINAL OUTPUT                              │
│  • AI-validated copy (with quality scores)                  │
│  • Generated image                                           │
│  • Validation metrics (brand, compliance, quality)          │
│  • Iteration history                                         │
│  • Research insights summary                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Details

### 1. Research Agent (NEW) 🔍
- **Model**: Qwen 2.5-14B-Instruct
- **Position**: FIRST (runs before content creation)
- **Purpose**: Gathers market intelligence and strategic context
- **Why Qwen**: Specifically optimized for agentic tasks, function calling, and research
- **Key Features**:
  - Web search via Serper API (optional)
  - Market trend analysis
  - Competitor content analysis
  - Audience insights (demographics, psychographics, pain points)
  - Strategic framework recommendations (4P's, AIDA, etc.)
  - Key messaging suggestions
- **Output**: Research report that informs Content Writer
- **Why 70b?**: Better reasoning for complex analysis tasks

### 2. Content Writer Agent ✍️
- **Model**: Llama 3.1-8b-instant
- **Position**: After Research Agent
- **Purpose**: Generate platform-optimized copy
- **Input**: Campaign brief + Research insights
- **Output**: Headlines, body copy, CTAs

### 3. Reviewer Agent 📊
- **Model**: Llama 3.1-8b-instant
- **Position**: First validator
- **Purpose**: Quality assessment
- **Scores**:
  - Readability (1-10)
  - Engagement potential (1-10)
  - Overall quality (1-10)
- **Threshold**: ≥7.5 to pass

### 4. Brand Guardian Agent 🛡️
- **Model**: Llama 3.1-8b-instant + MiniLM-L6-v2 embeddings
- **Position**: Second validator
- **Purpose**: Brand voice alignment
- **Method**: Semantic similarity with cosine distance
- **Output**: Brand alignment score (0-100)

### 5. Compliance Agent ⚖️
- **Model**: Llama 3.1-8b-instant
- **Position**: Third validator
- **Purpose**: Legal/ethical/policy compliance
- **Checks**:
  - Copyright/trademark issues
  - False claims
  - Ethical concerns
  - Platform policies
- **Output**: Pass/Fail + issues list

### 6. Designer Agent 🎨
- **Model**: FLUX.1-dev (via HuggingFace)
- **Position**: LAST (after all validation passes)
- **Purpose**: Generate visual content
- **Input**: Approved copy + brand guidelines
- **Output**: Platform-optimized image

---

## Model Strategy

### Why Different Models?

**Qwen 2.5-14B-Instruct** (Research Agent only):
- ✅ **Purpose-built for agentic tasks** (function calling, tool use)
- ✅ Superior performance on research and analytical reasoning
- ✅ Optimized for web search integration via Serper API
- ✅ Better structured output generation
- ✅ Perfect balance: faster than 70B, smarter than 8B
- ✅ Recommended by Perplexity for research agent use cases

**Llama 3.1-8b-instant** (Content Writer + 3 Validators):
- ✅ Lightning fast via Groq
- ✅ Sufficient for content generation and validation
- ✅ Lower latency = better user experience
- ✅ Can run multiple agents in parallel

**FLUX.1-dev** (Designer Agent):
- ✅ State-of-the-art open-source image generation
- ✅ High quality, brand-appropriate visuals
- ✅ No DALL-E or Midjourney needed

**MiniLM-L6-v2** (Brand Guardian embeddings):
- ✅ Local computation (no API calls)
- ✅ Fast semantic similarity
- ✅ Accurate brand voice matching

---

## Workflow Logic

### Sequential Flow:
1. **Research** → Gathers context (runs once)
2. **Content** → Writes copy using research
3. **Validation** → Three agents check quality
4. **Iteration** → If score < 7.5, improve (max 3 rounds)
5. **Design** → Generate image for approved copy

### Parallel Opportunities:
- Reviewer, Brand Guardian, and Compliance can run in parallel
- Speeds up validation phase
- All must pass for content to be approved

### Iteration Logic:
```python
for iteration in range(1, 4):  # Max 3 attempts
    content = content_writer.generate(brief, research_insights)
    
    # Validate in parallel
    review_score = reviewer.evaluate(content)
    brand_score = brand_guardian.check(content, brand_voice)
    compliance = compliance_agent.verify(content)
    
    if all_pass(review_score, brand_score, compliance):
        break  # Success!
    else:
        feedback = compile_feedback(review, brand, compliance)
        # Loop continues with feedback
```

---

## Integration with CreativeMediaCrew

The Research Agent will be integrated into `creative_crew.py`:

```python
class CreativeMediaCrew:
    def __init__(self):
        self.research_agent = create_research_agent()  # NEW!
        self.content_writer = create_content_writer()
        self.reviewer = create_reviewer()
        self.brand_guardian = create_brand_guardian()
        self.compliance = create_compliance_agent()
        self.designer = create_designer()
    
    def create_campaign(self, brief):
        # 1. Research FIRST
        research_insights = self.research_agent.execute(brief)
        
        # 2. Content generation with research context
        content = self.content_writer.execute(brief, research_insights)
        
        # 3. Validation loop (existing logic)
        # ... (reviewer, brand guardian, compliance)
        
        # 4. Design (existing logic)
        # ...
```

---

## API Keys Required

```bash
# Required
GROQ_API_KEY=your_groq_key_here
HUGGINGFACE_API_KEY=your_hf_key_here

# Optional (for Research Agent web search)
SERPER_API_KEY=your_serper_key_here
```

**Note**: Research Agent works without Serper API (uses LLM knowledge), but web search enables real-time data and better trend analysis.

---

## Performance Considerations

### Speed:
- Research Agent: ~10-15 seconds (70b model, comprehensive analysis)
- Content Writer: ~3-5 seconds (8b model, fast)
- Validators (3 agents): ~5-7 seconds total (can run in parallel)
- Designer: ~5-10 seconds (image generation)

**Total**: ~25-40 seconds per campaign (including iterations)

### Cost:
- All models are FREE via Groq/HuggingFace APIs
- Serper API: $50 free credits/month (optional)
- 100% open-source compliant ✅

---

**Last Updated**: November 11, 2025
**Status**: Research Agent created, ready for integration
**Next Step**: Update creative_crew.py to include Research Agent
