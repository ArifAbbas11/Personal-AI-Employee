"""
Machine Learning Engine for Platinum Tier AI Employee

Provides ML capabilities for pattern recognition, classification, and prediction.
"""

from .base import BaseMLModel, MLModelConfig
from .model_manager import ModelManager
from .email_classifier import EmailClassifier
from .task_predictor import TaskPredictor
from .expense_categorizer import ExpenseCategorizer
from .content_optimizer import ContentOptimizer

__all__ = [
    'BaseMLModel',
    'MLModelConfig',
    'ModelManager',
    'EmailClassifier',
    'TaskPredictor',
    'ExpenseCategorizer',
    'ContentOptimizer',
]
