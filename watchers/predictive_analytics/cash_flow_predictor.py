"""
Cash Flow Prediction Model

Predicts future cash flow (inflows and outflows) based on historical patterns.
Helps identify potential cash shortages and optimize financial planning.
"""

import logging
import joblib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy import stats

from .base import BasePredictiveModel, PredictionConfig, Prediction, ForecastResult

logger = logging.getLogger(__name__)


class CashFlowPredictor(BasePredictiveModel):
    """Predictive model for cash flow forecasting."""

    def __init__(self, vault_path: str):
        """
        Initialize Cash Flow Predictor.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.inflow_model = None
        self.outflow_model = None
        self.inflow_trend = None
        self.outflow_trend = None
        self.inflow_base = None
        self.outflow_base = None
        super().__init__(vault_path, 'cash_flow')

    def train(self, historical_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the cash flow prediction model.

        Args:
            historical_data: List of dicts with 'timestamp', 'inflow', 'outflow'
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        # Validate data
        if not historical_data:
            raise ValueError("No historical data provided")

        if len(historical_data) < 10:
            raise ValueError(f"Need at least 10 data points, got {len(historical_data)}")

        # Sort by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x['timestamp'])

        # Extract inflows and outflows
        inflows = np.array([item.get('inflow', 0) for item in sorted_data])
        outflows = np.array([item.get('outflow', 0) for item in sorted_data])
        n = len(sorted_data)

        # Train inflow model (linear trend)
        x = np.arange(n)
        inflow_slope, inflow_intercept, inflow_r, _, _ = stats.linregress(x, inflows)
        self.inflow_trend = inflow_slope
        self.inflow_base = inflow_intercept

        # Train outflow model (linear trend)
        outflow_slope, outflow_intercept, outflow_r, _, _ = stats.linregress(x, outflows)
        self.outflow_trend = outflow_slope
        self.outflow_base = outflow_intercept

        # Calculate net cash flow
        net_flow = inflows - outflows

        # Calculate metrics
        inflow_predictions = self.inflow_base + self.inflow_trend * x
        outflow_predictions = self.outflow_base + self.outflow_trend * x
        net_predictions = inflow_predictions - outflow_predictions

        inflow_rmse = np.sqrt(np.mean((inflows - inflow_predictions) ** 2))
        outflow_rmse = np.sqrt(np.mean((outflows - outflow_predictions) ** 2))
        net_rmse = np.sqrt(np.mean((net_flow - net_predictions) ** 2))

        # Update config
        self.config = PredictionConfig(
            model_name='cash_flow_predictor',
            model_version='1.0',
            prediction_type='time_series',
            created_at=datetime.now().isoformat(),
            last_trained=datetime.now().isoformat(),
            training_samples=len(historical_data),
            forecast_horizon=kwargs.get('forecast_horizon', 30),
            metrics={
                'inflow_rmse': float(inflow_rmse),
                'outflow_rmse': float(outflow_rmse),
                'net_flow_rmse': float(net_rmse),
                'inflow_r_squared': float(inflow_r ** 2),
                'outflow_r_squared': float(outflow_r ** 2)
            },
            hyperparameters={
                'inflow_trend': float(self.inflow_trend),
                'inflow_base': float(self.inflow_base),
                'outflow_trend': float(self.outflow_trend),
                'outflow_base': float(self.outflow_base)
            }
        )

        self.is_trained = True
        self.historical_data = sorted_data
        self._save_model()
        self.save_config()
        self.save_historical_data(sorted_data)

        logger.info(f"Cash flow predictor trained: Net RMSE={net_rmse:.2f}")

        return {
            'inflow_rmse': inflow_rmse,
            'outflow_rmse': outflow_rmse,
            'net_flow_rmse': net_rmse,
            'inflow_r_squared': inflow_r ** 2,
            'outflow_r_squared': outflow_r ** 2,
            'training_samples': len(historical_data)
        }

    def predict(self, forecast_horizon: int = 30, **kwargs) -> ForecastResult:
        """
        Predict future cash flow.

        Args:
            forecast_horizon: Number of days to forecast
            **kwargs: Additional prediction parameters

        Returns:
            ForecastResult with cash flow predictions
        """
        if not self.is_trained:
            raise ValueError("Model is not trained")

        # Get starting point
        if self.historical_data:
            last_timestamp = datetime.fromisoformat(self.historical_data[-1]['timestamp'])
            start_date = last_timestamp + timedelta(days=1)
            n_historical = len(self.historical_data)
        else:
            start_date = datetime.now()
            n_historical = 0

        # Generate predictions
        predictions = []
        for i in range(forecast_horizon):
            time_index = n_historical + i

            # Predict inflow and outflow
            predicted_inflow = max(0, self.inflow_base + self.inflow_trend * time_index)
            predicted_outflow = max(0, self.outflow_base + self.outflow_trend * time_index)
            predicted_net = predicted_inflow - predicted_outflow

            # Calculate confidence intervals
            if self.historical_data:
                inflows = [item.get('inflow', 0) for item in self.historical_data]
                outflows = [item.get('outflow', 0) for item in self.historical_data]
                inflow_std = np.std(inflows)
                outflow_std = np.std(outflows)
                net_std = np.sqrt(inflow_std**2 + outflow_std**2)

                margin = net_std * 1.96
                lower_bound = predicted_net - margin
                upper_bound = predicted_net + margin
            else:
                lower_bound = predicted_net * 0.7
                upper_bound = predicted_net * 1.3

            # Create prediction
            pred_date = start_date + timedelta(days=i)
            prediction = Prediction(
                timestamp=pred_date.isoformat(),
                predicted_value=float(predicted_net),
                lower_bound=float(lower_bound),
                upper_bound=float(upper_bound),
                confidence=0.95,
                metadata={
                    'predicted_inflow': float(predicted_inflow),
                    'predicted_outflow': float(predicted_outflow),
                    'net_cash_flow': float(predicted_net)
                }
            )
            predictions.append(prediction)

        # Create forecast result
        forecast_end = start_date + timedelta(days=forecast_horizon - 1)
        result = ForecastResult(
            model_name='cash_flow_predictor',
            forecast_start=start_date.isoformat(),
            forecast_end=forecast_end.isoformat(),
            predictions=predictions,
            metrics=self.config.metrics if self.config else {},
            metadata={
                'forecast_horizon': forecast_horizon,
                'historical_samples': len(self.historical_data)
            }
        )

        return result

    def _save_model(self) -> None:
        """Save model parameters to disk."""
        if self.inflow_trend is None or self.outflow_trend is None:
            return

        model_data = {
            'inflow_trend': float(self.inflow_trend),
            'inflow_base': float(self.inflow_base),
            'outflow_trend': float(self.outflow_trend),
            'outflow_base': float(self.outflow_base)
        }

        model_path = self.get_model_path('model.pkl')
        joblib.dump(model_data, model_path)
        logger.info(f"Saved cash flow predictor to {self.model_dir}")

    def _load_model(self) -> bool:
        """
        Load model parameters from disk.

        Returns:
            True if loaded successfully, False otherwise
        """
        model_path = self.get_model_path('model.pkl')
        if not model_path.exists():
            return False

        try:
            model_data = joblib.load(model_path)
            self.inflow_trend = model_data['inflow_trend']
            self.inflow_base = model_data['inflow_base']
            self.outflow_trend = model_data['outflow_trend']
            self.outflow_base = model_data['outflow_base']
            self.is_trained = True
            self.load_config()
            self.historical_data = self.load_historical_data()
            logger.info(f"Loaded cash flow predictor from {self.model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading cash flow predictor: {e}")
            return False

    def generate_sample_data(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Generate sample cash flow data for testing.

        Args:
            days: Number of days of data to generate

        Returns:
            List of cash flow data points
        """
        data = []
        base_inflow = 15000
        base_outflow = 12000
        inflow_trend = 150
        outflow_trend = 100

        start_date = datetime.now() - timedelta(days=days)

        for i in range(days):
            date = start_date + timedelta(days=i)

            # Calculate inflow with trend and noise
            inflow = base_inflow + inflow_trend * i + np.random.normal(0, 1000)
            inflow = max(0, inflow)

            # Calculate outflow with trend and noise
            outflow = base_outflow + outflow_trend * i + np.random.normal(0, 800)
            outflow = max(0, outflow)

            data.append({
                'timestamp': date.isoformat(),
                'inflow': float(inflow),
                'outflow': float(outflow)
            })

        return data

    def identify_cash_shortages(self, forecast: ForecastResult, threshold: float = 0) -> List[Dict[str, Any]]:
        """
        Identify periods with predicted cash shortages.

        Args:
            forecast: Forecast result
            threshold: Threshold for cash shortage (default 0)

        Returns:
            List of shortage periods
        """
        shortages = []

        for pred in forecast.predictions:
            if pred.predicted_value < threshold:
                shortages.append({
                    'date': pred.timestamp,
                    'predicted_net_flow': pred.predicted_value,
                    'severity': 'high' if pred.predicted_value < threshold - 5000 else 'medium',
                    'inflow': pred.metadata.get('predicted_inflow', 0),
                    'outflow': pred.metadata.get('predicted_outflow', 0)
                })

        return shortages

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics from historical data.

        Returns:
            Dictionary with statistics
        """
        if not self.historical_data:
            return {}

        inflows = [item.get('inflow', 0) for item in self.historical_data]
        outflows = [item.get('outflow', 0) for item in self.historical_data]
        net_flows = [i - o for i, o in zip(inflows, outflows)]

        return {
            'total_inflow': float(np.sum(inflows)),
            'total_outflow': float(np.sum(outflows)),
            'net_cash_flow': float(np.sum(net_flows)),
            'average_daily_inflow': float(np.mean(inflows)),
            'average_daily_outflow': float(np.mean(outflows)),
            'average_daily_net': float(np.mean(net_flows)),
            'inflow_trend_per_day': float(self.inflow_trend) if self.inflow_trend else 0,
            'outflow_trend_per_day': float(self.outflow_trend) if self.outflow_trend else 0,
            'data_points': len(self.historical_data)
        }
