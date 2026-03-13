# Universal Social Media Post Template

**How to use:** Fill in the fields below, save this file in `Post_Ideas/`, and the AI will automatically generate a platform-optimized caption and move it to Pending_Approval for your review.

---

## Post Details

**Platform:** instagram
<!-- Options: instagram, facebook, twitter, linkedin -->

**Image:** demo_screenshot.jpg
<!-- Place your image in Post_Ideas/ folder. Supported: .jpg, .png, .gif -->

**Topic:** AI automation for small businesses

**Details:**
- Focus on cost savings and efficiency
- Mention email automation capabilities
- Highlight 24/7 operation
- Keep tone professional but friendly
- Target audience: small business owners

---

## AI Instructions

The AI will:
1. ✅ Read your Platform, Image, Topic, and Details
2. ✅ Generate platform-optimized caption with:
   - Appropriate length (Instagram: 2200 chars, Twitter: 280 chars, etc.)
   - Platform-specific hashtags
   - Engaging emojis
   - Call-to-action
3. ✅ Create formatted post in Pending_Approval/{platform}/
4. ✅ Wait for your approval before posting

---

## Platform-Specific Guidelines

### Instagram
- Caption: Up to 2,200 characters
- Hashtags: 5-10 relevant hashtags
- Emojis: 3-5 emojis for engagement
- Image: Required (1080x1080 or 1080x1350)
- Tone: Visual, engaging, story-driven

### Facebook
- Caption: Up to 63,206 characters (but keep under 500 for best engagement)
- Hashtags: 1-3 hashtags (less important than Instagram)
- Emojis: 2-4 emojis
- Image: Optional but recommended (1200x630)
- Tone: Conversational, community-focused

### Twitter
- Caption: 280 characters max
- Hashtags: 1-2 hashtags
- Emojis: 1-2 emojis
- Image: Optional (1200x675)
- Tone: Concise, punchy, timely

### LinkedIn
- Caption: Up to 3,000 characters (but keep under 1,300 for best engagement)
- Hashtags: 3-5 professional hashtags
- Emojis: Minimal (1-2, professional only)
- Image: Optional (1200x627)
- Tone: Professional, value-driven, educational

---

## Examples

### Example 1: Product Launch (Instagram)

```
Platform: instagram
Image: product_launch.png
Topic: Launching new AI Employee feature
Details:
- Announce automated email response feature
- Highlight time savings (10 hours/week)
- Mention free trial
- Create excitement and urgency
- Include link to website
```

**AI will generate:**
```
🚀 BIG NEWS! We're launching our AI Employee's newest feature!

✨ Automated Email Responses
⏰ Save 10+ hours every week
🤖 Smart, professional replies
💰 Free 30-day trial

Imagine never worrying about inbox overload again. Our AI reads, understands, and drafts perfect responses while you focus on what matters.

Ready to reclaim your time? 👆 Link in bio!

Try it free for 30 days - no credit card required.

#AIAutomation #ProductLaunch #EmailAutomation #SmallBusiness #Productivity #TimeManagement #BusinessTools #Startup #Innovation #TechNews
```

### Example 2: Behind the Scenes (Facebook)

```
Platform: facebook
Image: team_working.jpg
Topic: Behind the scenes at our office
Details:
- Show human side of the company
- Mention team collaboration
- Highlight company culture
- Encourage engagement with question
- Keep it warm and personal
```

**AI will generate:**
```
☕ A peek behind the curtain!

This is where the magic happens - our team hard at work building tools that make YOUR life easier.

From brainstorming sessions over coffee to late-night coding marathons, every feature we build starts with one question: "How can we help small businesses thrive?"

We're not just building software. We're building solutions for real people with real challenges.

What's the biggest challenge in YOUR business right now? Drop a comment - we'd love to hear from you! 👇

#BehindTheScenes #TeamWork #StartupLife
```

### Example 3: Quick Tip (Twitter)

```
Platform: twitter
Image: tip_graphic.png
Topic: Productivity tip for entrepreneurs
Details:
- Share actionable tip about email management
- Keep it punchy and valuable
- Encourage retweets
- Link to blog post
```

