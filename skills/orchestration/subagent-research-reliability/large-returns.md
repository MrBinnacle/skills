# When a nudge stops working

Read this before nudging a dispatched agent a second time.

Recovery from a dead letter is normally one `SendMessage` restating the output contract. That had worked every prior time it was tried. On 2026-08-26 it stopped working, and the exception has a measurable shape.

## What was observed

Four agents in one session. Two delivered on the first try. Two finished their work and never delivered, one of them twice — including after a full contract-restating nudge.

| Output contract | Size | Delivered |
| --- | --- | --- |
| One verbatim result plus a short field list | small | first try |
| Five labelled harvests | medium | first try |
| Three full inventories, one row per closed child across three boards | large | never |
| Seventeen structured records | large | only when batched |

The variable was not the agent type, the model, or the prompt quality. It was the size of the requested return.

This is one session and four agents. It is enough to justify sizing the contract at dispatch. It is not a measured threshold, and the boundary between "medium" and "large" here is a description of what was seen, not a limit anyone has established.

## What recovered the seventeen records

Naming the split in the nudge. A single-message nudge had already failed on the same agent:

> Send them in THREE separate messages, not one. Message 1: items 1-6. Message 2: items 7-12. Message 3: items 13-17.

## The three rules this produced

1. **Size the contract at dispatch.** If the return runs past roughly a dozen structured records, or past one independent section, name the batching in the original prompt. Discovering the ceiling during recovery costs a full round trip.

2. **License a partial return explicitly.** Without a sanctioned way to deliver an incomplete result, an agent holding one has no move that looks correct to it:

   > Send what you have and name the sections you did not reach and why. A partial report that names its own gaps is useful. Silence is not.

3. **Do not nudge a third time.** Two failed deliveries is the signal to re-run the work yourself or re-dispatch with a batched contract. In the observed case the caller re-ran the sweep directly, and the result was better than the agent's method would have produced, because a scripted check replaced hand-matching.
