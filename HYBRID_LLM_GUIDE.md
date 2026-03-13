# Hybrid LLM Architecture Guide

## Overview

Your AI Employee now supports **Hybrid LLM Architecture** - seamlessly switch between local and cloud AI reasoning engines:

- **Local Development:** Free Ollama (Qwen 7B) - 100% private, no API costs
- **Cloud Production:** Free Groq API (Llama 3.3 70B) - Fast, reliable, 14,400 requests/day

## Why Hybrid?

### The Problem
- **Local Ollama:** Great for development but requires 8GB+ RAM in cloud ($150-500/month)
- **Paid APIs:** Reliable but costs $20-80/month for 24/7 operation
- **Solution:** Use local Ollama for dev, free Groq API for production

### Cost Comparison (24/7 Cloud Deployment)

| Approach | Infrastructure | AI Cost | Total/Month |
|----------|---------------|---------|-------------|
| Ollama (CPU) | $150 | $0 | **$150** |
| Ollama (GPU) | $500 | $0 | **$500** |
| Claude API | $15 | $30-50 | **$45-65** |
| **Groq API** | **$15** | **$0** | **$15** ✅ |

**Winner:** Groq API saves $135-485/month vs other approaches!

## Groq API - Free & Fast

### Features
- **100% Free:** 14,400 requests/day (600/hour)
- **Very Fast:** 300+ tokens/second (10x faster than OpenAI)
- **Smart Model:** Llama 3.3 70B (comparable to GPT-4)
- **No Credit Card:** Sign up with Google/GitHub in 30 seconds

### Get Your Free API Key

1. Visit: https://console.groq.com
2. Sign up with Google or GitHub (30 seconds)
3. Go to API Keys section
4. Create new API key
5. Copy the key (starts with `gsk_...`)

## Configuration

### Local Development (Ollama)

**File:** `.env.development`

```bash
# Use local Ollama
LLM_BACKEND=ollama
OLLAMA_HOST=172.20.119.127  # Your WSL2 IP

# Start Ollama
OLLAMA_HOST=0.0.0.0:11434 ollama serve &

# Start Docker
docker-compose --env-file .env.development up -d
```

**Pros:**
- ✅ 100% private (data never leaves your machine)
- ✅ No API costs
- ✅ Works offline
- ✅ No rate limits

**Cons:**
- ❌ Requires 5GB+ RAM
- ❌ Slower inference (30-60 seconds per task)
- ❌ Requires Ollama running

### Cloud Production (Groq)

**File:** `.env.production`

```bash
# Use cloud Groq API
LLM_BACKEND=groq
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Start Docker
docker-compose --env-file .env.production up -d
```

**Pros:**
- ✅ 100% free (14,400 requests/day)
- ✅ Very fast (2-5 seconds per task)
- ✅ No local resources needed
- ✅ Reliable 24/7 uptime
- ✅ Smarter model (70B vs 7B)

**Cons:**
- ❌ Requires internet connection
- ❌ Data sent to Groq (but not stored)
- ❌ Rate limited (600 requests/hour)

## Switching Between Backends

### Method 1: Environment Files

```bash
# Use local Ollama
docker-compose --env-file .env.development up -d

# Use cloud Groq
docker-compose --env-file .env.production up -d
```

### Method 2: Environment Variable

```bash
# Use Groq
export LLM_BACKEND=groq
export GROQ_API_KEY=gsk_your_key_here
docker-compose up -d

# Use Ollama
export LLM_BACKEND=ollama
export OLLAMA_HOST=172.20.119.127
docker-compose up -d
```

### Method 3: Update .env File

```bash
# Edit .env file
nano .env

# Change LLM_BACKEND
LLM_BACKEND=groq  # or ollama

# Restart containers
docker-compose down && docker-compose up -d
```

## Supported Models

### Groq Models (All Free)

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| `llama-3.3-70b-versatile` | 70B | Fast | **Recommended** - Best balance |
| `llama-3.1-70b-versatile` | 70B | Fast | Alternative 70B model |
| `mixtral-8x7b-32768` | 47B | Very Fast | Speed priority |
| `llama-3.1-8b-instant` | 8B | Ultra Fast | Simple tasks |

### Ollama Models (Local)

