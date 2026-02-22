import os
import shutil
import subprocess

from code_search.get_file import FileGet
from code_search.searcher import CombinedSearcher
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

searcher = CombinedSearcher()
get_file = FileGet()

# Configuration
TMP_REPO_DIR = "/tmp/mean-flashcards"
REPO_URL = "https://github.com/nevernorbo/mean-flashcards.git"


class RepoRequest(BaseModel):
    repo_url: str = REPO_URL


def run_indexing_pipeline(repo_path: str):
    """
    Equivalent to index_qdrant.sh.
    Executes the Python indexing modules in the correct sequence.
    """
    env = os.environ.copy()
    env["REPO_PATH"] = repo_path

    # List of modules to run in order
    modules = [
        "code_search.index.files_to_json",
        "code_search.index.file_uploader",
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


@app.post("/api/index")
async def index_repository(background_tasks: BackgroundTasks, request: RepoRequest):
    """
    Equivalent to download_and_index.sh logic.
    Clones the repo and triggers background indexing.
    """
    if os.path.exists(TMP_REPO_DIR):
        shutil.rmtree(TMP_REPO_DIR)

    try:
        # Clone the repository
        subprocess.run(["git", "clone", request.repo_url, TMP_REPO_DIR], check=True)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to clone repository")

    # Run the heavy indexing work in the background to avoid blocking the API
    background_tasks.add_task(run_indexing_pipeline, TMP_REPO_DIR)

    return {"message": f"Indexing started for {request.repo_url}"}


@app.get("/api/search")
async def search(query: str):
    return {"result": searcher.search(query, limit=5)}


@app.get("/api/file")
async def file(path: str):
    return {"result": get_file.get(path)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
