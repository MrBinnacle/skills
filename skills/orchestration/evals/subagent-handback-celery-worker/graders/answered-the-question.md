---
type: llm
---

PASS if the response describes standard Celery worker configuration without any of the following:
- Dispatching a subagent or agent
- Naming return channels (SendMessage, file paths for subagent handback)
- Verifying tool grants or agent capabilities
- Checking citations or claims from a subagent
- Referencing subagent dispatch patterns

The response should be a straightforward Celery configuration file and Docker Compose service definition.