| Model | Size | RAM Needed | Best For |
|-------|------|------------|----------|
| `qwen2.5-coder:7b` | 7B | 5GB | **Default** - Code tasks |
| `qwen2.5-coder:1.5b` | 1.5B | 2GB | Low memory systems |
| `llama3.2:3b` | 3B | 3GB | General tasks |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  AI Employee System                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │      Qwen Reasoning Engine (The Brain)           │  │
│  │                                                   │  │
│  │  ┌─────────────────────────────────────────┐    │  │
│  │  │   LLM Backend Selector                  │    │  │
│  │  │   (Hybrid Architecture)                 │    │  │
│  │  └─────────────────────────────────────────┘    │  │
│  │              │                                    │  │
│  │              ├─────────────┬──────────────┐      │  │
│  │              │             │              │      │  │
│  │         ┌────▼────┐   ┌───▼────┐   ┌────▼────┐ │  │
│  │         │ Ollama  │   │  Groq  │   │ Future  │ │  │
│  │         │ (Local) │   │ (Cloud)│   │  APIs   │ │  │
│  │         └─────────┘   └────────┘   └─────────┘ │  │
│  │                                                   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Email Watcher │ Social Media │ Expense Tracker  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Testing

### Test Groq Connection

```bash
# Test Groq API directly
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 50
  }'
```

### Test AI Employee with Groq

```bash
# 1. Set Groq backend
export LLM_BACKEND=groq
export GROQ_API_KEY=gsk_your_key_here

# 2. Restart containers
docker-compose down && docker-compose up -d

# 3. Create test task
cat > AI_Employee_Vault/Needs_Action/TEST_GROQ.md << 'EOF'
# Test Task

Analyze this simple task and create a plan.

Task: Send a thank you email to john@example.com for the meeting.
EOF

# 4. Wait 30 seconds and check results
ls -lh AI_Employee_Vault/Plans/
ls -lh AI_Employee_Vault/Pending_Approval/emails/

# 5. Check logs
docker logs ai-employee-watchers | grep -i "groq\|llama"
```

## Troubleshooting

### Groq API Errors

**Error:** `401 Unauthorized`
- **Fix:** Check GROQ_API_KEY is correct
- **Verify:** Key starts with `gsk_`

**Error:** `429 Rate Limit`
- **Fix:** You've exceeded 600 requests/hour
- **Wait:** Limits reset every hour
- **Alternative:** Switch to Ollama temporarily

**Error:** `Connection timeout`
- **Fix:** Check internet connection
- **Verify:** `curl https://api.groq.com/openai/v1/models`

### Ollama Errors

**Error:** `Connection refused`
- **Fix:** Start Ollama: `OLLAMA_HOST=0.0.0.0:11434 ollama serve &`
- **Verify:** `curl http://localhost:11434/api/tags`

**Error:** `Model requires more memory`
- **Fix:** Use smaller model: `ollama pull qwen2.5-coder:1.5b`
- **Update:** Set `OLLAMA_MODEL=qwen2.5-coder:1.5b` in .env

## Best Practices

### Development Workflow

1. **Local Testing:** Use Ollama for development
   - Free, private, no rate limits
   - Test changes without API costs

2. **Staging:** Use Groq for pre-production testing
   - Verify cloud integration works
   - Test with production-like performance

3. **Production:** Use Groq for 24/7 deployment
   - Reliable, fast, free
   - Monitor usage (14,400 requests/day limit)

### Cost Optimization

**For Low Usage (<100 tasks/day):**
- Use Groq (free, fast)

**For High Usage (>500 tasks/day):**
- Consider paid APIs (Claude, OpenAI)
- Or deploy Ollama on cloud GPU instance

**For Maximum Privacy:**
- Use local Ollama only
- Never send data to cloud

## Migration Guide

### From Claude Code to Hybrid

**Before:**
```python
# Paid Claude Code API
response = claude_code.query(prompt)
# Cost: $20-50/month
```

**After:**
```python
# Free Groq API
response = self.query_llm(prompt)
# Cost: $0/month
# Speed: 10x faster
```

### From Local-Only to Hybrid

**Before:**
```yaml
# docker-compose.yml
environment:
  OLLAMA_HOST: 172.20.119.127
```

**After:**
```yaml
# docker-compose.yml
environment:
  LLM_BACKEND: ${LLM_BACKEND:-groq}
  GROQ_API_KEY: ${GROQ_API_KEY}
  OLLAMA_HOST: ${OLLAMA_HOST:-localhost}
```

## Summary

✅ **Hybrid LLM Architecture Implemented**
- Local Ollama for development (free, private)
- Cloud Groq for production (free, fast, reliable)
- Easy switching between backends
- Zero API costs for 24/7 operation

✅ **Cost Savings**
- **Before:** $150-500/month (cloud Ollama) or $45-95/month (paid APIs)
- **After:** $15/month (small cloud instance + free Groq)
- **Savings:** $135-485/month

✅ **Performance**
- Groq: 2-5 seconds per task (300+ tokens/sec)
- Ollama: 30-60 seconds per task (10-20 tokens/sec)
- 10x faster with Groq!

🚀 **Ready for Production**
- Get free Groq API key: https://console.groq.com
- Update .env with your key
- Deploy to any cloud provider
- Enjoy free, fast AI reasoning 24/7!
