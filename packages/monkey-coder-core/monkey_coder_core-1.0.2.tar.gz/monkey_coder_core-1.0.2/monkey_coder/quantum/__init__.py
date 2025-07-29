"""
Quantum Execution Module

This module implements functional quantum execution patterns inspired by quantum computing 
principles for parallel task execution, collapse strategies, and performance optimization.
"""

from .manager import QuantumManager, quantum_task, CollapseStrategy

__all__ = [
    "QuantumManager",
    "quantum_task", 
    "CollapseStrategy",
]
