"""
Extract code snippets with precise position information for LLM context.

Parses source code to extract definitions with line/character positions and
surrounding context blocks for use in language model applications.
"""

import sys
from pathlib import Path

from code_search.config import DATA_DIR

from .language_definitions import LANGUAGES
from .parser_common import (
    get_context_block,
    get_language_extractor,
    get_language_for_file,
    get_parser_for_language,
    visit_files,
    write_jsonl,
)


def extract_code_snippets(lang, src_code, file_path, root_dir):
    """
    Extract code items with full position and context information.

    Args:
        lang (str): Language identifier.
        src_code (str): Full source code text.
        file_path (str): Absolute path to file.
        root_dir (str): Project root directory.

    Returns:
        list of dict: Entries with position and snippet information.
    """
    src_lines = src_code.splitlines()
    rel_path = str(Path(file_path).relative_to(root_dir))

    parser = get_parser_for_language(lang)
    tree = parser.parse(src_code.encode("utf-8"))
    root = tree.root_node

    extractor = get_language_extractor(lang)
    if not extractor:
        return []

    entries = []

    for extraction in extractor(root, src_lines):
        node, item_type, name_node = extraction
        name = name_node.text.decode()

        start_line = node.start_point.row
        end_line = node.end_point.row

        # Get surrounding context for LLM
        context_start, context_end, code_block = get_context_block(
            src_lines, start_line, end_line, context_lines=10
        )

        entry = {
            "file": rel_path,
            "item_name": name,
            "item_type": item_type,
            "code_snippet": code_block,
        }

        entries.append(entry)

    return entries


def main():
    """
    Entry point: Scan project, extract code with positions, write output.
    """
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    root_dir = Path(root_dir).resolve()

    print(f"Scanning {root_dir} with tree-sitter parser")

    all_entries = []
    files = list(visit_files(str(root_dir)))
    total_files = len(files)

    print(f"Found {total_files} source files\n")

    for i, filepath in enumerate(files, 1):
        lang = get_language_for_file(filepath)

        if lang and lang in LANGUAGES:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    src_code = f.read()

                entries = extract_code_snippets(lang, src_code, filepath, str(root_dir))
                all_entries.extend(entries)

            except Exception as e:
                print(f"Failed to parse {filepath}: {e}", file=sys.stderr)
                continue

        if i % 10 == 0:
            print(f"Processing files: {i}/{total_files}", end="\r", flush=True)

    write_jsonl(Path(DATA_DIR) / "code_snippets.jsonl", all_entries)
    print(f"\nWrote {len(all_entries)} code entities to code_snippets.json")


if __name__ == "__main__":
    main()
