# AI Caption Generation - Implementation Guide

## 🎯 Overview

This system allows you to provide simple inputs (Platform, Image, Topic, Details) and the AI automatically generates platform-optimized captions with hashtags, emojis, and calls-to-action.

## 📋 How It Works

### User Input (Simple)
```markdown
Platform: instagram
Image: product.jpg
Topic: New AI feature launch
Details:
- Saves 10 hours per week
- Free 30-day trial
- Target small businesses
```

### AI Output (Complete)
```markdown
🚀 BIG NEWS! Launching our newest AI feature!

✨ Automated Email Responses
⏰ Save 10+ hours every week
🤖 Smart, professional replies
💰 Free 30-day trial

Ready to reclaim your time? Link in bio! 👆

#AIAutomation #ProductLaunch #SmallBusiness #Productivity
```

## 🔧 Implementation Status

### ✅ What's Ready
- Folder structure created (Pending_Approval, Approved, Done for all platforms)
- Universal template with examples
- Workflow documentation
- Platform-specific guidelines

### ⏳ What Needs Implementation

#### 1. Update Post Generator Watcher

**File:** `watchers/post_generator.py`

**Add caption generation function:**
```python
def generate_caption(self, platform: str, topic: str, details: str) -> str:
    """
    Generate platform-optimized caption using Groq API

    Args:
        platform: instagram, facebook, twitter, linkedin
        topic: Main topic of the post
        details: Bullet points with specific requirements

    Returns:
        Generated caption with hashtags and emojis
    """
    import os
    from groq import Groq

    client = Groq(api_key=os.getenv('GROQ_API_KEY'))

    # Platform-specific guidelines
    guidelines = {
        'instagram': {
            'max_length': 2200,
            'hashtags': '5-10',
            'emojis': '3-5',
            'tone': 'Visual, engaging, story-driven'
        },
        'facebook': {
            'max_length': 500,
            'hashtags': '1-3',
            'emojis': '2-4',
            'tone': 'Conversational, community-focused'
        },
        'twitter': {
            'max_length': 280,
            'hashtags': '1-2',
            'emojis': '1-2',
            'tone': 'Concise, punchy, timely'
        },
        'linkedin': {
            'max_length': 1300,
            'hashtags': '3-5',
            'emojis': '1-2 (professional)',
            'tone': 'Professional, value-driven, educational'
        }
    }

    guide = guidelines.get(platform, guidelines['instagram'])

    prompt = f"""Generate a {platform} post caption based on these requirements:

Topic: {topic}

Details:
{details}

Platform Guidelines:
- Maximum length: {guide['max_length']} characters
- Hashtags: {guide['hashtags']}
- Emojis: {guide['emojis']}
- Tone: {guide['tone']}

Requirements:
1. Create an engaging caption that matches the platform's style
2. Include relevant emojis naturally throughout
3. Add appropriate hashtags at the end
4. Include a call-to-action
5. Make it authentic and valuable to the audience

Generate ONLY the caption text, no explanations."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()
```

#### 2. Update Post File Parser

**Add to `watchers/post_generator.py`:**
```python
def parse_universal_template(self, file_path: Path) -> dict:
    """Parse universal social media template"""
    content = file_path.read_text()

    # Extract fields
    platform = None
    image = None
    topic = None
    details = []

    lines = content.split('\n')
    in_details = False

    for line in lines:
        if line.startswith('**Platform:**'):
            platform = line.split('**Platform:**')[1].strip()
        elif line.startswith('**Image:**'):
            image = line.split('**Image:**')[1].strip()
        elif line.startswith('**Topic:**'):
            topic = line.split('**Topic:**')[1].strip()
        elif line.startswith('**Details:**'):
            in_details = True
        elif in_details and line.strip().startswith('-'):
            details.append(line.strip()[1:].strip())
        elif in_details and line.strip() == '---':
            break

    return {
        'platform': platform,
        'image': image,
        'topic': topic,
        'details': '\n'.join(details)
    }
```

#### 3. Create Formatted Post File

**Add to `watchers/post_generator.py`:**
```python
def create_pending_approval_post(self, platform: str, image: str,
                                 topic: str, caption: str,
                                 original_file: str) -> Path:
    """Create formatted post in Pending_Approval folder"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"POST_{timestamp}_{platform}.md"

    pending_dir = self.vault_path / 'Pending_Approval' / platform
    pending_dir.mkdir(parents=True, exist_ok=True)

    post_content = f"""# {platform.title()} Post - Pending Approval

**Status:** Pending Approval
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Platform:** {platform}
**Image:** {image}

---

## Generated Caption

{caption}

---

## Original Request

**Topic:** {topic}

**Original File:** {original_file}

---

## Instructions

1. **Review** the generated caption above
2. **Edit** if needed (modify the text under "Generated Caption")
3. **When satisfied**, move this file to: `Approved/{platform}/`
4. The system will automatically post within 60 seconds

**To approve:**
```bash
mv Pending_Approval/{platform}/{filename} Approved/{platform}/
```

**To reject:** Delete this file or move to Rejected folder

---

## Image Location

The image `{image}` should be in:
- `Post_Ideas/{image}` (original location)
- Or move it to `Approved/{platform}/{image}` when approving

---

*Generated by AI Employee Post Generator*
*Powered by Groq API (Llama 3.3 70B)*
"""

    output_file = pending_dir / filename
    output_file.write_text(post_content)

    return output_file
```

#### 4. Main Processing Loop

