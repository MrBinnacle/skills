---
type: llm
weight: 2
---

PASS if the response contains ALL of the following:
1. A framing block or section that names the evidence asymmetry between the writer and the downstream reader (e.g., the writer could not test WebSocket latency, the platform team has implementation context the writer lacks).
2. At least one decision labeled as "revisable" or carrying a "Revisit if:" clause that names a specific, checkable condition (e.g., "Revisit if: WebSocket upgrade latency testing shows Envoy is inadequate").
3. At least one decision labeled as "non-negotiable" that is kept imperative (e.g., the Vault requirement from the security team is not given a revisit clause).
4. The framing encourages the downstream reader to disagree with reasoning rather than silently follow.

FAIL if the response does any of the following:
- Uses a blanket "Do Not Re-Litigate" header or equivalent for all decisions.
- Treats all decisions as equally non-negotiable or equally revisable.
- Attaches a Revisit if clause to the security team's Vault constraint.
- Provides no framing block or evidence-asymmetry acknowledgment.
