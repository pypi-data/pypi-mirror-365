"""
TA-X: X (Twitter) Agent Package

A Python package for interacting with X (Twitter) platform using AI agents.

Usage:
    >>> from ta_x import setup, XAgent
    >>> setup(
    ...     x_auth_token="your_x_auth_token",
    ...     x_ct0="your_x_ct0_token",
    ...     openai_api_key="your_openai_api_key"
    ... )
    >>> agent = XAgent()
    >>> result = await agent.run("Post this: Hello world!")
"""

from .config import setup, get_config, reset_config, XAgentConfig
from .agent import XAgent, execute_x_task

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "setup",
    "get_config", 
    "reset_config",
    "XAgentConfig",
    "XAgent",
    "execute_x_task"
]