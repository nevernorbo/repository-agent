import json
import os.path
from pathlib import Path

from code_search.config import DATA_DIR

from .language_definitions import EXTENSION_LANG_MAP


def process_file(root_dir, file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        code_lines = file.readlines()
        relative_path = os.path.relpath(file_path, root_dir)
        repo_name = os.getenv("REPO_NAME")

        return {
            "repo_name": repo_name,
            "path": relative_path,
            "code": code_lines,
            "startline": 1,
            "endline": len(code_lines),
        }


def explore_directory(root_dir):
    result = []
    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            _, ext = os.path.splitext(file_path)
            if ext in EXTENSION_LANG_MAP:
                result.append(process_file(root_dir, file_path))
    return result


def main():
    folder_path = os.getenv("REPO_PATH")
    output_file = Path(DATA_DIR) / "files.json"

    files_data = explore_directory(folder_path)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(files_data, json_file, indent=2)


if __name__ == "__main__":
    main()
