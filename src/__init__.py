"""
Stock Fundamentals Analyzer

A Python-based tool for extracting, analyzing, and visualizing business fundamentals 
to identify undervalued small-cap companies across different sectors.
"""

__version__ = "0.1.0"
__author__ = "Paul Boys"
__email__ = "paul.d.boys@gmail.com"

from .analyzer import FundamentalsAnalyzer
from .screener import SmallCapScreener

__all__ = ['FundamentalsAnalyzer', 'SmallCapScreener']