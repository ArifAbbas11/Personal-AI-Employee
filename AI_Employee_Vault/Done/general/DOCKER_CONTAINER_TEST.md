---
type: test
priority: high
created: 2026-03-12
---

# Docker Container Test

This task verifies Ralph Groq is working inside the Docker container.

## Steps

1. Read this file
2. Create log: echo "Ralph Groq working in Docker!" > /vault/Logs/docker_test.log
3. Move this file to Done/

## Success Criteria

- Log file created in /vault/Logs/
- This file moved to /vault/Done/
