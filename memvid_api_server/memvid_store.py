import json
from pathlib import Path
import os
from memvid_sdk import use, create


def ingest_to_memvid(code_jsonl, nl_path, memory_file="repo_memory.mv2"):
    if os.path.exists(memory_file):
        mem = use("basic", memory_file)
        # return mem
    else:
        mem = create(memory_file)
    count = 0

    if Path(code_jsonl).exists():
        with open(code_jsonl, "r", encoding="utf-8") as code_file:
            for line in code_file:
                e = json.loads(line)
                text = f"{e['symbol_name']}\n{e['symbol_code']}"
                mem.put(
                    title=e["file"],
                    label="code",
                    text=text,
                    metadata={
                        "type": "syntactic",
                        "file": e["file"],
                        "line": e["start_line"],
                        "symbol_type": e["symbol_type"],
                    },
                )
                count += 1

    if Path(nl_path).exists():
        with open(nl_path, "r", encoding="utf-8") as code_file:
            for line in code_file:
                e = json.loads(line)
                doc = e.get("docstring") or ""
                text = f"Function: {e['name']}\nDocstring: {doc}\nSignature: {e['signature']}"
                mem.put(
                    title=e["context"]["file_path"],
                    label="nl",
                    text=text,
                    metadata={
                        "type": "semantic",
                        "file": e["context"]["file_path"],
                        "module": e["context"]["module"],
                    },
                )
                count += 1

    print(f"Added {count} items into {memory_file}")
    return mem
