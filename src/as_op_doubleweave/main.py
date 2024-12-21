__all__ = ["main"]

import argparse
import pathlib
import time
import traceback

import dtx_to_wif

from .as_op_doubleweave import Filter, as_op_doubleweave


def main() -> None:
    """Convert a weaving pattern file to overshot-patterned double weave.

    See as_op_doubleweave for restrictions.
    """
    parser = argparse.ArgumentParser(
        "Convert weaving patterns to overshot-patterned double weave"
    )
    parser.add_argument(
        "infiles", type=pathlib.Path, nargs="*", help=".wif or .dtx pattern file"
    )
    parser.add_argument(
        "--skip-odd-ends", action="store_true", help="Skip odd ends (1, 3, 5...)?"
    )
    parser.add_argument(
        "--skip-even-ends", action="store_true", help="Skip even ends (2, 4, 6...)?"
    )
    parser.add_argument(
        "--skip-odd-picks", action="store_true", help="Skip odd picks (1, 3, 5...)?"
    )
    parser.add_argument(
        "--skip-even-picks", action="store_true", help="Skip even picks (2, 4, 6...)?"
    )
    parser.add_argument(
        "--skip-treadles",
        type=int,
        nargs="*",
        default=(),
        help="(1-based) treadles to skip, e.g. treadles used for tabby",
    )
    args = parser.parse_args()
    filter = Filter(
        skip_even_ends=args.skip_even_ends,
        skip_odd_ends=args.skip_odd_ends,
        skip_even_picks=args.skip_even_picks,
        skip_odd_picks=args.skip_odd_picks,
        skip_treadles=args.skip_treadles,
    )

    reader_dict = {
        ".dtx": dtx_to_wif.read_dtx,
        ".wif": dtx_to_wif.read_wif,
    }
    file_types_str = ", ".join(reader_dict.keys())
    for infile in args.infiles:
        try:
            file_extension = infile.suffix.lower()
            reader = reader_dict.get(file_extension)
            if reader is None:
                raise RuntimeError(
                    f"Unsupported file type: must be one of {file_types_str}"
                )
            with open(infile, "r") as f:
                original = reader(f)

            if original.name == "?":
                original.name = infile.stem

            new_pattern = as_op_doubleweave(original=original, filter=filter)

            outpath = infile.parent / f"{new_pattern.name}.wif"
            with open(outpath, "w") as f:
                dtx_to_wif.write_wif(f, new_pattern)
                # Tell WeaveIt Pro that this is double weave
                f.write(
                    f"""

[PRIVATE IWEAVEIT PROJECT]
theDescription=
projectDate={time.time()}
isInches=1
sett=24
ppi=24
wasteLength=24.00
shrinkage=5
weaveType=3
"""
                )
        except RuntimeError as e:
            print(f"Could not process {str(infile)!r}: {e.args[0]}")
        except Exception as e:
            print(f"Could not process {str(infile)!r}: {e!r}")
            traceback.print_exc()
