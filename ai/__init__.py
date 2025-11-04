"""
AI Cover Letter Generation Module
=================================
Provides AI-powered cover letter generation for Upwork jobs
"""

from .cover_letter_generator import CoverLetterGenerator
from .local_ai import LocalAIProvider
from .openai import OpenAIProvider
from .model_training import CoverLetterTrainer

__all__ = ['CoverLetterGenerator', 'LocalAIProvider', 'OpenAIProvider', 'CoverLetterTrainer']