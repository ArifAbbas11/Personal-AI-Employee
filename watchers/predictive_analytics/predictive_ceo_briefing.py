"""
Predictive CEO Briefing

Generates forward-looking CEO briefings with predictions and forecasts.
Integrates all predictive analytics models for comprehensive insights.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from .revenue_forecaster import RevenueForecaster
from .cash_flow_predictor import CashFlowPredictor
from .churn_predictor import ChurnPredictor
from .bottleneck_predictor import BottleneckPredictor

logger = logging.getLogger(__name__)


class PredictiveCEOBriefing:
    """Generates predictive CEO briefings with forecasts and insights."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize Predictive CEO Briefing.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = Path(vault_path)

        # Initialize predictive models
        self.revenue_forecaster = RevenueForecaster(str(vault_path))
        self.cash_flow_predictor = CashFlowPredictor(str(vault_path))
        self.churn_predictor = ChurnPredictor(str(vault_path))
        self.bottleneck_predictor = BottleneckPredictor(str(vault_path))

    def generate_briefing(
        self,
        forecast_days: int = 30,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive predictive CEO briefing.

        Args:
            forecast_days: Number of days to forecast
            include_recommendations: Whether to include recommendations

        Returns:
            Dictionary with briefing content
        """
        briefing = {
            'generated_at': datetime.now().isoformat(),
            'forecast_period': f'{forecast_days} days',
            'sections': {}
        }

        # Revenue Forecast
        if self.revenue_forecaster.is_trained:
            briefing['sections']['revenue_forecast'] = self._generate_revenue_section(forecast_days)
        else:
            briefing['sections']['revenue_forecast'] = {
                'status': 'not_available',
                'message': 'Revenue forecasting model not trained'
            }

        # Cash Flow Prediction
        if self.cash_flow_predictor.is_trained:
            briefing['sections']['cash_flow_prediction'] = self._generate_cash_flow_section(forecast_days)
        else:
            briefing['sections']['cash_flow_prediction'] = {
                'status': 'not_available',
                'message': 'Cash flow prediction model not trained'
            }

        # Client Churn Risk
        if self.churn_predictor.is_trained:
            briefing['sections']['churn_risk'] = self._generate_churn_section()
        else:
            briefing['sections']['churn_risk'] = {
                'status': 'not_available',
                'message': 'Churn prediction model not trained'
            }

        # Workflow Bottlenecks
        if self.bottleneck_predictor.is_trained:
            briefing['sections']['bottleneck_analysis'] = self._generate_bottleneck_section()
        else:
            briefing['sections']['bottleneck_analysis'] = {
                'status': 'not_available',
                'message': 'Bottleneck prediction model not trained'
            }

        # Executive Summary
        briefing['executive_summary'] = self._generate_executive_summary(briefing['sections'])

        # Strategic Recommendations
        if include_recommendations:
            briefing['strategic_recommendations'] = self._generate_strategic_recommendations(briefing['sections'])

        return briefing

    def _generate_revenue_section(self, forecast_days: int) -> Dict[str, Any]:
        """Generate revenue forecast section."""
        try:
            forecast = self.revenue_forecaster.predict(forecast_days)
            stats = self.revenue_forecaster.get_summary_statistics()

            # Calculate key metrics
            total_forecast = sum(p.predicted_value for p in forecast.predictions)
            avg_daily = total_forecast / forecast_days if forecast_days > 0 else 0

            # Get trend
            if len(forecast.predictions) >= 2:
                first_week = sum(p.predicted_value for p in forecast.predictions[:7]) / 7
                last_week = sum(p.predicted_value for p in forecast.predictions[-7:]) / 7
                trend = ((last_week - first_week) / first_week * 100) if first_week > 0 else 0
            else:
                trend = 0

            return {
                'status': 'available',
                'forecast_period': f'{forecast_days} days',
                'total_forecast_revenue': total_forecast,
                'average_daily_revenue': avg_daily,
                'trend_percentage': trend,
                'historical_average': stats.get('average_daily_revenue', 0),
                'confidence_interval': '95%',
                'predictions': [
                    {
                        'date': p.timestamp,
                        'value': p.predicted_value,
                        'lower_bound': p.lower_bound,
                        'upper_bound': p.upper_bound
                    }
                    for p in forecast.predictions[:7]  # First week
                ],
                'insights': self._generate_revenue_insights(forecast, stats, trend)
            }
        except Exception as e:
            logger.error(f"Error generating revenue section: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _generate_cash_flow_section(self, forecast_days: int) -> Dict[str, Any]:
        """Generate cash flow prediction section."""
        try:
            forecast = self.cash_flow_predictor.predict(forecast_days)
            stats = self.cash_flow_predictor.get_summary_statistics()
            shortages = self.cash_flow_predictor.identify_cash_shortages(forecast)

            # Calculate key metrics
            total_net_flow = sum(p.predicted_value for p in forecast.predictions)
            avg_daily_net = total_net_flow / forecast_days if forecast_days > 0 else 0

            return {
                'status': 'available',
                'forecast_period': f'{forecast_days} days',
                'total_net_cash_flow': total_net_flow,
                'average_daily_net_flow': avg_daily_net,
                'historical_average_net': stats.get('average_daily_net', 0),
                'cash_shortages_detected': len(shortages),
                'shortages': shortages[:5],  # Top 5
                'predictions': [
                    {
                        'date': p.timestamp,
                        'net_flow': p.predicted_value,
                        'inflow': p.metadata.get('predicted_inflow', 0),
                        'outflow': p.metadata.get('predicted_outflow', 0)
                    }
                    for p in forecast.predictions[:7]  # First week
                ],
                'insights': self._generate_cash_flow_insights(forecast, stats, shortages)
            }
        except Exception as e:
            logger.error(f"Error generating cash flow section: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _generate_churn_section(self) -> Dict[str, Any]:
        """Generate churn risk section."""
        try:
            # Note: In production, this would analyze actual client data
            # For now, we'll return a placeholder structure
            return {
                'status': 'available',
                'message': 'Churn prediction model trained and ready',
                'model_metrics': self.churn_predictor.get_metrics(),
                'insights': [
                    'Churn prediction model is operational',
                    'Use predict() method with client data to identify at-risk clients',
                    'Model considers engagement, payment history, and support interactions'
                ]
            }
        except Exception as e:
            logger.error(f"Error generating churn section: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _generate_bottleneck_section(self) -> Dict[str, Any]:
        """Generate bottleneck analysis section."""
        try:
            # Note: In production, this would analyze actual task data
            # For now, we'll return a placeholder structure
            return {
                'status': 'available',
                'message': 'Bottleneck prediction model trained and ready',
                'model_metrics': self.bottleneck_predictor.get_metrics(),
                'insights': [
                    'Bottleneck prediction model is operational',
                    'Use analyze_workflow() method with task data to identify bottlenecks',
                    'Model considers dependencies, team size, and task complexity'
                ]
            }
        except Exception as e:
            logger.error(f"Error generating bottleneck section: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _generate_revenue_insights(self, forecast: Any, stats: Dict[str, Any], trend: float) -> List[str]:
        """Generate revenue insights."""
        insights = []

        if trend > 10:
            insights.append(f"Strong upward revenue trend: {trend:.1f}% growth expected")
        elif trend < -10:
            insights.append(f"Concerning downward trend: {trend:.1f}% decline expected")
        else:
            insights.append(f"Stable revenue trend: {trend:.1f}% change expected")

        historical_avg = stats.get('average_daily_revenue', 0)
        forecast_avg = sum(p.predicted_value for p in forecast.predictions) / len(forecast.predictions)

        if forecast_avg > historical_avg * 1.1:
            insights.append(f"Forecast exceeds historical average by {((forecast_avg / historical_avg - 1) * 100):.1f}%")
        elif forecast_avg < historical_avg * 0.9:
            insights.append(f"Forecast below historical average by {((1 - forecast_avg / historical_avg) * 100):.1f}%")

        return insights

    def _generate_cash_flow_insights(self, forecast: Any, stats: Dict[str, Any], shortages: List[Dict[str, Any]]) -> List[str]:
        """Generate cash flow insights."""
        insights = []

        if shortages:
            insights.append(f"⚠️ {len(shortages)} potential cash shortages detected in forecast period")
            if shortages[0]['severity'] == 'high':
                insights.append("Critical: First shortage is high severity - immediate action required")

        total_net = sum(p.predicted_value for p in forecast.predictions)
        if total_net < 0:
            insights.append(f"⚠️ Negative net cash flow expected: ${abs(total_net):,.2f}")
        else:
            insights.append(f"✓ Positive net cash flow expected: ${total_net:,.2f}")

        return insights

    def _generate_executive_summary(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary from all sections."""
        summary = {
            'key_metrics': {},
            'alerts': [],
            'opportunities': []
        }

        # Revenue summary
        if sections.get('revenue_forecast', {}).get('status') == 'available':
            rev_section = sections['revenue_forecast']
            summary['key_metrics']['revenue_forecast'] = {
                'total': rev_section.get('total_forecast_revenue', 0),
                'trend': rev_section.get('trend_percentage', 0)
            }
            if rev_section.get('trend_percentage', 0) < -10:
                summary['alerts'].append('Revenue declining - review sales strategy')
            elif rev_section.get('trend_percentage', 0) > 15:
                summary['opportunities'].append('Strong revenue growth - consider scaling operations')

        # Cash flow summary
        if sections.get('cash_flow_prediction', {}).get('status') == 'available':
            cf_section = sections['cash_flow_prediction']
            summary['key_metrics']['cash_flow'] = {
                'net_flow': cf_section.get('total_net_cash_flow', 0),
                'shortages': cf_section.get('cash_shortages_detected', 0)
            }
            if cf_section.get('cash_shortages_detected', 0) > 0:
                summary['alerts'].append(f"{cf_section['cash_shortages_detected']} cash shortages predicted")

        return summary

    def _generate_strategic_recommendations(self, sections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate strategic recommendations."""
        recommendations = []

        # Revenue recommendations
        if sections.get('revenue_forecast', {}).get('status') == 'available':
            trend = sections['revenue_forecast'].get('trend_percentage', 0)
            if trend < -5:
                recommendations.append({
                    'category': 'Revenue',
                    'priority': 'high',
                    'recommendation': 'Implement revenue recovery plan - focus on customer retention and upselling',
                    'expected_impact': 'Stabilize revenue trend'
                })

        # Cash flow recommendations
        if sections.get('cash_flow_prediction', {}).get('status') == 'available':
            shortages = sections['cash_flow_prediction'].get('cash_shortages_detected', 0)
            if shortages > 0:
                recommendations.append({
                    'category': 'Cash Flow',
                    'priority': 'critical',
                    'recommendation': 'Secure additional credit line or accelerate receivables collection',
                    'expected_impact': 'Prevent cash shortages'
                })

        return recommendations

    def save_briefing(self, briefing: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """
        Save briefing to file.

        Args:
            briefing: Briefing data
            filename: Optional filename (default: predictive_briefing_YYYY-MM-DD.json)

        Returns:
            Path to saved file
        """
        if filename is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f'predictive_briefing_{date_str}.json'

        output_path = self.vault_path / 'Reports' / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(briefing, f, indent=2)

        logger.info(f"Saved predictive briefing to {output_path}")
        return output_path


def main():
    """Main function for generating predictive CEO briefing."""
    import argparse

    parser = argparse.ArgumentParser(description='Predictive CEO Briefing Generator')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--forecast-days', type=int, default=30, help='Number of days to forecast')
    parser.add_argument('--output', type=str, help='Output file path')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Generate briefing
    briefing_gen = PredictiveCEOBriefing(args.vault_path)
    briefing = briefing_gen.generate_briefing(forecast_days=args.forecast_days)

    # Save briefing
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(briefing, f, indent=2)
        print(f"Briefing saved to: {output_path}")
    else:
        output_path = briefing_gen.save_briefing(briefing)
        print(f"Briefing saved to: {output_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("PREDICTIVE CEO BRIEFING SUMMARY")
    print("=" * 80)
    print(f"Generated: {briefing['generated_at']}")
    print(f"Forecast Period: {briefing['forecast_period']}")
    print("\nSections Available:")
    for section_name, section_data in briefing['sections'].items():
        status = section_data.get('status', 'unknown')
        print(f"  - {section_name}: {status}")

    if 'executive_summary' in briefing:
        print("\nExecutive Summary:")
        summary = briefing['executive_summary']
        if summary.get('alerts'):
            print(f"  Alerts: {len(summary['alerts'])}")
            for alert in summary['alerts']:
                print(f"    ⚠️  {alert}")
        if summary.get('opportunities'):
            print(f"  Opportunities: {len(summary['opportunities'])}")
            for opp in summary['opportunities']:
                print(f"    ✓ {opp}")


if __name__ == '__main__':
    main()
