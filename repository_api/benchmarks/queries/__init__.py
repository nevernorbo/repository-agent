from dataclasses import dataclass, field
from typing import List


@dataclass
class Query:
    """Represents a benchmark query with ground truth annotations."""

    id: str
    text: str
    query_type: str  # "natural_language" or "code"
    description: str
    expected_files: List[str] = field(default_factory=list)
    expected_symbols: List[str] = field(default_factory=list)
