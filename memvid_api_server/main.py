import sys
import shutil
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from git import Repo
import os

# Ensure the code_search module can be found
sys.path.append(str(Path(__file__).resolve().parent))

from code_search.parser_for_code import main as parse_code_main
from code_search.parser_for_nl import main as parse_nl_main
from memvid_store import ingest_to_memvid
from memvid_sdk import use

app = FastAPI()

# In-memory cache for loaded memories
loaded_memories = {}

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

class Repository(BaseModel):
    repo_url: str

def get_repo_name_from_url(url: str) -> str:
    return Path(url).stem

@app.post("/repository")
async def add_repository(repository: Repository):
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
        
        # We need to temporarily change sys.argv for the parsers
        original_argv = sys.argv
        
        sys.argv = ["", repo_str]
        parse_code_main()
        parse_nl_main()
        
        sys.argv = original_argv
        print("Parsing complete.")
        
        # 3. Ingest to Memvid
        print("Ingesting into Memvid...")
        code_snippets_path = DATA_DIR / "code_snippets.jsonl"
        nl_snippets_path = DATA_DIR / "nl_snippets"
        
        ingest_to_memvid(code_snippets_path, nl_snippets_path, str(memory_file))
        print(f"Ingestion complete. Memory file saved to {memory_file}")
        
        # Clean up intermediate files
        if code_snippets_path.exists():
            os.remove(code_snippets_path)
        if nl_snippets_path.exists():
            os.remove(nl_snippets_path)

        return {"message": f"Repository {repo_name} indexed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if repo_dir.exists():
            shutil.rmtree(repo_dir)


@app.get("/repository/{repo_name}/query")
async def query_repository(repo_name: str, q: str):
    if repo_name in loaded_memories:
        mem = loaded_memories[repo_name]
    else:
        memory_file = DATA_DIR / f"{repo_name}.mv2"
        if not memory_file.exists():
            raise HTTPException(status_code=404, detail="Repository not found or not indexed yet.")
        
        try:
            mem = use("basic", str(memory_file))
            loaded_memories[repo_name] = mem
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load memory: {e}")

    try:
        results = mem.find(q)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during search: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
