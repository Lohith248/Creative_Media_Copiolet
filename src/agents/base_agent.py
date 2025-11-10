# src/agents/base_agent.py
"""
Base Agent Class - Foundation for all specialized agents
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
import os


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str
    role: str
    goal: str
    backstory: str
    temperature: float = 0.7
    model_name: str = "llama-3.1-8b-instant"


class AgentResponse(BaseModel):
    """Standardized response from an agent"""
    agent_name: str
    status: str  # 'success', 'error', 'pending'
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)


class BaseAgent:
    """
    Base class for all agents in the Creative Media Co-Pilot system.
    Provides common functionality and structure.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.llm = self._initialize_llm()
        self.memory: List[Dict[str, Any]] = []
        
    def _initialize_llm(self) -> ChatGroq:
        """Initialize the LLM for this agent"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        return ChatGroq(
            model=self.config.model_name,
            temperature=self.config.temperature,
            api_key=api_key
        )
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Execute a task. To be overridden by specific agents.
        
        Args:
            task: The task description
            context: Additional context for the task
            
        Returns:
            AgentResponse with the result
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def add_to_memory(self, interaction: Dict[str, Any]):
        """Add an interaction to the agent's memory"""
        self.memory.append(interaction)
    
    def get_recent_memory(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get the n most recent memory items"""
        return self.memory[-n:] if len(self.memory) >= n else self.memory
    
    def clear_memory(self):
        """Clear the agent's memory"""
        self.memory = []
    
    def __str__(self) -> str:
        return f"{self.config.name} ({self.config.role})"
    
    def __repr__(self) -> str:
        return f"BaseAgent(name='{self.config.name}', role='{self.config.role}')"
