---
name: social-media
description: Manage social media content across multiple platforms
version: 1.0.0
---

# Social Media Integration

This skill provides multi-platform social media management for the Personal AI Employee system.

## Supported Platforms

- **Facebook** - Page posts and engagement
- **Instagram** - Business account posts with images
- **Twitter/X** - Tweets and threads
- **LinkedIn** - Professional posts and articles

## Available Operations

### 1. Post to Platform

Post content immediately to a social media platform:

```
Post to Facebook: "Excited to announce our new product launch! 🚀"
```

```
Post to Instagram with image: "Check out our latest design" [image: /path/to/image.jpg]
```

```
Tweet: "Just shipped a major update to our platform. Check it out!"
```

```
Post to LinkedIn: "Thrilled to share our Q1 results with the team..."
```

### 2. Schedule Posts

Schedule posts for future publication:

```
Schedule a Facebook post for tomorrow at 10 AM: "Happy Monday everyone!"
```

```
Schedule Instagram post for Friday 3 PM: "Weekend vibes 🌴" [image: beach.jpg]
```

```
Schedule LinkedIn post for next Monday 9 AM: "Weekly industry insights..."
```

### 3. Get Platform Stats

View engagement metrics and statistics:

```
Show me Facebook stats for the last 7 days
```

```
Get Instagram analytics for this month
```

```
Show Twitter engagement metrics
```

### 4. View Recent Posts

See recently published content:

```
Show my last 10 Facebook posts
```

```
List recent Instagram posts
```

```
Show my recent tweets
```

### 5. Delete Posts

Remove published content:

```
Delete Facebook post [post_id]
```

```
Remove Instagram post [post_id]
```

## Workflow Integration

### Content Creation from Tasks

When processing content creation tasks:

1. Read task file from Needs_Action/
2. Generate content based on requirements
3. Create approval request for posting
4. After approval, post to platform(s)
5. Log post details
6. Move task to Done/

### Weekly Content Planning

Generate and schedule a week's worth of content:

1. Analyze trending topics
2. Generate 3-5 posts per platform
3. Create approval requests for each
4. After approval, schedule posts
5. Distribute throughout the week
6. Log scheduled posts

### Email-to-Social Workflow

Convert email requests into social posts:

1. Email arrives: "Please post about our new feature"
2. Extract key information
3. Generate platform-appropriate content
4. Create approval request
5. After approval, post or schedule
6. Send confirmation email
7. Move email to Done/

## Content Guidelines

### Character Limits

- **Twitter:** 280 characters
- **Facebook:** 63,206 characters (recommended: 40-80)
- **Instagram:** 2,200 characters (recommended: 138-150)
- **LinkedIn:** 3,000 characters (recommended: 150-300)

### Hashtag Best Practices

- **Twitter:** 1-2 hashtags
- **Facebook:** 2-5 hashtags
- **Instagram:** 5-30 hashtags (optimal: 11)
- **LinkedIn:** 3-5 hashtags

### Optimal Posting Times

- **Facebook:** 1-4 PM weekdays
- **Instagram:** 11 AM - 1 PM weekdays
- **Twitter:** 8-10 AM, 6-9 PM weekdays
- **LinkedIn:** 7-8 AM, 12 PM, 5-6 PM weekdays

### Content Types

**Facebook:**
- Company updates
- Behind-the-scenes content
- Customer stories
- Event announcements

**Instagram:**
- Visual content (photos, graphics)
- Product showcases
- Lifestyle content
- User-generated content

**Twitter:**
- Quick updates
- Industry news
- Engagement/conversations
- Links to blog posts

**LinkedIn:**
- Professional insights
- Company milestones
- Thought leadership
- Industry trends

## Human-in-the-Loop (HITL)

All social media posts require approval before publishing:

1. **Content Review** - Verify message, tone, and accuracy
2. **Platform Selection** - Confirm target platforms
3. **Timing** - Approve immediate or scheduled posting
4. **Media** - Review attached images/videos

Approval requests created in: `AI_Employee_Vault/Needs_Action/APPROVAL_SOCIAL_*.md`

## Scheduling System

### Queue Management

Posts are queued in: `/tmp/social_media_queue/`

Each scheduled post includes:
- Platform
- Content
- Media URLs
- Scheduled time
- Status (scheduled, posted, failed)

### Scheduler Daemon

Run the scheduler to automatically publish posts:

```bash
python3 watchers/social_media_scheduler.py --daemon --interval 60
```

