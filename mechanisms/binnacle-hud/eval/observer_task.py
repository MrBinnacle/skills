"""Replays observer samples through a model with Inspect AI. No scorer yet: a person labels the
notes first (error analysis), and scoring is added afterwards with `inspect score`.

    bun mechanisms/binnacle-hud/eval/slices.ts <out> <transcripts...> --notes forwarded.jsonl
    inspect eval mechanisms/binnacle-hud/eval/observer_task.py -T samples=<out>/samples.jsonl \
        --model anthropic/claude-opus-5-5 --log-dir <out>/logs --log-format json
    bun mechanisms/binnacle-hud/eval/report.ts <out>/logs/<log>.json <out>/labels.md

The samples hold the system prompt and the observer's message exactly as observer.ts builds them,
so this file adds no prompt text of its own.
"""

from typing import Any

from inspect_ai import Task, task
from inspect_ai.dataset import Sample, json_dataset
from inspect_ai.model import ChatMessageSystem, ChatMessageUser, GenerateConfig
from inspect_ai.solver import generate


def record_to_sample(record: dict[str, Any]) -> Sample:
    roles = {"system": ChatMessageSystem, "user": ChatMessageUser}
    return Sample(
        id=record["id"],
        input=[roles[m["role"]](content=m["content"]) for m in record["input"]],
        metadata=record["metadata"],
    )


@task
def observer(samples: str) -> Task:
    return Task(
        dataset=json_dataset(samples, record_to_sample),
        solver=generate(),
        # Same knobs as index.ts: OUTPUT_TOKENS, and no prompt cache (cacheRetention "none").
        config=GenerateConfig(max_tokens=2000, cache_prompt=False),
    )
