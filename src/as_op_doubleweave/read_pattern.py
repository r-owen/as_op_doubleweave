__all__ = ["read_pattern"]

import pathlib

import dtx_to_wif

from .expected_error import ExpectedError

READER_DICT = {
    ".dtx": dtx_to_wif.read_dtx,
    ".wif": dtx_to_wif.read_wif,
}


def read_pattern(pattern_path: pathlib.Path) -> dtx_to_wif.PatternData:
    """Read a weaving pattern file."""
    file_extension = pattern_path.suffix.lower()
    reader = READER_DICT.get(file_extension)
    if reader is None:
        raise ExpectedError(
            f"Unsupported file extension {file_extension}; must be one of: "
            ", ".join(READER_DICT.keys())
        )
    with open(pattern_path, "r") as f:
        pattern = reader(f)
    return pattern
