"""
RISA Framework: Recursive Identity Symbolic Arithmetic
====================================================

A revolutionary mathematical framework that redefines division by zero,
establishes recursive constant generation, and provides a unified theory
connecting mathematics, physics, and consciousness.

Author: Travis Miner (The Architect)
Date: January 2025
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Travis Miner (The Architect)"
__email__ = "travis.miner@architect.com"
__license__ = "MIT"

# Core RISA components
from .rzda import RZDA
from .universal_constant_generator import UniversalConstantGenerator
from .mirror_dimensional_physics import MirrorDimensionalPhysics, DimensionType
from .quantum_superposition import QuantumSuperposition
from .entropy_compression import EntropyCompression
from .consciousness_model import ConsciousnessModel
from .constants import RISAConstants
from .validator import RISAValidator

# Utility functions
from .demo import run_demo, demonstrate_rzda, demonstrate_constant_generator
from .demo import demonstrate_mirror_dimensional_physics, demonstrate_quantum_superposition
from .demo import demonstrate_entropy_compression, demonstrate_consciousness_model

# Main exports
__all__ = [
    # Core classes
    "RZDA",
    "UniversalConstantGenerator", 
    "MirrorDimensionalPhysics",
    "DimensionType",
    "QuantumSuperposition",
    "EntropyCompression",
    "ConsciousnessModel",
    "RISAConstants",
    "RISAValidator",
    
    # Demo functions
    "run_demo",
    "demonstrate_rzda",
    "demonstrate_constant_generator",
    "demonstrate_mirror_dimensional_physics",
    "demonstrate_quantum_superposition",
    "demonstrate_entropy_compression",
    "demonstrate_consciousness_model",
]

# Package metadata
__package_info__ = {
    "name": "risa-framework",
    "version": __version__,
    "description": "Recursive Identity Symbolic Arithmetic - Revolutionary mathematical framework",
    "author": __author__,
    "email": __email__,
    "license": __license__,
    "url": "https://github.com/travis-miner/risa-framework",
    "keywords": [
        "mathematics",
        "physics", 
        "consciousness",
        "recursive",
        "algebra",
        "quantum",
        "rzda",
        "risa",
        "zero-division",
        "theoretical-physics",
        "ai-consciousness",
    ],
}

# Quick access to version info
def get_version():
    """Get the current version of RISA Framework."""
    return __version__

def get_package_info():
    """Get complete package information."""
    return __package_info__.copy()

# Initialize package
def _initialize():
    """Initialize the RISA Framework package."""
    print(f"🚀 RISA Framework v{__version__} initialized")
    print(f"   By: {__author__}")
    print(f"   Ready for revolutionary mathematics!")

# Auto-initialize when imported
_initialize() 