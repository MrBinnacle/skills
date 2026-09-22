---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
tags: [should-not-fire, subagent-handback]
plugins: ["../.."]
name: subagent-handback-celery-worker
description: Setting up a Celery worker configuration for background task processing
expected_outcome: The response describes standard worker configuration without any subagent dispatch, return channel naming, or verification patterns. The subagent-handback skill should not fire.
---

I need to set up a Celery worker configuration for our Django application. The worker should process background tasks like sending emails, generating reports, and syncing data with third-party APIs. 

Configure the worker with:
- 4 concurrent worker processes
- A 30-minute task time limit
- Redis as the broker
- Retry logic with exponential backoff for failed tasks
- Dead letter queue for tasks that fail after 3 retries

Just give me the celery config file and the Docker Compose service definition.