Or process queue once:

```bash
python3 watchers/social_media_scheduler.py --process
```

### List Pending Posts

```bash
python3 watchers/social_media_scheduler.py --list
```

## Configuration

Social media credentials stored in:
```
AI_Employee_Vault/Config/social_media_config.json
```

Required for each platform:
- **Facebook:** Access token, Page ID
- **Instagram:** Access token, Business Account ID
- **Twitter:** API keys, Access tokens, Bearer token
- **LinkedIn:** Access token, Person URN

## Error Handling

If posting fails:

1. Log error to `AI_Employee_Vault/Logs/social_media_errors.log`
2. Mark post as failed in queue
3. Create manual review task
4. Notify user of failure
5. Provide troubleshooting steps

Common errors:
- **Authentication Failed** - Check access tokens
- **Rate Limit Exceeded** - Wait and retry
- **Invalid Content** - Check character limits
- **Media Upload Failed** - Verify image format/size

## Examples

### Example 1: Weekly Content Generation

```
Task: Generate 3 LinkedIn posts for this week about our product updates

Actions:
1. Review recent product updates
2. Generate 3 professional posts
3. Create approval requests for each
4. After approval, schedule:
   - Monday 9 AM: Feature announcement
   - Wednesday 12 PM: Customer success story
   - Friday 3 PM: Weekly recap
5. Log scheduled posts
6. Move task to Done/
```

### Example 2: Cross-Platform Announcement

```
Task: Announce new partnership across all platforms

Actions:
1. Generate platform-specific content:
   - Twitter: Short announcement (280 chars)
   - Facebook: Detailed post with link
   - Instagram: Visual post with image
   - LinkedIn: Professional announcement
2. Create approval request for all 4 posts
3. After approval, post immediately to all platforms
4. Log post IDs and URLs
5. Track engagement
6. Move task to Done/
```

### Example 3: Scheduled Campaign

```
Task: Create 5-day product launch campaign

Actions:
1. Generate 5 posts per platform (20 total)
2. Create approval requests
3. After approval, schedule:
   - Day 1: Teaser posts
   - Day 2: Feature highlights
   - Day 3: Customer testimonials
   - Day 4: Behind-the-scenes
   - Day 5: Launch announcement
4. Distribute across optimal times
5. Log all scheduled posts
6. Move task to Done/
```

## Integration with Other Systems

### CEO Briefing Integration

Social media metrics included in weekly briefings:
- Posts published this week
- Total engagement (likes, comments, shares)
- Follower growth
- Top performing posts
- Platform-specific insights

### Email Integration

Automatically process:
- Social media post requests
- Content approval notifications
- Engagement alerts
- Scheduling confirmations

### Dashboard Integration

Real-time social media metrics:
- Posts published today
- Pending scheduled posts
- Recent engagement
- Platform health status

## Analytics & Reporting

### Weekly Report

Automatically generated metrics:
- Posts published per platform
- Total impressions
- Total engagements
- Engagement rate
- Follower growth
- Top performing content

### Monthly Report

Comprehensive analysis:
- Content performance trends
- Best posting times
- Optimal content types
- Audience growth
- Recommendations for improvement

## Troubleshooting

### Connection Issues

If platform connection fails:
1. Check `social_media_config.json` credentials
2. Verify access tokens haven't expired
3. Test API access manually
4. Check platform API status
5. Review error logs

### Authentication Issues

If authentication fails:
1. Regenerate access tokens
2. Verify permissions/scopes
3. Check account status
4. Review API rate limits
5. Test with platform's API explorer

### Posting Issues

If posts fail:
1. Check content length
2. Verify media format/size
3. Review platform guidelines
4. Check rate limits
5. Review error message in logs

## Security Notes

- Credentials stored in config file (not in git)
- All posts require approval
- API access limited to posting operations
- All operations logged
- Rate limiting enforced

## Best Practices

1. **Content Quality** - Always review before posting
2. **Timing** - Post during optimal hours
3. **Engagement** - Respond to comments promptly
4. **Consistency** - Maintain regular posting schedule
5. **Analytics** - Review performance weekly
6. **Compliance** - Follow platform guidelines
7. **Backup** - Keep copies of all content

## Next Steps

After setup:
1. Test posting to each platform
2. Schedule test posts
3. Verify scheduler daemon
4. Review analytics
5. Integrate with content calendar
6. Set up monitoring alerts
