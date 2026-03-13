# Instagram Posting Guide - Easy Image Workflow

## 📸 Current Status

**Instagram posting is NOT yet implemented in the system.**

The social_media_auto_poster.py currently only supports:
- ✅ LinkedIn (text posts)
- ✅ Twitter/X (text posts)
- ❌ Instagram (needs implementation)

## 🎯 Proposed Easy Workflow (When Implemented)

### Step 1: Create Your Post

Create a file in `Post_Ideas/` folder:

**Example: `Post_Ideas/MY_INSTAGRAM_POST.md`**

```markdown
---
platform: instagram
image: my_photo.jpg
status: draft
---

# Instagram Post

## Caption

🤖 Excited to share our AI Employee system!

This autonomous assistant handles:
✅ Email monitoring
✅ Response drafting
✅ Social media management
✅ Business analytics

All with human oversight for important decisions.

Want to learn more? Link in bio! 👆

#AIAutomation #TechInnovation #SmallBusiness #Productivity

## Image

File: my_photo.jpg
Location: Same folder as this file

## Hashtags

#AIEmployee #Automation #BusinessTools #Innovation #TechStartup
#SmallBusinessTech #ProductivityHacks #AITools #WorkSmarter
```

### Step 2: Add Your Image

Simply place your image in the **same folder**:
```
Post_Ideas/
├── MY_INSTAGRAM_POST.md
└── my_photo.jpg          ← Your image here!
```

**Supported formats:**
- .jpg / .jpeg
- .png
- .gif (if Instagram supports it)

**Recommended size:**
- Square: 1080x1080 pixels
- Portrait: 1080x1350 pixels
- Landscape: 1080x566 pixels

### Step 3: Approve for Posting

When ready, move BOTH files to Approved:
```bash
# Move the post file
mv Post_Ideas/MY_INSTAGRAM_POST.md Approved/instagram/

# The system will automatically find the image in Post_Ideas/
# Or you can move the image too:
mv Post_Ideas/my_photo.jpg Approved/instagram/
```

### Step 4: Automatic Posting

The system will:
1. ✅ Read the post file
2. ✅ Find the referenced image
3. ✅ Upload image to Instagram
4. ✅ Post with your caption
5. ✅ Move to Done/instagram/

## 📝 Template Files

### Simple Template

```markdown
---
platform: instagram
image: photo.jpg
---

# My Post Title

## Caption

Your caption here with emojis! 🎉

#Hashtag1 #Hashtag2 #Hashtag3

## Image

File: photo.jpg
```

### Detailed Template

```markdown
---
platform: instagram
image: product_demo.png
alt_text: Screenshot of AI Employee dashboard
scheduled_time: 2026-03-15 10:00
status: draft
---

# Product Launch Post

## Caption

🚀 Launching our new AI Employee feature!

What's new:
✨ Automated email responses
📊 Real-time analytics dashboard
🤖 Smart task routing
⚡ 10x faster processing

Try it free for 30 days! Link in bio 👆

Questions? Drop them below! 👇

## Hashtags

#ProductLaunch #AIAutomation #NewFeature #TechNews
#StartupLife #Innovation #BusinessTools #Productivity

## Image Details

File: product_demo.png
Size: 1080x1080
Format: PNG
Alt Text: Dashboard showing AI Employee analytics

## Notes

- Post during peak hours (10 AM - 2 PM)
- Engage with comments within first hour
- Cross-post to Facebook if engagement is high
```

## 🔧 What Needs to Be Implemented

To make this work, the following needs to be added to `watchers/social_media_auto_poster.py`:

### 1. Instagram API Integration

```python
def post_to_instagram(self, content: str, image_path: str) -> dict:
    """Post content with image to Instagram"""
    try:
        from instagram_poster import InstagramPoster

        poster = InstagramPoster()
        result = poster.post_image(
            image_path=image_path,
            caption=content
        )

        return {
            'success': True,
            'post_id': result.get('id'),
            'platform': 'Instagram'
        }
    except Exception as e:
        logger.error(f"Error posting to Instagram: {e}")
        return {'success': False, 'error': str(e)}
```

### 2. Image File Detection

