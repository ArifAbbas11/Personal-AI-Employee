"""
Marketing Agent

Specialized agent for marketing automation, social media management, and content optimization.
Integrates with Content Optimizer ML model and social media platforms.
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_agent.base import (
    BaseAgent,
    AgentRole,
    AgentCapability,
    AgentTask,
    AgentCoordinator,
    TaskPriority
)

# Import ML model for content optimization
from ml_engine.content_optimizer import ContentOptimizer

logger = logging.getLogger(__name__)


class MarketingAgent(BaseAgent):
    """Agent specialized in marketing and social media management."""

    def __init__(
        self,
        vault_path: str = "AI_Employee_Vault",
        coordinator: Optional[AgentCoordinator] = None
    ):
        """
        Initialize Marketing Agent.

        Args:
            vault_path: Path to AI_Employee_Vault
            coordinator: Optional agent coordinator
        """
        super().__init__(
            agent_id="marketing_agent",
            role=AgentRole.MARKETING,
            vault_path=vault_path,
            coordinator=coordinator
        )

        # Initialize ML model for content optimization
        try:
            self.content_optimizer = ContentOptimizer(vault_path)
            logger.info("Content optimizer loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load content optimizer: {e}")
            self.content_optimizer = None

        # Marketing data cache
        self.campaigns: Dict[str, Dict[str, Any]] = {}
        self.posts: List[Dict[str, Any]] = []
        self.analytics: Dict[str, List[Dict[str, Any]]] = {
            'twitter': [],
            'linkedin': [],
            'facebook': [],
            'instagram': []
        }

    def _initialize_capabilities(self) -> None:
        """Initialize marketing agent capabilities."""
        self.capabilities = [
            AgentCapability(
                capability_id="optimize_content",
                name="Optimize Content",
                description="Optimize social media content for engagement using ML",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "platform": {"type": "string", "enum": ["twitter", "linkedin", "facebook", "instagram"]},
                        "post_time": {"type": "string"}
                    },
                    "required": ["content", "platform"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "predicted_engagement": {"type": "number"},
                        "recommendations": {"type": "array"}
                    }
                },
                estimated_duration_seconds=10
            ),
            AgentCapability(
                capability_id="create_social_post",
                name="Create Social Media Post",
                description="Create and schedule a social media post",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "platform": {"type": "string"},
                        "schedule_time": {"type": "string"},
                        "media_urls": {"type": "array"}
                    },
                    "required": ["content", "platform"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "post_id": {"type": "string"},
                        "scheduled": {"type": "boolean"}
                    }
                },
                estimated_duration_seconds=15
            ),
            AgentCapability(
                capability_id="analyze_campaign",
                name="Analyze Campaign",
                description="Analyze marketing campaign performance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "metrics": {"type": "array"}
                    },
                    "required": ["campaign_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "analysis": {"type": "object"}
                    }
                },
                estimated_duration_seconds=30
            ),
            AgentCapability(
                capability_id="generate_content_ideas",
                name="Generate Content Ideas",
                description="Generate content ideas based on trends and audience",
                input_schema={
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "platform": {"type": "string"},
                        "count": {"type": "integer"}
                    },
                    "required": ["topic"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "ideas": {"type": "array"}
                    }
                },
                estimated_duration_seconds=20
            ),
            AgentCapability(
                capability_id="track_engagement",
                name="Track Engagement",
                description="Track and analyze social media engagement metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string"},
                        "period_days": {"type": "integer"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "metrics": {"type": "object"}
                    }
                },
                estimated_duration_seconds=15
            ),
            AgentCapability(
                capability_id="schedule_campaign",
                name="Schedule Campaign",
                description="Schedule a multi-post marketing campaign",
                input_schema={
                    "type": "object",
                    "properties": {
                        "campaign_name": {"type": "string"},
                        "posts": {"type": "array"},
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"}
                    },
                    "required": ["campaign_name", "posts"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "scheduled": {"type": "boolean"}
                    }
                },
                estimated_duration_seconds=30
            )
        ]

    def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a marketing task.

        Args:
            task: Task to process

        Returns:
            Task result dictionary
        """
        task_type = task.task_type
        metadata = task.metadata

        if task_type == "optimize_content":
            return self._optimize_content(metadata)
        elif task_type == "create_social_post":
            return self._create_social_post(metadata)
        elif task_type == "analyze_campaign":
            return self._analyze_campaign(metadata)
        elif task_type == "generate_content_ideas":
            return self._generate_content_ideas(metadata)
        elif task_type == "track_engagement":
            return self._track_engagement(metadata)
        elif task_type == "schedule_campaign":
            return self._schedule_campaign(metadata)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _optimize_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize social media content using ML."""
        content = data.get('content', '')
        platform = data.get('platform', 'twitter')
        post_time = data.get('post_time', datetime.now().isoformat())

        # Extract features
        content_length = len(content)
        hashtag_count = content.count('#')
        mention_count = content.count('@')

        # Parse post time
        try:
            post_dt = datetime.fromisoformat(post_time.replace('Z', '+00:00'))
            hour = post_dt.hour
        except:
            hour = 12  # Default to noon

        if self.content_optimizer and self.content_optimizer.is_trained:
            # Use ML model
            result = self.content_optimizer.predict({
                'content': content,
                'platform': platform,
                'content_length': content_length,
                'hashtag_count': hashtag_count,
                'mention_count': mention_count,
                'post_hour': hour
            })
            predicted_engagement = result['engagement_score']
        else:
            # Fallback to heuristic scoring
            predicted_engagement = self._heuristic_engagement_score(
                content_length, hashtag_count, mention_count, hour, platform
            )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            content, platform, content_length, hashtag_count, predicted_engagement
        )

        return {
            'success': True,
            'predicted_engagement': predicted_engagement,
            'recommendations': recommendations,
            'content_analysis': {
                'length': content_length,
                'hashtags': hashtag_count,
                'mentions': mention_count,
                'post_hour': hour
            }
        }

    def _heuristic_engagement_score(
        self,
        length: int,
        hashtags: int,
        mentions: int,
        hour: int,
        platform: str
    ) -> float:
        """Calculate heuristic engagement score."""
        score = 50.0  # Base score

        # Length scoring (platform-specific optimal lengths)
        optimal_lengths = {
            'twitter': 280,
            'linkedin': 150,
            'facebook': 120,
            'instagram': 150
        }
        optimal = optimal_lengths.get(platform, 150)
        length_score = 100 - abs(length - optimal) / optimal * 50
        score += length_score * 0.3

        # Hashtag scoring (2-3 is optimal)
        if 2 <= hashtags <= 3:
            score += 20
        elif hashtags == 1 or hashtags == 4:
            score += 10
        elif hashtags > 5:
            score -= 10

        # Mention scoring
        if mentions > 0:
            score += min(mentions * 5, 15)

        # Time scoring (peak hours: 9-11 AM, 1-3 PM)
        if hour in [9, 10, 11, 13, 14, 15]:
            score += 15
        elif hour in [8, 12, 16, 17]:
            score += 10

        return max(0, min(100, score))

    def _generate_recommendations(
        self,
        content: str,
        platform: str,
        length: int,
        hashtags: int,
        predicted_engagement: float
    ) -> List[str]:
        """Generate content optimization recommendations."""
        recommendations = []

        # Length recommendations
        optimal_lengths = {
            'twitter': 280,
            'linkedin': 150,
            'facebook': 120,
            'instagram': 150
        }
        optimal = optimal_lengths.get(platform, 150)

        if length < optimal * 0.5:
            recommendations.append(f"Consider expanding content (current: {length}, optimal: ~{optimal} chars)")
        elif length > optimal * 1.5:
            recommendations.append(f"Consider shortening content (current: {length}, optimal: ~{optimal} chars)")

        # Hashtag recommendations
        if hashtags == 0:
            recommendations.append("Add 2-3 relevant hashtags to increase discoverability")
        elif hashtags > 5:
            recommendations.append("Reduce hashtags to 2-3 for better engagement")

        # Engagement prediction
        if predicted_engagement < 40:
            recommendations.append("Low predicted engagement - consider revising content or timing")
        elif predicted_engagement > 70:
            recommendations.append("High predicted engagement - good content!")

        # Platform-specific recommendations
        if platform == 'twitter' and '@' not in content:
            recommendations.append("Consider mentioning relevant accounts to increase reach")
        elif platform == 'linkedin' and '?' not in content:
            recommendations.append("Questions tend to drive engagement on LinkedIn")
        elif platform == 'instagram' and hashtags < 5:
            recommendations.append("Instagram posts perform well with 5-10 hashtags")

        return recommendations

    def _create_social_post(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and schedule a social media post."""
        import uuid

        post = {
            'post_id': str(uuid.uuid4()),
            'content': data.get('content', ''),
            'platform': data.get('platform', 'twitter'),
            'schedule_time': data.get('schedule_time', datetime.now().isoformat()),
            'media_urls': data.get('media_urls', []),
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }

        self.posts.append(post)
        self._save_posts()

        logger.info(f"Social post created: {post['post_id']} for {post['platform']}")

        return {
            'success': True,
            'post_id': post['post_id'],
            'scheduled': True,
            'post': post
        }

    def _analyze_campaign(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze marketing campaign performance."""
        campaign_id = data.get('campaign_id')

        if campaign_id not in self.campaigns:
            return {
                'success': False,
                'message': f"Campaign not found: {campaign_id}"
            }

        campaign = self.campaigns[campaign_id]

        # Get campaign posts
        campaign_posts = [
            p for p in self.posts
            if p.get('campaign_id') == campaign_id
        ]

        # Calculate metrics
        total_posts = len(campaign_posts)
        platforms = list(set(p['platform'] for p in campaign_posts))

        # Simulated engagement metrics
        total_impressions = total_posts * 1000
        total_engagements = total_posts * 50
        engagement_rate = (total_engagements / total_impressions * 100) if total_impressions > 0 else 0

        return {
            'success': True,
            'campaign_id': campaign_id,
            'campaign_name': campaign['name'],
            'analysis': {
                'total_posts': total_posts,
                'platforms': platforms,
                'total_impressions': total_impressions,
                'total_engagements': total_engagements,
                'engagement_rate': engagement_rate,
                'status': campaign.get('status', 'active')
            }
        }

    def _generate_content_ideas(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content ideas based on topic and platform."""
        topic = data.get('topic', '')
        platform = data.get('platform', 'twitter')
        count = data.get('count', 5)

        # Generate ideas based on topic
        ideas = []

        # Template-based idea generation
        templates = [
            f"5 ways {topic} can transform your business",
            f"The ultimate guide to {topic}",
            f"Common mistakes to avoid with {topic}",
            f"How {topic} is changing the industry",
            f"Expert tips for mastering {topic}",
            f"The future of {topic}: What to expect",
            f"Case study: Success with {topic}",
            f"Quick wins with {topic}",
            f"Behind the scenes: Our {topic} process",
            f"Q&A: Everything you need to know about {topic}"
        ]

        for i, template in enumerate(templates[:count]):
            ideas.append({
                'idea_id': f"idea_{i+1}",
                'content': template,
                'platform': platform,
                'type': 'educational' if i % 2 == 0 else 'promotional',
                'estimated_engagement': 60 + (i * 5)
            })

        return {
            'success': True,
            'topic': topic,
            'platform': platform,
            'ideas': ideas,
            'count': len(ideas)
        }

    def _track_engagement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Track social media engagement metrics."""
        platform = data.get('platform', 'all')
        period_days = data.get('period_days', 30)

        cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()

        # Filter posts by platform and date
        if platform == 'all':
            recent_posts = [
                p for p in self.posts
                if p.get('created_at', '') >= cutoff_date
            ]
        else:
            recent_posts = [
                p for p in self.posts
                if p.get('platform') == platform and p.get('created_at', '') >= cutoff_date
            ]

        # Calculate metrics (simulated)
        total_posts = len(recent_posts)
        total_impressions = total_posts * 1000
        total_engagements = total_posts * 50
        total_clicks = total_posts * 25

        # Group by platform
        by_platform = {}
        for post in recent_posts:
            plat = post.get('platform', 'unknown')
            if plat not in by_platform:
                by_platform[plat] = {'posts': 0, 'impressions': 0, 'engagements': 0}
            by_platform[plat]['posts'] += 1
            by_platform[plat]['impressions'] += 1000
            by_platform[plat]['engagements'] += 50

        return {
            'success': True,
            'platform': platform,
            'period_days': period_days,
            'metrics': {
                'total_posts': total_posts,
                'total_impressions': total_impressions,
                'total_engagements': total_engagements,
                'total_clicks': total_clicks,
                'engagement_rate': (total_engagements / total_impressions * 100) if total_impressions > 0 else 0,
                'click_through_rate': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                'by_platform': by_platform
            }
        }

    def _schedule_campaign(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a multi-post marketing campaign."""
        import uuid

        campaign_id = str(uuid.uuid4())
        campaign = {
            'campaign_id': campaign_id,
            'name': data.get('campaign_name', ''),
            'posts': data.get('posts', []),
            'start_date': data.get('start_date', datetime.now().isoformat()),
            'end_date': data.get('end_date'),
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }

        self.campaigns[campaign_id] = campaign

        # Create individual posts
        for i, post_data in enumerate(campaign['posts']):
            post = {
                'post_id': str(uuid.uuid4()),
                'campaign_id': campaign_id,
                'content': post_data.get('content', ''),
                'platform': post_data.get('platform', 'twitter'),
                'schedule_time': post_data.get('schedule_time'),
                'status': 'scheduled',
                'created_at': datetime.now().isoformat()
            }
            self.posts.append(post)

        self._save_campaigns()
        self._save_posts()

        logger.info(f"Campaign scheduled: {campaign_id} with {len(campaign['posts'])} posts")

        return {
            'success': True,
            'campaign_id': campaign_id,
            'scheduled': True,
            'posts_count': len(campaign['posts']),
            'campaign': campaign
        }

    def _save_posts(self) -> None:
        """Save posts to disk."""
        import json
        posts_path = self.agent_dir / "posts.json"
        try:
            with open(posts_path, 'w') as f:
                json.dump(self.posts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving posts: {e}")

    def _save_campaigns(self) -> None:
        """Save campaigns to disk."""
        import json
        campaigns_path = self.agent_dir / "campaigns.json"
        try:
            with open(campaigns_path, 'w') as f:
                json.dump(self.campaigns, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving campaigns: {e}")


def main():
    """Main function for testing marketing agent."""
    import argparse

    parser = argparse.ArgumentParser(description='Marketing Agent')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize agent
    agent = MarketingAgent(args.vault_path)

    if args.test:
        print("Testing Marketing Agent...")
        print("=" * 80)

        # Test 1: Optimize content
        print("\nTest 1: Optimize Content")
        task = AgentTask(
            task_id="test_1",
            task_type="optimize_content",
            description="Optimize social media post",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'content': 'Check out our new product launch! #innovation #tech',
                'platform': 'twitter',
                'post_time': '2026-02-28T10:00:00Z'
            }
        )
        result = agent.process_task(task)
        print(f"  Predicted Engagement: {result['predicted_engagement']:.1f}")
        print(f"  Recommendations: {len(result['recommendations'])}")
        for rec in result['recommendations']:
            print(f"    - {rec}")

        # Test 2: Create social post
        print("\nTest 2: Create Social Post")
        task = AgentTask(
            task_id="test_2",
            task_type="create_social_post",
            description="Create LinkedIn post",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'content': 'Excited to announce our Q1 results! #growth #business',
                'platform': 'linkedin',
                'schedule_time': '2026-03-01T09:00:00Z'
            }
        )
        result = agent.process_task(task)
        print(f"  Post ID: {result['post_id']}")
        print(f"  Scheduled: {result['scheduled']}")

        # Test 3: Generate content ideas
        print("\nTest 3: Generate Content Ideas")
        task = AgentTask(
            task_id="test_3",
            task_type="generate_content_ideas",
            description="Generate AI content ideas",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'topic': 'artificial intelligence',
                'platform': 'linkedin',
                'count': 3
            }
        )
        result = agent.process_task(task)
        print(f"  Ideas Generated: {result['count']}")
        for idea in result['ideas']:
            print(f"    - {idea['content']}")

        # Test 4: Track engagement
        print("\nTest 4: Track Engagement")
        task = AgentTask(
            task_id="test_4",
            task_type="track_engagement",
            description="Track engagement metrics",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'platform': 'all',
                'period_days': 30
            }
        )
        result = agent.process_task(task)
        print(f"  Total Posts: {result['metrics']['total_posts']}")
        print(f"  Engagement Rate: {result['metrics']['engagement_rate']:.2f}%")

        # Test 5: Agent status
        print("\nTest 5: Agent Status")
        status = agent.get_status()
        print(f"  Agent ID: {status['agent_id']}")
        print(f"  Role: {status['role']}")
        print(f"  Capabilities: {len(status['capabilities'])}")

    else:
        print("Marketing Agent initialized")
        print(f"Agent ID: {agent.agent_id}")
        print(f"Role: {agent.role.value}")
        print(f"Capabilities: {len(agent.capabilities)}")


if __name__ == '__main__':
    main()
