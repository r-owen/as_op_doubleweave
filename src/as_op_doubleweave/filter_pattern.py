from __future__ import annotations

__all__ = ["Filter", "filter_pattern"]

import argparse
import copy
import dataclasses
from collections.abc import Collection

import dtx_to_wif

from .expected_error import ExpectedError


@dataclasses.dataclass
class Filter:
    """Filters for the in_pattern pattern."""

    skip_odd_ends: bool = False
    skip_even_ends: bool = False
    skip_odd_picks: bool = False
    skip_even_picks: bool = False
    skip_treadles: Collection[int] = ()

    def __post_init__(self):
        if self.skip_even_ends and self.skip_odd_ends:
            raise ValueError("Cannot skip both even and odd ends")
        if self.skip_even_picks and self.skip_odd_picks:
            raise ValueError("Cannot skip both even and odd picks")

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Filter:
        """Construct a Filter from command-line arguments.

        Assumes the arguments specifid by `add_filter_args`.
        """
        return cls(
            skip_even_ends=args.skip_even_ends,
            skip_odd_ends=args.skip_odd_ends,
            skip_even_picks=args.skip_even_picks,
            skip_odd_picks=args.skip_odd_picks,
            skip_treadles=args.skip_treadles,
        )


def add_filter_args(parser: argparse.ArgumentParser) -> None:
    """Add filter arguments to a command-line parser."""
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


def sort_and_purge_empty_sets(data: dict[int, set[int]]) -> dict[int, set[int]]:
    """Sort a dict of int: set[int] and purge items where the set is empty"""
    return {key: data[key] for key in sorted(data.keys()) if data[key]}


def filter_pattern(
    in_pattern: dtx_to_wif.PatternData, filter: Filter
) -> dtx_to_wif.PatternData:
    """Filter ends and/or picks in a weaving pattern file.

    Parameters
    ----------
    in_pattern : dtx_to_wif.PatternData
        Input pattern.
    filter : Filter
        Filter to apply to in_pattern. In addition,
        ends that are not threaded on any shaft and picks
        with no treadle are silently omitted.
    """
    if filter.skip_even_ends and filter.skip_odd_ends:
        raise ExpectedError("Cannot remove both even and odd ends")

    if filter.skip_even_picks and filter.skip_odd_picks:
        raise ExpectedError("Cannot remove both even and odd picks")

    warp = copy.copy(in_pattern.warp)
    warp.threads = 0  # Let PatternData compute it
    weft = copy.copy(in_pattern.weft)
    weft.threads = 0  # Let PatternData compute it

    # Sort threading by end and filter out ends that are not threaded.
    filtered_threading = sort_and_purge_empty_sets(in_pattern.threading)

    # Apply skip_odd_ends or skip_even_ends to threading, if requested.
    if filter.skip_odd_ends or filter.skip_even_ends:
        offset = 1 if filter.skip_odd_ends else 0
        filtered_threading = {
            end: shaft_set
            for end, shaft_set in filtered_threading.items()
            if (end + offset) % 2 == 0
        }

    # Compute output threading and warp_colors with sequential keys
    # (but warp_colors is sparse).
    threading = {
        i + 1: shaft_set for i, shaft_set in enumerate(filtered_threading.values())
    }
    warp_colors = {
        i + 1: in_pattern.warp_colors[pick]
        for i, pick in enumerate(filtered_threading.keys())
        if pick in in_pattern.warp_colors and in_pattern.warp_colors[pick] != warp.color
    }

    # Sort liftplan and treadling by pick,
    # and filter out picks that are not treadled.
    filtered_treadling = sort_and_purge_empty_sets(in_pattern.treadling)
    filtered_liftplan = sort_and_purge_empty_sets(in_pattern.liftplan)

    # Apply skip_odd_picks or skip_even_picks to liftplan and treadling,
    # if requested.
    if filter.skip_odd_picks or filter.skip_even_picks:
        offset = 1 if filter.skip_odd_picks else 0
        filtered_treadling = {
            pick: treadle_set
            for pick, treadle_set in filtered_treadling.items()
            if (pick + offset) % 2 == 0
        }
        filtered_liftplan = {
            pick: shaft_set
            for pick, shaft_set in filtered_liftplan.items()
            if (pick + offset) % 2 == 0
        }

    # Apply skip_treadles to treadling (not to liftplan).
    if filter.skip_treadles:
        skip_treadle_set = set(filter.skip_treadles)
        filtered_treadling = {
            pick: (treadle_set - skip_treadle_set)
            for pick, treadle_set in filtered_treadling.items()
            if treadle_set - skip_treadle_set
        }

    # Compute output liftplan, threading, and weft_colors,
    # with sequential keys 1-N (but weft_colors is sparse)
    liftplan = {
        i + 1: shaft_set for i, shaft_set in enumerate(filtered_liftplan.values())
    }
    treadling = {
        i + 1: treadle_set for i, treadle_set in enumerate(filtered_treadling.values())
    }
    if in_pattern.treadling:
        filtered_picks = filtered_treadling.keys()
    else:
        filtered_picks = filtered_liftplan.keys()
    weft_colors = {
        i + 1: in_pattern.weft_colors[pick]
        for i, pick in enumerate(filtered_picks)
        if pick in in_pattern.weft_colors and in_pattern.weft_colors[pick] != weft.color
    }

    new_name_components = [in_pattern.name]
    for name, value in vars(filter).items():
        if name == "skip_treadles":
            if value:
                new_name_components.append(
                    " ".join(["skip-treadles"] + [str(treadle) for treadle in value])
                )
        else:
            if value:
                new_name_components.append(name.replace("_", "-"))
    new_name = " ".join(new_name_components)

    return dtx_to_wif.PatternData(
        name=new_name,
        threading=threading,
        tieup=in_pattern.tieup,
        treadling=treadling,
        liftplan=liftplan,
        color_table=in_pattern.color_table,
        color_range=in_pattern.color_range,
        warp=warp,
        weft=weft,
        warp_colors=warp_colors,
        weft_colors=weft_colors,
        source_program="filter_pattern",
    )
