"""
🧠 LinkTune Neural Enhancement Blocks
Advanced neural synthesis and AI-powered music generation
"""

from .orpheus_bridge import create_orpheus_block
from .harmony import NeuralHarmonyBlock, create_neural_harmony_block

__all__ = [
    'create_orpheus_block',
    'NeuralHarmonyBlock', 
    'create_neural_harmony_block'
]