"""
Content Optimization Model

Analyzes and optimizes social media content for engagement.
Predicts engagement score and provides optimization suggestions.
Uses regression for engagement prediction and feature importance analysis.
"""

import logging
import joblib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np

from .base import BaseMLModel, MLModelConfig

logger = logging.getLogger(__name__)


class ContentOptimizer(BaseMLModel):
    """ML model for content optimization and engagement prediction."""

    def __init__(self, vault_path: str):
        """
        Initialize Content Optimizer.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vectorizer = None
        super().__init__(vault_path, 'content_optimizer')

    def _extract_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from content data.

        Args:
            content_data: Content information

        Returns:
            Dictionary of extracted features
        """
        text = content_data.get('text', '')

        # Text features
        word_count = len(text.split())
        char_count = len(text)
        has_hashtags = 1 if '#' in text else 0
        hashtag_count = text.count('#')
        has_mentions = 1 if '@' in text else 0
        mention_count = text.count('@')
        has_url = 1 if 'http' in text.lower() else 0
        has_emoji = 1 if any(ord(c) > 127 for c in text) else 0
        has_question = 1 if '?' in text else 0
        has_exclamation = 1 if '!' in text else 0

        # Timing features
        hour = content_data.get('post_hour', 12)
        is_weekend = 1 if content_data.get('is_weekend', False) else 0

        # Media features
        has_image = 1 if content_data.get('has_image', False) else 0
        has_video = 1 if content_data.get('has_video', False) else 0

        # Platform
        platform = content_data.get('platform', 'facebook')

        features = {
            'text': text,
            'word_count': word_count,
            'char_count': char_count,
            'has_hashtags': has_hashtags,
            'hashtag_count': hashtag_count,
            'has_mentions': has_mentions,
            'mention_count': mention_count,
            'has_url': has_url,
            'has_emoji': has_emoji,
            'has_question': has_question,
            'has_exclamation': has_exclamation,
            'hour': hour,
            'is_weekend': is_weekend,
            'has_image': has_image,
            'has_video': has_video,
            'platform_facebook': 1 if platform == 'facebook' else 0,
            'platform_twitter': 1 if platform == 'twitter' else 0,
            'platform_linkedin': 1 if platform == 'linkedin' else 0,
            'platform_instagram': 1 if platform == 'instagram' else 0,
        }
        return features

    def train(self, training_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the content optimizer.

        Args:
            training_data: List of dicts with content info and 'engagement_score' label
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        if len(training_data) < 20:
            raise ValueError("Need at least 20 training examples")

        # Extract features
        texts = []
        numeric_features = []
        labels = []

        for item in training_data:
            features = self._extract_features(item)
            texts.append(features['text'])
            numeric_features.append([
                features['word_count'],
                features['char_count'],
                features['has_hashtags'],
                features['hashtag_count'],
                features['has_mentions'],
                features['mention_count'],
                features['has_url'],
                features['has_emoji'],
                features['has_question'],
                features['has_exclamation'],
                features['hour'],
                features['is_weekend'],
                features['has_image'],
                features['has_video'],
                features['platform_facebook'],
                features['platform_twitter'],
                features['platform_linkedin'],
                features['platform_instagram'],
            ])
            labels.append(item['engagement_score'])

        # Split data
        X_text_train, X_text_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
            texts, numeric_features, labels, test_size=0.2, random_state=42
        )

        # Create and train text vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=kwargs.get('max_features', 200),
            ngram_range=(1, 2),
            stop_words='english'
        )
        X_text_train_vec = self.vectorizer.fit_transform(X_text_train)
        X_text_test_vec = self.vectorizer.transform(X_text_test)

        # Combine text and numeric features
        X_train_combined = np.hstack([
            X_text_train_vec.toarray(),
            np.array(X_num_train)
        ])
        X_test_combined = np.hstack([
            X_text_test_vec.toarray(),
            np.array(X_num_test)
        ])

        # Train regressor
        self.model = GradientBoostingRegressor(
            n_estimators=kwargs.get('n_estimators', 100),
            max_depth=kwargs.get('max_depth', 5),
            learning_rate=kwargs.get('learning_rate', 0.1),
            random_state=42
        )
        self.model.fit(X_train_combined, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_combined)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Update config
        self.config = MLModelConfig(
            model_name='content_optimizer',
            model_version='1.0',
            model_type='regressor',
            created_at=datetime.now().isoformat(),
            last_trained=datetime.now().isoformat(),
            training_samples=len(training_data),
            accuracy=float(r2),  # Using R² as accuracy metric for regression
            feature_names=[
                'text_features', 'word_count', 'char_count', 'has_hashtags', 'hashtag_count',
                'has_mentions', 'mention_count', 'has_url', 'has_emoji', 'has_question',
                'has_exclamation', 'hour', 'is_weekend', 'has_image', 'has_video',
                'platform_facebook', 'platform_twitter', 'platform_linkedin', 'platform_instagram'
            ],
            hyperparameters={
                'max_features': kwargs.get('max_features', 200),
                'n_estimators': kwargs.get('n_estimators', 100),
                'max_depth': kwargs.get('max_depth', 5),
                'learning_rate': kwargs.get('learning_rate', 0.1),
                'rmse': float(rmse),
                'mae': float(mae)
            }
        )

        self.is_trained = True
        self._save_model()
        self.save_config()

        logger.info(f"Content optimizer trained: R²={r2:.3f}, RMSE={rmse:.3f}")

        return {
            'r2_score': r2,
            'rmse': rmse,
            'mae': mae,
            'mse': mse,
            'training_samples': len(training_data),
            'test_samples': len(X_test_combined)
        }

    def predict(self, input_data: Any) -> Dict[str, Any]:
        """
        Predict engagement score and provide optimization suggestions.

        Args:
            input_data: Content data dictionary

        Returns:
            Dictionary with prediction results and suggestions
        """
        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            return {'error': error, 'engagement_score': 0.0, 'suggestions': []}

        if not isinstance(input_data, dict):
            return {'error': 'Input must be a dictionary', 'engagement_score': 0.0, 'suggestions': []}

        try:
            # Extract features
            features = self._extract_features(input_data)
            text = features['text']
            numeric = [
                features['word_count'],
                features['char_count'],
                features['has_hashtags'],
                features['hashtag_count'],
                features['has_mentions'],
                features['mention_count'],
                features['has_url'],
                features['has_emoji'],
                features['has_question'],
                features['has_exclamation'],
                features['hour'],
                features['is_weekend'],
                features['has_image'],
                features['has_video'],
                features['platform_facebook'],
                features['platform_twitter'],
                features['platform_linkedin'],
                features['platform_instagram'],
            ]

            # Vectorize text
            text_vec = self.vectorizer.transform([text])

            # Combine features
            X_combined = np.hstack([text_vec.toarray(), np.array([numeric])])

            # Predict
            engagement_score = float(self.model.predict(X_combined)[0])

            # Generate optimization suggestions
            suggestions = self._generate_suggestions(features, engagement_score)

            return {
                'engagement_score': engagement_score,
                'suggestions': suggestions,
                'features_analyzed': features,
                'model_version': self.config.model_version if self.config else 'unknown'
            }

        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            return {'error': str(e), 'engagement_score': 0.0, 'suggestions': []}

    def _generate_suggestions(self, features: Dict[str, Any], current_score: float) -> List[str]:
        """
        Generate optimization suggestions based on features.

        Args:
            features: Extracted features
            current_score: Current predicted engagement score

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Word count suggestions
        if features['word_count'] < 10:
            suggestions.append("Consider adding more content - posts with 10-30 words tend to perform better")
        elif features['word_count'] > 50:
            suggestions.append("Consider shortening the text - concise posts often get more engagement")

        # Hashtag suggestions
        if features['hashtag_count'] == 0:
            suggestions.append("Add 2-3 relevant hashtags to increase discoverability")
        elif features['hashtag_count'] > 5:
            suggestions.append("Reduce hashtags to 2-3 - too many can look spammy")

        # Media suggestions
        if not features['has_image'] and not features['has_video']:
            suggestions.append("Add an image or video - visual content significantly boosts engagement")

        # Emoji suggestions
        if not features['has_emoji']:
            suggestions.append("Consider adding 1-2 emojis to make the post more engaging")

        # Question suggestions
        if not features['has_question']:
            suggestions.append("Try ending with a question to encourage comments and interaction")

        # Timing suggestions
        if features['hour'] < 8 or features['hour'] > 20:
            suggestions.append("Consider posting during peak hours (8am-8pm) for better visibility")

        # URL suggestions
        if features['has_url']:
            suggestions.append("URLs can reduce engagement - consider using link in bio or comments")

        # Platform-specific suggestions
        if features['platform_twitter'] and features['char_count'] > 280:
            suggestions.append("Twitter has a 280 character limit - shorten your text")

        if features['platform_instagram'] and features['hashtag_count'] < 5:
            suggestions.append("Instagram posts perform well with 5-10 hashtags")

        if features['platform_linkedin'] and features['word_count'] < 20:
            suggestions.append("LinkedIn audiences prefer more detailed, professional content")

        return suggestions[:5]  # Return top 5 suggestions

    def _save_model(self) -> None:
        """Save model and vectorizer to disk."""
        if self.model is None or self.vectorizer is None:
            return

        model_path = self.get_model_path('model.pkl')
        vectorizer_path = self.get_model_path('vectorizer.pkl')

        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)

        logger.info(f"Saved content optimizer to {self.model_dir}")

    def _load_model(self) -> bool:
        """
        Load model and vectorizer from disk.

        Returns:
            True if loaded successfully, False otherwise
        """
        model_path = self.get_model_path('model.pkl')
        vectorizer_path = self.get_model_path('vectorizer.pkl')

        if not model_path.exists() or not vectorizer_path.exists():
            return False

        try:
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.is_trained = True
            self.load_config()
            logger.info(f"Loaded content optimizer from {self.model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading content optimizer: {e}")
            return False

    def generate_sample_training_data(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Generate sample training data for testing.

        Args:
            count: Number of samples to generate

        Returns:
            List of training examples
        """
        samples = [
            # High engagement
            {'text': 'Check out our new product launch! 🚀 What do you think? #innovation #tech', 'platform': 'twitter', 'has_image': True, 'post_hour': 14, 'engagement_score': 8.5},
            {'text': 'Behind the scenes at our office 📸 #teamwork', 'platform': 'instagram', 'has_image': True, 'post_hour': 18, 'engagement_score': 9.2},
            {'text': 'Excited to share our Q1 results! 📊 What challenges are you facing?', 'platform': 'linkedin', 'has_image': True, 'post_hour': 10, 'engagement_score': 7.8},

            # Medium engagement
            {'text': 'New blog post is live! Check it out', 'platform': 'facebook', 'has_url': True, 'post_hour': 12, 'engagement_score': 5.5},
            {'text': 'Happy Monday everyone! Hope you have a great week', 'platform': 'twitter', 'post_hour': 9, 'engagement_score': 4.8},
            {'text': 'Working on something exciting', 'platform': 'instagram', 'post_hour': 15, 'engagement_score': 5.2},

            # Low engagement
            {'text': 'Update', 'platform': 'twitter', 'post_hour': 3, 'engagement_score': 1.5},
            {'text': 'Check this out http://example.com/very/long/url/that/nobody/clicks', 'platform': 'facebook', 'has_url': True, 'post_hour': 23, 'engagement_score': 2.1},
            {'text': 'Post', 'platform': 'instagram', 'post_hour': 4, 'engagement_score': 1.8},
        ]

        # Repeat and vary samples to reach desired count
        while len(samples) < count:
            samples.extend(samples[:min(len(samples), count - len(samples))])

        return samples[:count]
