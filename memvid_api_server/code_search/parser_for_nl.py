"""
Extract code items for natural language processing.

Parses source code files to extract functions, classes, and other definitions
with metadata. Output format includes name, signature, docstring, and line numbers.
"""

import sys
import os
from pathlib import Path

from code_search.config import DATA_DIR
from .language_definitions import LANGUAGES
from .parser_common import (
    get_language_for_file,
    get_snippet,
    visit_files,
    get_language_extractor,
    get_parser_for_language,
    write_ndjson,
)


def extract_code_items(lang, src_code, file_meta):
    """
    Parse source code to extract code items (functions, classes, etc.) with metadata.

    Args:
        lang (str): Language identifier (e.g., 'python', 'typescript').
        src_code (str): The full source code of the file.
        file_meta (dict): Metadata about the file (e.g., file path, module).

    Returns:
        list of dict: A list of extracted code items with metadata.
    """
    src_lines = src_code.splitlines()
    parser = get_parser_for_language(lang)
    tree = parser.parse(src_code.encode("utf-8"))
    root = tree.root_node

    extractor = get_language_extractor(lang)
    if not extractor:
        return []

    items = []

    for extraction in extractor(root, src_lines):
        if lang == "python":
            node, item_type, name_node, docstring = extraction
            name = name_node.text.decode()

            item = {
                "name": name,
                "signature": get_snippet(src_lines, node.start_point, node.end_point),
                "code_type": item_type,
                "docstring": docstring,
                "line": node.start_point[0] + 1,
                "line_from": node.start_point[0] + 1,
                "line_to": node.end_point[0] + 1,
                "context": {
                    **file_meta,
                    "snippet": get_snippet(src_lines, node.start_point, node.end_point),
                },
            }
        else:
            # JavaScript/TypeScript and C family
            node, item_type, name_node = extraction
            name = name_node.text.decode()

            item = {
                "name": name,
                "signature": get_snippet(src_lines, node.start_point, node.end_point),
                "code_type": item_type,
                "docstring": None,
                "line": node.start_point[0] + 1,
                "line_from": node.start_point[0] + 1,
                "line_to": node.end_point[0] + 1,
                "context": {
                    **file_meta,
                    "snippet": get_snippet(src_lines, node.start_point, node.end_point),
                },
            }

        items.append(item)

    return items


def main():
    """
    Entry point: Walk files, extract code items, and write to output file.
    """
    dir_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"Scanning {dir_path} with tree-sitter parser")

    all_entries = []
    files = list(visit_files(dir_path))
    total_files = len(files)

    print(f"Found {total_files} source files\n")

    for i, filepath in enumerate(files, 1):
        lang = get_language_for_file(filepath)

        if lang and lang in LANGUAGES:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    src_code = f.read()

                file_meta = {
                    "module": Path(filepath).parent.name,
                    "file_path": os.path.relpath(filepath, dir_path),
                    "file_name": Path(filepath).name,
                }

                items = extract_code_items(lang, src_code, file_meta)
                all_entries.extend(items)

            except Exception as e:
                print(f"Failed to parse {filepath}: {e}", file=sys.stderr)
                continue

        # Simple progress print (overwrites the same line)
        print(f"Processing files: {i}/{total_files}", end="\r", flush=True)

    write_ndjson(Path(DATA_DIR) / "nl_snippets", all_entries)
    print(f"\nWrote {len(all_entries)} code entities to nl_snippets")


if __name__ == "__main__":
    main()
