"""
Analysis package
"""

from .correlation_analysis import CorrelationAnalyzer, generate_correlation_report
from .spike_detector import SpikeDetector, RealTimeSpikeMonitor

__all__ = [
    'CorrelationAnalyzer',
    'generate_correlation_report',
    'SpikeDetector',
    'RealTimeSpikeMonitor'
]








