import json
import os
import shutil
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from git import Repo
from pydantic import BaseModel

# Ensure the code_search module can be found
sys.path.append(str(Path(__file__).resolve().parent))

from code_search.parser import main as parser_main
from memvid_sdk import use
from memvid_store import ingest_to_memvid

app = FastAPI()

# In-memory cache for loaded memory
loaded_memory = None

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)


class Repository(BaseModel):
    repo_url: str


def get_repo_name_from_url(url: str) -> str:
    return Path(url).stem


def get_result_snippets(results: dict) -> list:
    snippets = []
    if not results or "hits" not in results:
        return []

    for hit in results["hits"]:
        snippet = hit.get("snippet", "")
        snippets.append(snippet)

    return snippets


@app.post("/repository")
async def index_repository(repository: Repository):
    repo_name = get_repo_name_from_url(repository.repo_url)
    repo_dir = DATA_DIR / repo_name
    memory_file = DATA_DIR / f"{repo_name}.mv2"

    if repo_dir.exists():
        shutil.rmtree(repo_dir)
    repo_dir.mkdir()

    try:
        # 1. Clone the repository
        print(f"Cloning {repository.repo_url} into {repo_dir}...")
        Repo.clone_from(repository.repo_url, repo_dir)
        print("Clone successful.")

        # 2. Run parsers
        print("Parsing repository...")
        repo_str = str(repo_dir)

        original_argv = sys.argv
        sys.argv = ["", repo_str]
        parser_main()

        sys.argv = original_argv
        print("Parsing complete.")

        # 3. Ingest to Memvid
        print("Ingesting into Memvid...")
        code_snippets_path = DATA_DIR / "code_snippets.jsonl"

        ingest_to_memvid(code_snippets_path, str(memory_file))
        print(f"Ingestion complete. Memory file saved to {memory_file}")

        # Clean up intermediate files
        if code_snippets_path.exists():
            os.remove(code_snippets_path)

        return {"message": f"Repository {repo_name} indexed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if repo_dir.exists():
            shutil.rmtree(repo_dir)


@app.post("/repository/open/{repo_name}")
async def open_repository(repo_name: str):
    global loaded_memory
    if loaded_memory is not None:
        loaded_memory.close()

    memory_file = DATA_DIR / f"{repo_name}.mv2"
    if not memory_file.exists():
        raise HTTPException(
            status_code=404, detail="Repository not found or not indexed yet."
        )

    try:
        mem = use("basic", str(memory_file))
        loaded_memory = mem
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load memory: {e}")


@app.get("/repository/query")
async def query_repository(q: str):
    global loaded_memory
    if loaded_memory is None:
        raise HTTPException(status_code=500, detail=f"No memory is loaded: {e}")

    try:
        results = loaded_memory.find(q)
        formatted_results = get_result_snippets(results)
        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during search: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