**AI will generate:**
```
⚡ Productivity hack: Batch process emails 2x daily instead of constantly checking.

Result? 3+ hours saved per week.

Our AI Employee does this automatically 🤖

Try it: [link]

#ProductivityTip #Entrepreneur
```

### Example 4: Case Study (LinkedIn)

```
Platform: linkedin
Image: results_chart.png
Topic: Customer success story
Details:
- Share specific results (50% time savings)
- Mention industry (consulting)
- Keep professional tone
- Include credibility markers
- Encourage discussion
```

**AI will generate:**
```
📊 Real Results: How a Consulting Firm Saved 20 Hours Per Week

We recently worked with a 5-person consulting firm struggling with email overload. Their challenge? Spending 4 hours daily on routine client communications.

The Solution:
✅ Automated email categorization
✅ AI-drafted responses for common queries
✅ Human approval for all outgoing messages

The Results:
• 50% reduction in email processing time
• 20 hours/week saved across the team
• 100% client satisfaction maintained
• ROI achieved in 3 weeks

Key Takeaway: Automation doesn't replace human judgment - it amplifies it. The team now spends their time on strategic work, not inbox management.

What's your biggest time drain in client communications? Let's discuss in the comments.

#CaseStudy #BusinessAutomation #Consulting #Productivity #AIinBusiness
```

---

## Workflow

### Step 1: Create Your Post
Save this file as `Post_Ideas/MY_POST_NAME.md` with your details filled in.

### Step 2: Add Your Image
Place your image in `Post_Ideas/` folder:
```
Post_Ideas/
├── MY_POST_NAME.md
└── my_image.jpg
```

### Step 3: AI Generates Caption
The Post Generator watcher will:
- Read your file
- Generate platform-optimized caption
- Create formatted post in `Pending_Approval/{platform}/`

### Step 4: Review & Approve
Check `Pending_Approval/{platform}/` for your generated post.
Edit if needed, then move to `Approved/{platform}/`

### Step 5: Automatic Posting
System posts automatically and moves to `Done/{platform}/`

---

## Tips for Better AI-Generated Captions

### Be Specific in Details
❌ Bad: "Make it engaging"
✅ Good: "Target small business owners, focus on time savings, use friendly tone"

### Provide Context
❌ Bad: "New feature"
✅ Good: "Launching automated email responses that save 10 hours/week for small teams"

### Mention Target Audience
❌ Bad: "Everyone"
✅ Good: "Small business owners with 5-20 employees struggling with email overload"

### Include Key Points
❌ Bad: "Talk about our product"
✅ Good: "Highlight: 24/7 operation, human oversight, 30-day free trial, no credit card"

### Specify Tone
❌ Bad: "Make it good"
✅ Good: "Professional but approachable, emphasize trust and reliability"

---

## Folder Structure

```
AI_Employee_Vault/
├── Post_Ideas/              ← Create posts here
│   ├── MY_POST.md          ← Your post details
│   └── my_image.jpg        ← Your image
│
├── Pending_Approval/        ← AI-generated posts for review
│   ├── instagram/
│   ├── facebook/
│   ├── twitter/
│   └── linkedin/
│
├── Approved/                ← Move here to post
│   ├── instagram/
│   ├── facebook/
│   ├── twitter/
│   └── linkedin/
│
└── Done/                    ← Completed posts
    ├── instagram/
    ├── facebook/
    ├── twitter/
    └── linkedin/
```

---

## Quick Start

1. **Copy this template** to `Post_Ideas/my_first_post.md`
2. **Fill in:** Platform, Image, Topic, Details
3. **Add image** to `Post_Ideas/` folder
4. **Wait** for AI to generate caption (checks every 30 seconds)
5. **Review** in `Pending_Approval/{platform}/`
6. **Approve** by moving to `Approved/{platform}/`
7. **Done!** System posts automatically

---

*Template Version: 1.0*
*Created: 2026-03-13*
*Supports: Instagram, Facebook, Twitter, LinkedIn*
