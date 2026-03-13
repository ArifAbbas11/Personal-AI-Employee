"""
Revenue Forecasting Model

Predicts future revenue based on historical data using time-series analysis.
Uses exponential smoothing for trend and seasonality detection.
"""

import logging
import joblib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from scipy import stats

from .base import BasePredictiveModel, PredictionConfig, Prediction, ForecastResult

logger = logging.getLogger(__name__)


class RevenueForecaster(BasePredictiveModel):
    """Predictive model for revenue forecasting."""

    def __init__(self, vault_path: str):
        """
        Initialize Revenue Forecaster.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.trend_coefficient = None
        self.seasonal_factors = None
        self.base_level = None
        super().__init__(vault_path, 'revenue')

    def train(self, historical_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the revenue forecasting model.

        Args:
            historical_data: List of dicts with 'timestamp' and 'value' (revenue)
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        # Validate data
        is_valid, error = self.validate_historical_data(historical_data)
        if not is_valid:
            raise ValueError(f"Invalid historical data: {error}")

        # Sort by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x['timestamp'])

        # Extract values
        values = np.array([item['value'] for item in sorted_data])
        n = len(values)

        # Calculate trend using linear regression
        x = np.arange(n)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)

        self.trend_coefficient = slope
        self.base_level = intercept

        # Calculate seasonal factors (simple moving average approach)
        # Assume weekly seasonality (7 days)
        seasonal_period = min(7, n // 2)
        if seasonal_period > 0:
            self.seasonal_factors = []
            for i in range(seasonal_period):
                seasonal_values = values[i::seasonal_period]
                if len(seasonal_values) > 0:
                    self.seasonal_factors.append(np.mean(seasonal_values) / np.mean(values))
                else:
                    self.seasonal_factors.append(1.0)
        else:
            self.seasonal_factors = [1.0]

        # Calculate metrics
        predictions = self._predict_values(n)
        mse = np.mean((values - predictions) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(values - predictions))
        mape = np.mean(np.abs((values - predictions) / (values + 1e-10))) * 100

        # Update config
        self.config = PredictionConfig(
            model_name='revenue_forecaster',
            model_version='1.0',
            prediction_type='time_series',
            created_at=datetime.now().isoformat(),
            last_trained=datetime.now().isoformat(),
            training_samples=len(historical_data),
            forecast_horizon=kwargs.get('forecast_horizon', 30),
            metrics={
                'rmse': float(rmse),
                'mae': float(mae),
                'mape': float(mape),
                'r_squared': float(r_value ** 2)
            },
            hyperparameters={
                'trend_coefficient': float(self.trend_coefficient),
                'base_level': float(self.base_level),
                'seasonal_period': seasonal_period
            }
        )

        self.is_trained = True
        self.historical_data = sorted_data
        self._save_model()
        self.save_config()
        self.save_historical_data(sorted_data)

        logger.info(f"Revenue forecaster trained: RMSE={rmse:.2f}, MAPE={mape:.2f}%")

        return {
            'rmse': rmse,
            'mae': mae,
            'mape': mape,
            'r_squared': r_value ** 2,
            'training_samples': len(historical_data)
        }

    def _predict_values(self, n: int) -> np.ndarray:
        """
        Predict values for n time steps.

        Args:
            n: Number of time steps

        Returns:
            Array of predicted values
        """
        predictions = []
        for i in range(n):
            # Trend component
            trend_value = self.base_level + self.trend_coefficient * i

            # Seasonal component
            seasonal_idx = i % len(self.seasonal_factors)
            seasonal_factor = self.seasonal_factors[seasonal_idx]

            # Combined prediction
            prediction = trend_value * seasonal_factor
            predictions.append(max(0, prediction))  # Revenue can't be negative

        return np.array(predictions)

    def predict(self, forecast_horizon: int = 30, **kwargs) -> ForecastResult:
        """
        Forecast future revenue.

        Args:
            forecast_horizon: Number of days to forecast
            **kwargs: Additional prediction parameters

        Returns:
            ForecastResult with revenue predictions
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
            # Calculate prediction
            time_index = n_historical + i
            trend_value = self.base_level + self.trend_coefficient * time_index
            seasonal_idx = time_index % len(self.seasonal_factors)
            seasonal_factor = self.seasonal_factors[seasonal_idx]
            predicted_value = max(0, trend_value * seasonal_factor)

            # Calculate confidence interval (simple approach)
            # Use historical variance
            if self.historical_data:
                historical_values = [item['value'] for item in self.historical_data]
                std = np.std(historical_values)
                margin = std * 1.96  # 95% confidence
                lower_bound = max(0, predicted_value - margin)
                upper_bound = predicted_value + margin
            else:
                lower_bound = predicted_value * 0.8
                upper_bound = predicted_value * 1.2

            # Create prediction
            pred_date = start_date + timedelta(days=i)
            prediction = Prediction(
                timestamp=pred_date.isoformat(),
                predicted_value=float(predicted_value),
                lower_bound=float(lower_bound),
                upper_bound=float(upper_bound),
                confidence=0.95,
                metadata={
                    'trend_component': float(trend_value),
                    'seasonal_factor': float(seasonal_factor)
                }
            )
            predictions.append(prediction)

        # Create forecast result
        forecast_end = start_date + timedelta(days=forecast_horizon - 1)
        result = ForecastResult(
            model_name='revenue_forecaster',
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
        if self.trend_coefficient is None or self.base_level is None:
            return

        model_data = {
            'trend_coefficient': float(self.trend_coefficient),
            'base_level': float(self.base_level),
            'seasonal_factors': [float(f) for f in self.seasonal_factors]
        }

        model_path = self.get_model_path('model.pkl')
        joblib.dump(model_data, model_path)
        logger.info(f"Saved revenue forecaster to {self.model_dir}")

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
            self.trend_coefficient = model_data['trend_coefficient']
            self.base_level = model_data['base_level']
            self.seasonal_factors = model_data['seasonal_factors']
            self.is_trained = True
            self.load_config()
            self.historical_data = self.load_historical_data()
            logger.info(f"Loaded revenue forecaster from {self.model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading revenue forecaster: {e}")
            return False

    def generate_sample_data(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Generate sample revenue data for testing.

        Args:
            days: Number of days of data to generate

        Returns:
            List of revenue data points
        """
        data = []
        base_revenue = 10000
        trend = 100  # $100 increase per day

        start_date = datetime.now() - timedelta(days=days)

        for i in range(days):
            date = start_date + timedelta(days=i)

            # Add trend
            trend_component = base_revenue + trend * i

            # Add weekly seasonality (higher on weekdays)
            day_of_week = date.weekday()
            if day_of_week < 5:  # Weekday
                seasonal_factor = 1.2
            else:  # Weekend
                seasonal_factor = 0.8

            # Add random noise
            noise = np.random.normal(0, 500)

            revenue = max(0, trend_component * seasonal_factor + noise)

            data.append({
                'timestamp': date.isoformat(),
                'value': float(revenue)
            })

        return data

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics from historical data.

        Returns:
            Dictionary with statistics
        """
        if not self.historical_data:
            return {}

        values = [item['value'] for item in self.historical_data]

        return {
            'total_revenue': float(np.sum(values)),
            'average_daily_revenue': float(np.mean(values)),
            'median_revenue': float(np.median(values)),
            'std_deviation': float(np.std(values)),
            'min_revenue': float(np.min(values)),
            'max_revenue': float(np.max(values)),
            'trend_per_day': float(self.trend_coefficient) if self.trend_coefficient else 0,
            'data_points': len(values)
        }