```python
def find_image_file(self, post_file: Path, image_filename: str) -> Path:
    """Find image file referenced in post"""
    # Check same directory as post file
    image_path = post_file.parent / image_filename
    if image_path.exists():
        return image_path

    # Check Post_Ideas directory
    post_ideas = self.vault_path / 'Post_Ideas'
    image_path = post_ideas / image_filename
    if image_path.exists():
        return image_path

    raise FileNotFoundError(f"Image not found: {image_filename}")
```

### 3. Parse Instagram Posts

```python
def parse_instagram_post(self, file_path: Path) -> dict:
    """Parse Instagram post with image reference"""
    content = file_path.read_text()

    # Extract metadata
    metadata = {}
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        yaml_content = content[3:yaml_end]
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()

    # Extract caption
    caption = ""
    lines = content.split('\n')
    in_caption = False
    for line in lines:
        if '## Caption' in line:
            in_caption = True
            continue
        elif in_caption and line.startswith('##'):
            break
        elif in_caption and line.strip():
            caption += line + '\n'

    return {
        'caption': caption.strip(),
        'image': metadata.get('image'),
        'platform': metadata.get('platform'),
        'metadata': metadata
    }
```

## 🚀 Quick Start (Once Implemented)

### Example 1: Simple Photo Post

**File: `Post_Ideas/team_photo.md`**
```markdown
---
platform: instagram
image: team.jpg
---

## Caption

Meet the team! 👋 #TeamPhoto #Startup
```

**Image: `Post_Ideas/team.jpg`**

**Approve:**
```bash
mv Post_Ideas/team_photo.md Approved/instagram/
```

### Example 2: Product Screenshot

**File: `Post_Ideas/feature_launch.md`**
```markdown
---
platform: instagram
image: dashboard_screenshot.png
---

## Caption

🎉 New feature alert!

Check out our redesigned dashboard with:
📊 Real-time analytics
⚡ Faster performance
🎨 Beautiful new UI

Try it now! Link in bio 👆

#ProductUpdate #NewFeature #Dashboard
```

**Image: `Post_Ideas/dashboard_screenshot.png`**

## 📋 Checklist for Instagram Posts

Before approving your post:

- [ ] Image file exists in Post_Ideas/ folder
- [ ] Image filename matches exactly (case-sensitive)
- [ ] Image is high quality (min 1080px width)
- [ ] Caption is under 2,200 characters
- [ ] Used 3-5 relevant emojis
- [ ] Added 5-10 hashtags
- [ ] Included call-to-action
- [ ] Checked for typos
- [ ] Image and post file ready to move to Approved/

## 🔍 Troubleshooting

**"Image not found" error:**
- Check filename spelling (case-sensitive!)
- Ensure image is in Post_Ideas/ folder
- Verify file extension (.jpg not .jpeg)

**"Post failed" error:**
- Check Instagram API credentials
- Verify image format is supported
- Ensure caption length is valid

**"No response" from system:**
- Check if social_media_auto_poster is running
- Verify Approved/instagram/ folder exists
- Check logs: `docker logs ai-employee-watchers`

## 📚 Additional Resources

**Instagram API Documentation:**
- https://developers.facebook.com/docs/instagram-api

**Image Best Practices:**
- Use high-resolution images (1080px+)
- Optimize file size (under 8MB)
- Use square format for best compatibility
- Add alt text for accessibility

**Caption Best Practices:**
- First 125 characters are most visible
- Use line breaks for readability
- Include 1-2 emojis per line
- Add hashtags at the end
- Include call-to-action

---

## ⚠️ Current Limitation

**Instagram posting is not yet implemented.** This guide provides the workflow and templates for when it IS implemented.

**To implement Instagram posting:**
1. Add Instagram API credentials to `.env`
2. Create `watchers/instagram_poster.py`
3. Update `watchers/social_media_auto_poster.py`
4. Add Instagram support to the posting workflow

**For now, you can:**
- ✅ Use LinkedIn and Twitter posting (fully working)
- ✅ Prepare Instagram posts using these templates
- ✅ Manually post to Instagram using the drafted content

---

*This guide will be updated once Instagram posting is implemented.*