**Add to `watchers/post_generator.py`:**
```python
def process_universal_templates(self):
    """Process universal social media templates"""
    post_ideas_dir = self.vault_path / 'Post_Ideas'

    if not post_ideas_dir.exists():
        return

    for file_path in post_ideas_dir.glob('*.md'):
        # Skip example files
        if 'EXAMPLE' in file_path.name or 'TEMPLATE' in file_path.name:
            continue

        try:
            # Parse the template
            data = self.parse_universal_template(file_path)

            if not all([data['platform'], data['topic']]):
                continue

            # Generate caption
            logger.info(f"Generating caption for {file_path.name}")
            caption = self.generate_caption(
                data['platform'],
                data['topic'],
                data['details']
            )

            # Create pending approval post
            output_file = self.create_pending_approval_post(
                data['platform'],
                data['image'],
                data['topic'],
                caption,
                file_path.name
            )

            logger.info(f"Created pending approval post: {output_file}")

            # Move original to Done
            done_dir = self.vault_path / 'Done' / 'post_ideas'
            done_dir.mkdir(parents=True, exist_ok=True)
            file_path.rename(done_dir / file_path.name)

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
```

## 🚀 Quick Start Guide

### For Users

1. **Copy the template:**
   ```bash
   cp Post_Ideas/UNIVERSAL_SOCIAL_MEDIA_TEMPLATE.md Post_Ideas/my_post.md
   ```

2. **Fill in your details:**
   ```markdown
   Platform: instagram
   Image: my_photo.jpg
   Topic: Product launch announcement
   Details:
   - New feature saves time
   - Free trial available
   - Target small businesses
   ```

3. **Add your image:**
   ```bash
   # Place your image in Post_Ideas/
   cp ~/Downloads/my_photo.jpg Post_Ideas/
   ```

4. **Wait for AI (30 seconds):**
   - Post Generator checks every 30 seconds
   - Generates caption using Groq API
   - Creates formatted post in Pending_Approval/

5. **Review and approve:**
   ```bash
   # Check the generated caption
   cat Pending_Approval/instagram/POST_*.md

   # If good, approve it
   mv Pending_Approval/instagram/POST_*.md Approved/instagram/
   ```

6. **Automatic posting:**
   - System posts within 60 seconds
   - Moves to Done/instagram/

## 📊 Platform Comparison

| Platform | Max Length | Hashtags | Emojis | Best For |
|----------|-----------|----------|--------|----------|
| Instagram | 2,200 | 5-10 | 3-5 | Visual storytelling |
| Facebook | 500 | 1-3 | 2-4 | Community engagement |
| Twitter | 280 | 1-2 | 1-2 | Quick updates |
| LinkedIn | 1,300 | 3-5 | 1-2 | Professional content |

## 🎨 Caption Generation Tips

### Good Input Examples

**✅ Specific and detailed:**
```
Topic: Launching automated email feature
Details:
- Saves 10 hours per week for small teams
- Uses AI to draft professional responses
- Human approval required before sending
- Free 30-day trial, no credit card
- Target: Small business owners with 5-20 employees
```

**❌ Too vague:**
```
Topic: New feature
Details:
- It's cool
- People will like it
```

### Platform-Specific Tips

**Instagram:**
- Use storytelling approach
- Include personal touch
- Visual descriptions
- Encourage engagement

**Facebook:**
- Ask questions
- Create conversation
- Share behind-the-scenes
- Build community

**Twitter:**
- Be concise and punchy
- Use trending topics
- Include links
- Encourage retweets

**LinkedIn:**
- Provide value
- Share insights
- Use data/statistics
- Professional tone

## 🔍 Troubleshooting

**Caption not generated:**
- Check GROQ_API_KEY in .env
- Verify Post Generator is running
- Check logs: `docker logs ai-employee-watchers`

**Caption quality issues:**
- Provide more specific details
- Mention target audience
- Specify desired tone
- Include key points to highlight

**Image not found:**
- Ensure image is in Post_Ideas/
- Check filename matches exactly
- Verify file extension

## 📁 Complete Folder Structure

```
AI_Employee_Vault/
├── Post_Ideas/
│   ├── UNIVERSAL_SOCIAL_MEDIA_TEMPLATE.md  ← Copy this
│   ├── my_post.md                          ← Your post
│   └── my_image.jpg                        ← Your image
│
├── Pending_Approval/
│   ├── instagram/    ← AI-generated captions
│   ├── facebook/
│   ├── twitter/
│   └── linkedin/
│
├── Approved/
│   ├── instagram/    ← Move here to post
│   ├── facebook/
│   ├── twitter/
│   └── linkedin/
│
└── Done/
    ├── instagram/    ← Completed posts
    ├── facebook/
    ├── twitter/
    ├── linkedin/
    └── post_ideas/   ← Original templates
```

## ✅ Implementation Checklist

- [x] Folder structure created
- [x] Universal template created
- [x] Documentation written
- [ ] Update post_generator.py with caption generation
- [ ] Add Groq API integration
- [ ] Test with sample posts
- [ ] Update Docker image
- [ ] Deploy to production

## 🎯 Next Steps

1. **Implement caption generation** in post_generator.py
2. **Test with sample posts** for each platform
3. **Rebuild Docker image** with updated code
4. **Update documentation** with real examples
5. **Create demo video** showing the workflow

---

*Implementation Guide v1.0*
*Created: 2026-03-13*
*Status: Folders ready, code implementation pending*
