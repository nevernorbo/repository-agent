import os
import shutil
import subprocess
from typing import Dict, List

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from code_search.repo_searcher import RepoSearcher
from code_search.searcher import CombinedSearcher

app = FastAPI()
origins = [
    "http://localhost:3000",  # Common React port
    "http://localhost:8100",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies and auth headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

searcher = CombinedSearcher()
repo_searcher = RepoSearcher()

from typing import Dict, List, Any
import time
from pathlib import Path

# ... existing code up to RepoSearcher ...

indexing_status: Dict[str, Any] = {}

def count_repo_stats(repo_path: str) -> Dict[str, int]:
    p = Path(repo_path)
    if not p.exists():
        return {"file_count": 0, "loc": 0}
    file_count = 0
    loc = 0
    for f in p.rglob("*"):
        if f.is_file() and f.suffix in {".py", ".js", ".jsx", ".ts", ".tsx", ".cs"}:
            file_count += 1
            try:
                loc += sum(1 for _ in f.open("r", encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return {"file_count": file_count, "loc": loc}

@app.get("/api/repositories", response_model=List[str])
async def get_repositories():
    """
    Returns a distinct list of all indexed repository names
    across both Code and NLU collections.
    """
    try:
        # In a real production app, you might want to clear this cache
        # when a new repo finishes indexing.
        repos = list(repo_searcher.get_unique_repositories())
        return repos
    except Exception as e:
        # Log the error for debugging (standard for software engineers)
        print(f"Error fetching from Qdrant: {e}")
        return []


def wrapped_indexing_pipeline(path: str, repo_name: str):
    stats = count_repo_stats(path)
    indexing_status[repo_name] = {"status": "indexing", "times": {}, "stats": stats}
    try:
        run_indexing_pipeline(path, repo_name)
        indexing_status[repo_name]["status"] = "completed"
    except Exception as e:
        if isinstance(indexing_status.get(repo_name), dict):
            indexing_status[repo_name]["status"] = f"failed: {str(e)}"
        else:
            indexing_status[repo_name] = {"status": f"failed: {str(e)}", "times": {}, "stats": stats}


def run_indexing_pipeline(repo_path: str, repo_name):
    """
    Equivalent to index_qdrant.sh.
    Executes the Python indexing modules in the correct sequence.
    """
    env = os.environ.copy()
    env["REPO_PATH"] = repo_path
    env["REPO_NAME"] = repo_name

    # List of modules to run in order
    modules = [
        "code_search.index.files_to_json",
        "code_search.index.parser_for_code",
        "code_search.index.upload_code",
        "code_search.index.upload_code_hybrid",
        "code_search.index.parser_for_nl",
        "code_search.index.upload_signatures",
        "code_search.index.upload_signatures_hybrid",
    ]

    try:
        for module in modules:
            print(f"Running indexing step: {module}...")
            start_t = time.time()
            # We pass repo_path as an argument to match the original shell script
            subprocess.run(["python3", "-m", module, repo_path], check=True, env=env)
            elapsed = time.time() - start_t
            if isinstance(indexing_status.get(repo_name), dict):
                indexing_status[repo_name]["times"][module] = elapsed
        print("Indexing completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Indexing failed at step {e.cmd}: {e}")
        raise e
    finally:
        # Cleanup: Equivalent to 'rm -rf' in download_and_index.sh
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)


class IndexRequest(BaseModel):
    repo_name: str


@app.post("/api/index")
async def index_repository(background_tasks: BackgroundTasks, request: IndexRequest):
    """
    Equivalent to download_and_index.sh logic.
    Clones the repo and triggers background indexing.
    """
    TMP_REPO_DIR = "/tmp/" + request.repo_name

    if os.path.exists(TMP_REPO_DIR):
        shutil.rmtree(TMP_REPO_DIR)

    repo_url = f"https://github.com/{request.repo_name}"

    try:
        # Clone the repository
        subprocess.run(["git", "clone", repo_url, TMP_REPO_DIR], check=True)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to clone repository")

    # Run the heavy indexing work in the background to avoid blocking the API
    indexing_status[request.repo_name] = "cloned"
    background_tasks.add_task(
        wrapped_indexing_pipeline, TMP_REPO_DIR, request.repo_name
    )

    return {"message": "cloning successful, indexing started"}


@app.get("/api/index/status/{repo_name:path}")
async def get_status(repo_name: str):
    status_data = indexing_status.get(repo_name, {"status": "not_started", "times": {}})
    if isinstance(status_data, str):
        status_data = {"status": status_data, "times": {}}
    return {"repo_name": repo_name, **status_data}


@app.get("/api/search")
def search(query: str, repo_name: str):
    return {"result": searcher.search(query, repo_name, limit=5)}

from code_search.searcher import HybridCombinedSearcher
hybrid_searcher = HybridCombinedSearcher()

@app.get("/api/search_hybrid")
def search_hybrid(query: str, repo_name: str):
    return {"result": hybrid_searcher.search(query, repo_name, limit=5)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
