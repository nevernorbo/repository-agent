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

indexing_status: Dict[str, str] = {}


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
    indexing_status[repo_name] = "indexing"
    try:
        run_indexing_pipeline(path, repo_name)
        indexing_status[repo_name] = "completed"
    except Exception as e:
        indexing_status[repo_name] = f"failed: {str(e)}"


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
        "code_search.index.parser_for_nl",
        "code_search.index.upload_signatures",
    ]

    try:
        for module in modules:
            print(f"Running indexing step: {module}...")
            # We pass repo_path as an argument to match the original shell script
            subprocess.run(["python3", "-m", module, repo_path], check=True, env=env)
        print("Indexing completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Indexing failed at step {e.cmd}: {e}")
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
    status = indexing_status.get(repo_name, "not_started")
    return {"repo_name": repo_name, "status": status}


@app.get("/api/search")
async def search(query: str, repo_name: str):
    return {"result": searcher.search(query, repo_name, limit=5)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
