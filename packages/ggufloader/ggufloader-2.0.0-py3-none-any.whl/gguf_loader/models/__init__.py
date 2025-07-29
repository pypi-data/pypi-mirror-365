"""
Models package - Contains all model-related functionality

This package provides model loading, chat generation, and addon integration
for GGUF models.
"""

from .model_loader import ModelLoader
from .chat_generator import ChatGenerator
from .addon_manager import AddonManager

__all__ = [
    'ModelLoader',
    'ChatGenerator', 
    'AddonManager'
]
