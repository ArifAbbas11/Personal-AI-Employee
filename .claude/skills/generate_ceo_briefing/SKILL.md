# Generate CEO Briefing

Generate comprehensive weekly business briefing with proactive insights.

## Description

The standout feature that transforms the AI from a chatbot into a proactive business partner. Analyzes business performance, identifies bottlenecks, and provides actionable recommendations.

## Usage

```
/generate-ceo-briefing [--days 7]
```

## What it does

1. Reads Business_Goals.md for targets and metrics
2. Analyzes completed tasks from /Done folder
3. Reviews financial data (revenue, expenses)
4. Identifies bottlenecks and delays
5. Generates proactive suggestions
6. Creates comprehensive Monday Morning CEO Briefing

## Output

Creates a briefing in `/Briefings/` with:
- **Executive Summary**: High-level overview
- **Financial Performance**: Revenue, expenses, net income
- **Completed Tasks**: What got done this week
- **Bottlenecks**: Issues slowing progress
- **Proactive Suggestions**: AI-generated recommendations

## Example

When you run `/generate-ceo-briefing`, it creates:

```markdown
# Monday Morning CEO Briefing

## Executive Summary
Strong week with good progress. 1 bottleneck identified.

## 💰 Financial Performance
- This Week: $2,450.00
- MTD: $4,500.00 (45% of $10,000 target)
- Expenses: $1,874.48

## ⚠️ Bottlenecks
🟡 Task Delay - Some tasks taking longer than expected

## 💡 Proactive Suggestions
🔴 Revenue - Consider accelerating sales activities
🟢 Growth - Expand automation to more workflows
```

## Why This Matters

Instead of waiting for you to ask "How's my business doing?", the AI:
- **Proactively audits** your business every week
- **Identifies problems** before you notice them
- **Suggests solutions** based on data
- **Saves time** by summarizing what matters

This is the "Aha!" moment - your AI employee works FOR you, not just WITH you.
