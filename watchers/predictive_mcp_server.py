"""
Predictive Analytics MCP Server

Model-Context-Protocol server for predictive analytics capabilities.
Exposes forecasting and prediction models as tools for Claude Code integration.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .predictive_analytics.revenue_forecaster import RevenueForecaster
from .predictive_analytics.cash_flow_predictor import CashFlowPredictor
from .predictive_analytics.churn_predictor import ChurnPredictor
from .predictive_analytics.bottleneck_predictor import BottleneckPredictor
from .predictive_analytics.predictive_ceo_briefing import PredictiveCEOBriefing

logger = logging.getLogger(__name__)


class PredictiveAnalyticsMCPServer:
    """MCP Server for predictive analytics capabilities."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize Predictive Analytics MCP Server.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = Path(vault_path)

        # Initialize models
        self.revenue_forecaster = RevenueForecaster(str(vault_path))
        self.cash_flow_predictor = CashFlowPredictor(str(vault_path))
        self.churn_predictor = ChurnPredictor(str(vault_path))
        self.bottleneck_predictor = BottleneckPredictor(str(vault_path))
        self.briefing_generator = PredictiveCEOBriefing(str(vault_path))

        logger.info("Predictive Analytics MCP Server initialized")

    # Tool 1: Forecast Revenue
    def forecast_revenue(self, forecast_days: int = 30) -> Dict[str, Any]:
        """
        Forecast future revenue.

        Args:
            forecast_days: Number of days to forecast

        Returns:
            Dictionary with revenue forecast
        """
        try:
            if not self.revenue_forecaster.is_trained:
                return {
                    'success': False,
                    'error': 'Revenue forecasting model not trained',
                    'message': 'Train the model first using train_revenue_model'
                }

            forecast = self.revenue_forecaster.predict(forecast_days)
            stats = self.revenue_forecaster.get_summary_statistics()

            # Calculate summary metrics
            total_forecast = sum(p.predicted_value for p in forecast.predictions)
            avg_daily = total_forecast / forecast_days if forecast_days > 0 else 0

            return {
                'success': True,
                'forecast_period': f'{forecast_days} days',
                'total_forecast_revenue': total_forecast,
                'average_daily_revenue': avg_daily,
                'historical_average': stats.get('average_daily_revenue', 0),
                'predictions': [
                    {
                        'date': p.timestamp,
                        'value': p.predicted_value,
                        'lower_bound': p.lower_bound,
                        'upper_bound': p.upper_bound
                    }
                    for p in forecast.predictions[:7]  # First week
                ],
                'model_metrics': self.revenue_forecaster.get_metrics()
            }
        except Exception as e:
            logger.error(f"Error forecasting revenue: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 2: Predict Cash Flow
    def predict_cash_flow(self, forecast_days: int = 30) -> Dict[str, Any]:
        """
        Predict future cash flow.

        Args:
            forecast_days: Number of days to forecast

        Returns:
            Dictionary with cash flow prediction
        """
        try:
            if not self.cash_flow_predictor.is_trained:
                return {
                    'success': False,
                    'error': 'Cash flow prediction model not trained',
                    'message': 'Train the model first using train_cash_flow_model'
                }

            forecast = self.cash_flow_predictor.predict(forecast_days)
            stats = self.cash_flow_predictor.get_summary_statistics()
            shortages = self.cash_flow_predictor.identify_cash_shortages(forecast)

            total_net = sum(p.predicted_value for p in forecast.predictions)
            avg_daily_net = total_net / forecast_days if forecast_days > 0 else 0

            return {
                'success': True,
                'forecast_period': f'{forecast_days} days',
                'total_net_cash_flow': total_net,
                'average_daily_net_flow': avg_daily_net,
                'historical_average_net': stats.get('average_daily_net', 0),
                'cash_shortages_detected': len(shortages),
                'shortages': shortages[:5],
                'predictions': [
                    {
                        'date': p.timestamp,
                        'net_flow': p.predicted_value,
                        'inflow': p.metadata.get('predicted_inflow', 0),
                        'outflow': p.metadata.get('predicted_outflow', 0)
                    }
                    for p in forecast.predictions[:7]
                ],
                'model_metrics': self.cash_flow_predictor.get_metrics()
            }
        except Exception as e:
            logger.error(f"Error predicting cash flow: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 3: Predict Client Churn
    def predict_churn(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict client churn probability.

        Args:
            client_data: Client information dictionary

        Returns:
            Dictionary with churn prediction
        """
        try:
            if not self.churn_predictor.is_trained:
                return {
                    'success': False,
                    'error': 'Churn prediction model not trained',
                    'message': 'Train the model first using train_churn_model'
                }

            prediction = self.churn_predictor.predict(client_data)

            return {
                'success': True,
                'client_id': client_data.get('client_id', 'unknown'),
                'churn_probability': prediction.get('churn_probability', 0),
                'will_churn': prediction.get('will_churn', False),
                'risk_level': prediction.get('risk_level', 'unknown'),
                'top_risk_factors': prediction.get('top_risk_factors', []),
                'model_version': prediction.get('model_version', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 4: Predict Task Bottlenecks
    def predict_bottleneck(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict if a task will become a bottleneck.

        Args:
            task_data: Task information dictionary

        Returns:
            Dictionary with bottleneck prediction
        """
        try:
            if not self.bottleneck_predictor.is_trained:
                return {
                    'success': False,
                    'error': 'Bottleneck prediction model not trained',
                    'message': 'Train the model first using train_bottleneck_model'
                }

            prediction = self.bottleneck_predictor.predict(task_data)

            return {
                'success': True,
                'task_id': task_data.get('task_id', 'unknown'),
                'bottleneck_probability': prediction.get('bottleneck_probability', 0),
                'is_bottleneck': prediction.get('is_bottleneck', False),
                'risk_level': prediction.get('risk_level', 'unknown'),
                'contributing_factors': prediction.get('contributing_factors', []),
                'recommendations': prediction.get('recommendations', []),
                'model_version': prediction.get('model_version', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error predicting bottleneck: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 5: Generate Predictive CEO Briefing
    def generate_predictive_briefing(self, forecast_days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive predictive CEO briefing.

        Args:
            forecast_days: Number of days to forecast

        Returns:
            Dictionary with briefing content
        """
        try:
            briefing = self.briefing_generator.generate_briefing(forecast_days)

            return {
                'success': True,
                'briefing': briefing,
                'message': 'Predictive briefing generated successfully'
            }
        except Exception as e:
            logger.error(f"Error generating predictive briefing: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 6: Train Revenue Model
    def train_revenue_model(self, use_sample_data: bool = True) -> Dict[str, Any]:
        """
        Train revenue forecasting model.

        Args:
            use_sample_data: Whether to use sample data for training

        Returns:
            Dictionary with training results
        """
        try:
            if use_sample_data:
                training_data = self.revenue_forecaster.generate_sample_data(90)
            else:
                # In production, load real data
                training_data = self.revenue_forecaster.load_historical_data()
                if not training_data:
                    return {
                        'success': False,
                        'error': 'No historical data available',
                        'message': 'Use sample data or provide historical data'
                    }

            metrics = self.revenue_forecaster.train(training_data)

            return {
                'success': True,
                'model': 'revenue_forecaster',
                'metrics': metrics,
                'message': 'Revenue forecasting model trained successfully'
            }
        except Exception as e:
            logger.error(f"Error training revenue model: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 7: Train Cash Flow Model
    def train_cash_flow_model(self, use_sample_data: bool = True) -> Dict[str, Any]:
        """
        Train cash flow prediction model.

        Args:
            use_sample_data: Whether to use sample data for training

        Returns:
            Dictionary with training results
        """
        try:
            if use_sample_data:
                training_data = self.cash_flow_predictor.generate_sample_data(90)
            else:
                training_data = self.cash_flow_predictor.load_historical_data()
                if not training_data:
                    return {
                        'success': False,
                        'error': 'No historical data available'
                    }

            metrics = self.cash_flow_predictor.train(training_data)

            return {
                'success': True,
                'model': 'cash_flow_predictor',
                'metrics': metrics,
                'message': 'Cash flow prediction model trained successfully'
            }
        except Exception as e:
            logger.error(f"Error training cash flow model: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 8: Train Churn Model
    def train_churn_model(self, use_sample_data: bool = True) -> Dict[str, Any]:
        """
        Train churn prediction model.

        Args:
            use_sample_data: Whether to use sample data for training

        Returns:
            Dictionary with training results
        """
        try:
            if use_sample_data:
                training_data = self.churn_predictor.generate_sample_data(100)
            else:
                training_data = self.churn_predictor.load_historical_data()
                if not training_data:
                    return {
                        'success': False,
                        'error': 'No historical data available'
                    }

            metrics = self.churn_predictor.train(training_data)

            return {
                'success': True,
                'model': 'churn_predictor',
                'metrics': metrics,
                'message': 'Churn prediction model trained successfully'
            }
        except Exception as e:
            logger.error(f"Error training churn model: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 9: Train Bottleneck Model
    def train_bottleneck_model(self, use_sample_data: bool = True) -> Dict[str, Any]:
        """
        Train bottleneck prediction model.

        Args:
            use_sample_data: Whether to use sample data for training

        Returns:
            Dictionary with training results
        """
        try:
            if use_sample_data:
                training_data = self.bottleneck_predictor.generate_sample_data(100)
            else:
                training_data = self.bottleneck_predictor.load_historical_data()
                if not training_data:
                    return {
                        'success': False,
                        'error': 'No historical data available'
                    }

            metrics = self.bottleneck_predictor.train(training_data)

            return {
                'success': True,
                'model': 'bottleneck_predictor',
                'metrics': metrics,
                'message': 'Bottleneck prediction model trained successfully'
            }
        except Exception as e:
            logger.error(f"Error training bottleneck model: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 10: Get Predictive Analytics Status
    def get_predictive_status(self) -> Dict[str, Any]:
        """
        Get status of all predictive analytics models.

        Returns:
            Dictionary with system status
        """
        try:
            models_status = {
                'revenue_forecaster': {
                    'trained': self.revenue_forecaster.is_trained,
                    'metrics': self.revenue_forecaster.get_metrics()
                },
                'cash_flow_predictor': {
                    'trained': self.cash_flow_predictor.is_trained,
                    'metrics': self.cash_flow_predictor.get_metrics()
                },
                'churn_predictor': {
                    'trained': self.churn_predictor.is_trained,
                    'metrics': self.churn_predictor.get_metrics()
                },
                'bottleneck_predictor': {
                    'trained': self.bottleneck_predictor.is_trained,
                    'metrics': self.bottleneck_predictor.get_metrics()
                }
            }

            total_models = len(models_status)
            trained_models = sum(1 for m in models_status.values() if m['trained'])

            return {
                'success': True,
                'total_models': total_models,
                'trained_models': trained_models,
                'training_percentage': (trained_models / total_models * 100) if total_models > 0 else 0,
                'models': models_status
            }
        except Exception as e:
            logger.error(f"Error getting predictive status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available predictive analytics tools.

        Returns:
            List of tool definitions
        """
        return [
            {
                'name': 'forecast_revenue',
                'description': 'Forecast future revenue based on historical patterns',
                'parameters': ['forecast_days (optional, default 30)']
            },
            {
                'name': 'predict_cash_flow',
                'description': 'Predict future cash flow (inflows and outflows)',
                'parameters': ['forecast_days (optional, default 30)']
            },
            {
                'name': 'predict_churn',
                'description': 'Predict client churn probability',
                'parameters': ['client_data (dict with client information)']
            },
            {
                'name': 'predict_bottleneck',
                'description': 'Predict if a task will become a bottleneck',
                'parameters': ['task_data (dict with task information)']
            },
            {
                'name': 'generate_predictive_briefing',
                'description': 'Generate comprehensive predictive CEO briefing',
                'parameters': ['forecast_days (optional, default 30)']
            },
            {
                'name': 'train_revenue_model',
                'description': 'Train revenue forecasting model',
                'parameters': ['use_sample_data (optional, default True)']
            },
            {
                'name': 'train_cash_flow_model',
                'description': 'Train cash flow prediction model',
                'parameters': ['use_sample_data (optional, default True)']
            },
            {
                'name': 'train_churn_model',
                'description': 'Train churn prediction model',
                'parameters': ['use_sample_data (optional, default True)']
            },
            {
                'name': 'train_bottleneck_model',
                'description': 'Train bottleneck prediction model',
                'parameters': ['use_sample_data (optional, default True)']
            },
            {
                'name': 'get_predictive_status',
                'description': 'Get status of all predictive analytics models',
                'parameters': []
            }
        ]


def main():
    """Main function for testing MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description='Predictive Analytics MCP Server')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test predictions')
    parser.add_argument('--train-all', action='store_true', help='Train all models')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize server
    server = PredictiveAnalyticsMCPServer(args.vault_path)

    if args.train_all:
        print("Training all predictive models...")
        print("\n1. Training revenue forecaster...")
        result = server.train_revenue_model()
        print(json.dumps(result, indent=2))

        print("\n2. Training cash flow predictor...")
        result = server.train_cash_flow_model()
        print(json.dumps(result, indent=2))

        print("\n3. Training churn predictor...")
        result = server.train_churn_model()
        print(json.dumps(result, indent=2))

        print("\n4. Training bottleneck predictor...")
        result = server.train_bottleneck_model()
        print(json.dumps(result, indent=2))

        print("\n5. Getting system status...")
        result = server.get_predictive_status()
        print(json.dumps(result, indent=2))

    elif args.test:
        print("Testing Predictive Analytics MCP Server...")

        print("\n1. Getting system status...")
        result = server.get_predictive_status()
        print(json.dumps(result, indent=2))

        if result.get('trained_models', 0) > 0:
            print("\n2. Forecasting revenue...")
            result = server.forecast_revenue(30)
            print(json.dumps(result, indent=2))

            print("\n3. Predicting cash flow...")
            result = server.predict_cash_flow(30)
            print(json.dumps(result, indent=2))

            print("\n4. Generating predictive briefing...")
            result = server.generate_predictive_briefing(30)
            print(json.dumps(result, indent=2))
        else:
            print("\nNo models trained. Run with --train-all first.")

    else:
        print("Predictive Analytics MCP Server initialized")
        print("\nAvailable tools:")
        for tool in server.get_available_tools():
            print(f"  - {tool['name']}: {tool['description']}")


if __name__ == '__main__':
    main()
