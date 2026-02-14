import json
import os
from pathlib import Path

from memvid_sdk import create, use


def ingest_to_memvid(code_jsonl, memory_file="repo_memory.mv2"):
    if os.path.exists(memory_file):
        mem = use("basic", memory_file, read_only=True)
    else:
        mem = create(memory_file)
    count = 0

    if Path(code_jsonl).exists():
        with open(code_jsonl, "r", encoding="utf-8") as code_file:
            for line in code_file:
                e = json.loads(line)
                mem.put(
                    title=e["file"],
                    label="code",
                    text=line,
                    metadata={},
                )
                count += 1

    print(f"Added {count} items into {memory_file}")
    return mem
