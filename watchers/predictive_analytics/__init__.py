"""
Predictive Analytics Package

Provides time-series forecasting and predictive models for business intelligence.
"""

from .base import BasePredictiveModel, PredictionConfig, Prediction, ForecastResult
from .revenue_forecaster import RevenueForecaster
from .cash_flow_predictor import CashFlowPredictor
from .churn_predictor import ChurnPredictor
from .bottleneck_predictor import BottleneckPredictor
from .predictive_ceo_briefing import PredictiveCEOBriefing

__all__ = [
    'BasePredictiveModel',
    'PredictionConfig',
    'Prediction',
    'ForecastResult',
    'RevenueForecaster',
    'CashFlowPredictor',
    'ChurnPredictor',
    'BottleneckPredictor',
    'PredictiveCEOBriefing',
]
