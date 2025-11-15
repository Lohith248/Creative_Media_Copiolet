# src/utils/safe_types.py
"""
Type-safe utility functions to prevent serialization and type errors.
"""
from typing import Any, Union, List, Dict


def safe_str(value: Any, default: str = "") -> str:
    """
    Safely convert any value to a string.
    
    Args:
        value: Any value to convert
        default: Default value if conversion fails
        
    Returns:
        String representation of the value
    """
    if value is None:
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        # Join list items safely
        return " ".join(str(item) for item in value)
    if isinstance(value, dict):
        # For dicts, return a formatted string
        return str(value)
    return str(value)


def safe_join(parts: Union[str, List, tuple], sep: str = " ") -> str:
    """
    Safely join parts into a string, handling both strings and iterables.
    
    Args:
        parts: String or iterable to join
        sep: Separator string
        
    Returns:
        Joined string
        
    Example:
        >>> safe_join("hello")
        'hello'
        >>> safe_join(["hello", "world"])
        'hello world'
        >>> safe_join(["hello", 123, None])
        'hello 123 None'
    """
    if isinstance(parts, str):
        return parts
    if isinstance(parts, (list, tuple)):
        # Ensure all elements are stringified
        return sep.join(str(x) if x is not None else "" for x in parts)
    return str(parts)


def safe_list(value: Any, default: List = None) -> List:
    """
    Safely convert any value to a list.
    
    Args:
        value: Any value to convert
        default: Default value if conversion fails
        
    Returns:
        List representation of the value
    """
    if default is None:
        default = []
        
    if value is None:
        return default
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    if isinstance(value, str):
        # Don't split strings into characters - treat as single item
        return [value] if value else default
    if isinstance(value, dict):
        return [value]
    return [value]


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert any value to an integer.
    
    Args:
        value: Any value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer representation of the value
    """
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, (float, str)):
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default
    if isinstance(value, (list, tuple)):
        return len(value)
    return default


def safe_dict(value: Any, default: Dict = None) -> Dict:
    """
    Safely convert any value to a dictionary.
    
    Args:
        value: Any value to convert
        default: Default value if conversion fails
        
    Returns:
        Dictionary representation of the value
    """
    if default is None:
        default = {}
        
    if value is None:
        return default
    if isinstance(value, dict):
        return value
    return default


def normalize_agent_output(output: Any) -> str:
    """
    Normalize agent output to ensure it's always a clean string.
    Handles cases where CrewAI returns lists, dicts, or other types.
    
    Args:
        output: Raw output from an agent
        
    Returns:
        Clean string output
    """
    if output is None:
        return ""
    
    # If it's already a string, return it
    if isinstance(output, str):
        return output.strip()
    
    # If it's a list, join items
    if isinstance(output, (list, tuple)):
        return safe_join(output, sep="\n")
    
    # If it's a dict, try to extract common fields
    if isinstance(output, dict):
        # Try common output field names
        for field in ['output', 'text', 'content', 'result', 'message']:
            if field in output:
                return normalize_agent_output(output[field])
        # Fall back to string representation
        return str(output)
    
    # For any other type, convert to string
    return str(output).strip()


def validate_string_output(output: Any, agent_name: str = "Agent") -> str:
    """
    Validate and normalize agent output with error checking.
    
    Args:
        output: Raw output from an agent
        agent_name: Name of the agent for error messages
        
    Returns:
        Validated string output
        
    Raises:
        ValueError: If output cannot be normalized to a valid string
    """
    try:
        normalized = normalize_agent_output(output)
        if not normalized:
            raise ValueError(f"{agent_name} returned empty output")
        return normalized
    except Exception as e:
        raise ValueError(f"{agent_name} output normalization failed: {e}")
