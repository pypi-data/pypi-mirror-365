"""
MDIS - Malware Detection and Identification System
--------------------------------------------------
A minimal yet expressive malware identifier system,
designed for fast parsing, clarity, and extensibility.
"""

from typing import Dict, Any, Union
import re

DICTIONARIES: Dict[str, Dict[str, str]]

class MDISParserError(Exception):
    def __init__(self, err: str) -> None: ...

class MDISParser:
    REGEX_PATTERN: re.Pattern

    def __init__(self, identifier: str) -> None: ...
    def is_valid(self) -> bool: ...
    def parse(
        self, more_info: bool = False
    ) -> Union[Dict[str, Any], MDISParserError]: ...
    def to_natural(self) -> str: ...
    def dump_report_file(self) -> None: ...
    @staticmethod
    def build_id(fields: Dict[str, str]) -> str: ...
