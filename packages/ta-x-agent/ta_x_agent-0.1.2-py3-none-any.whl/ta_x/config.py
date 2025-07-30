import os
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

@dataclass
class XAgentConfig:
    """Configuration class for X Agent settings."""
    x_auth_token: Optional[str] = None
    x_ct0: Optional[str] = None
    openai_api_key: Optional[str] = None
    rapid_api_key: Optional[str] = None
    
    def __post_init__(self):
        """Load environment variables if not explicitly set."""
        load_dotenv(override=True)
        
        if self.x_auth_token is None:
            self.x_auth_token = os.getenv("X_AUTH_TOKEN")
        
        if self.x_ct0 is None:
            self.x_ct0 = os.getenv("X_CT0")
            
        if self.openai_api_key is None:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            
        if self.rapid_api_key is None:
            self.rapid_api_key = os.getenv("RAPID_API_KEY")
    
    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self.x_auth_token:
            raise ValueError("X_AUTH_TOKEN is required. Please set it using setup() or environment variable.")
        
        if not self.x_ct0:
            raise ValueError("X_CT0 is required. Please set it using setup() or environment variable.")
            
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required. Please set it using setup() or environment variable.")
        
        return True

# Global configuration instance
_config = XAgentConfig()

def setup(
    x_auth_token: Optional[str] = None,
    x_ct0: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    rapid_api_key: Optional[str] = None
) -> None:
    """
    Setup the X Agent with required authentication tokens and API keys.
    
    Args:
        x_auth_token: X (Twitter) authentication token
        x_ct0: X (Twitter) ct0 token
        openai_api_key: OpenAI API key for the language model
        rapid_api_key: RapidAPI key for X (Twitter) API access
        
    Example:
        >>> from ta_x import setup
        >>> setup(
        ...     x_auth_token="your_x_auth_token",
        ...     x_ct0="your_x_ct0_token", 
        ...     openai_api_key="your_openai_api_key",
        ...     rapid_api_key="your_rapid_api_key"
        ... )
    """
    global _config
    
    if x_auth_token:
        _config.x_auth_token = x_auth_token
    
    if x_ct0:
        _config.x_ct0 = x_ct0
        
    if openai_api_key:
        _config.openai_api_key = openai_api_key
        
    if rapid_api_key:
        _config.rapid_api_key = rapid_api_key
    
    # Validate configuration
    _config.validate()

def get_config() -> XAgentConfig:
    """Get the current configuration."""
    return _config

def reset_config() -> None:
    """Reset configuration to default values."""
    global _config
    _config = XAgentConfig() 