__all__ = ["run_filter_pattern", "run_as_op_doubleweave"]

import argparse
import pathlib
import time
import traceback

import dtx_to_wif

from .as_op_doubleweave import as_op_doubleweave
from .expected_error import ExpectedError
from .filter_pattern import Filter, add_filter_args, filter_pattern
from .read_pattern import read_pattern


def run_filter_pattern() -> None:
    """Command-line interface to `filter_pattern`."""
    parser = argparse.ArgumentParser(
        "Filter ends and/or picks in weaving pattern files"
    )
    parser.add_argument(
        "files", type=pathlib.Path, nargs="*", help=".wif or .dtx pattern file"
    )
    add_filter_args(parser)
    args = parser.parse_args()
    filter = Filter.from_args(args)
    if not any(bool(value) for value in vars(filter).values()):
        # Avoid overwriting input files
        # (since with no options, the new name will match old)
        parser.error("Must select at least one filter option")

    for inpath in args.files:
        try:
            in_pattern = read_pattern(inpath)
            in_pattern.name = inpath.stem

            out_pattern = filter_pattern(in_pattern=in_pattern, filter=filter)

            outpath = inpath.parent / f"{out_pattern.name}.wif"
            with open(outpath, "w") as f:
                dtx_to_wif.write_wif(f, out_pattern)
            print(f'Wrote "{outpath!s}"')

        except ExpectedError as e:
            print(f"Could not process {str(inpath)!r}: {e.args[0]}")
        except Exception as e:
            print(f"Could not process {str(inpath)!r}: {e!r}")
            traceback.print_exc()


def run_as_op_doubleweave() -> None:
    """Convert weaving pattern files to overshot-patterned double weave.

    See as_op_doubleweave for restrictions.
    """
    parser = argparse.ArgumentParser(
        "Convert weaving patterns to overshot-patterned double weave"
    )
    parser.add_argument(
        "files", type=pathlib.Path, nargs="*", help=".wif or .dtx pattern file"
    )
    add_filter_args(parser)
    args = parser.parse_args()
    filter = Filter.from_args(args)

    for inpath in args.files:
        try:
            in_pattern = read_pattern(inpath)
            in_pattern.name = inpath.stem

            out_pattern = as_op_doubleweave(in_pattern=in_pattern, filter=filter)

            outpath = inpath.parent / f"{out_pattern.name}.wif"
            with open(outpath, "w") as f:
                dtx_to_wif.write_wif(f, out_pattern)
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
            print(f'Wrote "{outpath!s}"')
        except ExpectedError as e:
            print(f"Could not process {str(inpath)!r}: {e.args[0]}")
        except Exception as e:
            print(f"Could not process {str(inpath)!r}: {e!r}")
            traceback.print_exc()
