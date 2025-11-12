# tests/test_agents.py
"""
Tests for the agent system
"""

import pytest
from src.agents.base_agent import BaseAgent, AgentConfig, AgentResponse
from src.agents.content_writer import ContentWriterAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TestBaseAgent:
    """Tests for BaseAgent class"""
    
    def test_agent_initialization(self):
        """Test that a base agent can be initialized"""
        config = AgentConfig(
            name="TestAgent",
            role="Tester",
            goal="Test the system",
            backstory="A test agent"
        )
        
        # BaseAgent is abstract, so we'll test through a concrete implementation
        agent = ContentWriterAgent()
        assert agent.config.name == "ContentWriter"
        assert agent.llm is not None
    
    def test_memory_functions(self):
        """Test agent memory operations"""
        agent = ContentWriterAgent()
        
        # Add to memory
        agent.add_to_memory({"task": "test", "result": "success"})
        assert len(agent.memory) == 1
        
        # Get recent memory
        recent = agent.get_recent_memory(n=1)
        assert len(recent) == 1
        assert recent[0]["task"] == "test"
        
        # Clear memory
        agent.clear_memory()
        assert len(agent.memory) == 0


class TestContentWriterAgent:
    """Tests for ContentWriterAgent"""
    
    def test_content_writer_initialization(self):
        """Test ContentWriterAgent initialization"""
        agent = ContentWriterAgent()
        assert agent.config.name == "ContentWriter"
        assert agent.config.role == "Creative Content Writer"
    
    def test_execute_simple_task(self):
        """Test executing a simple content generation task"""
        agent = ContentWriterAgent()
        
        task = "Write a short tagline for an eco-friendly water bottle"
        context = {
            "brand_voice": "casual and inspiring",
            "max_length": 15
        }
        
        response = agent.execute(task, context)
        
        assert response.status == "success"
        assert response.content is not None
        assert len(response.content) > 0
        assert response.agent_name == "ContentWriter"
    
    def test_execute_with_key_points(self):
        """Test content generation with specific key points"""
        agent = ContentWriterAgent()
        
        task = "Write an Instagram caption for a new product launch"
        context = {
            "brand_voice": "excited and friendly",
            "target_audience": "millennials",
            "key_points": [
                "Revolutionary design",
                "Sustainable materials",
                "Limited time offer"
            ],
            "content_type": "social_post",
            "max_length": 100
        }
        
        response = agent.execute(task, context)
        
        assert response.status == "success"
        assert response.content is not None
        assert "word_count" in response.metadata
    
    def test_generate_variations(self):
        """Test generating variations of content"""
        agent = ContentWriterAgent()
        
        original = "Discover the future of sustainable living."
        response = agent.generate_variations(original, num_variations=3)
        
        assert response.status == "success"
        assert response.content is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
