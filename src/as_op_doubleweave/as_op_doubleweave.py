__all__ = ["as_op_doubleweave"]

import copy

import dtx_to_wif

from .expected_error import ExpectedError
from .filter_pattern import Filter, filter_pattern


def as_op_doubleweave(
    in_pattern: dtx_to_wif.PatternData, filter: Filter
) -> dtx_to_wif.PatternData:
    """Convert a weaving pattern file to overshot-patterned double weave.

    Parameters
    ----------
    in_pattern : dtx_to_wif.PatternData
        Original pattern. Ends that are not threaded on any shaft
        and picks with no treadle are silently ignored.

    Notes
    -----
    The pattern must obey the following rules:

    * It must contain treadling information (not pure liftplan).
    * It must not use multiple shafts per end.
    * It must not use multiple treadles per pick.
    * It must have the same number of treadles as shafts.

    In addition, the ends and picks should change by a single shaft/treadle
    each step, else the result will probably have floats that will make
    the fabric unstable.
    """
    if len(in_pattern.treadling) == 0:
        raise ExpectedError("Pattern has no treadling info")

    filtered_original = filter_pattern(in_pattern=in_pattern, filter=filter)
    filtered_threading = filtered_original.threading
    filtered_treadling = filtered_original.treadling

    max_shafts_per_end = max(
        len(shaft_set) for shaft_set in filtered_threading.values()
    )
    if max_shafts_per_end > 1:
        raise ExpectedError(
            "some warp yarns are threaded on multiple shafts (even after filtering)"
        )

    shaft_set = set.union(*filtered_threading.values())
    # Dict of original shaft: main new shaft
    shaft_dict = {shaft: i + 1 for i, shaft in enumerate(sorted(shaft_set))}

    treadle_set = set.union(*filtered_treadling.values())
    # Dict of original treadle: main new treadle
    treadle_dict = {treadle: i + 1 for i, treadle in enumerate(sorted(treadle_set))}

    if len(shaft_dict) != len(treadle_dict):
        raise ExpectedError(
            f"num shafts={len(shaft_dict)} "
            f"!= num treadles={len(treadle_dict)} "
            "after filtering"
        )

    max_treadles_per_end = max(
        len(treadle_set) for treadle_set in filtered_treadling.values()
    )
    if max_treadles_per_end > 1:
        raise ExpectedError(
            "some picks use more than one treadle (even after filtering)"
        )

    warp = copy.copy(in_pattern.warp)
    warp.threads = 0  # Let PatternData compute it
    weft = copy.copy(in_pattern.weft)
    weft.threads = 0  # Let PatternData compute it

    main_color = warp.color
    opposite_color = weft.color
    if main_color is None or opposite_color is None or main_color == opposite_color:
        main_color = 1
        opposite_color = 2

    warp_colors: dict[int, int] = dict()

    weft_colors: dict[int, int] = dict()

    num_shafts = len(shaft_dict)
    shafts_delta = num_shafts // 2

    threading: dict[int, set[int]] = dict()
    for i, shaft_set in enumerate(filtered_threading.values()):
        main_end = i * 2 + 1
        original_shaft = shaft_set.pop()
        main_shaft = shaft_dict[original_shaft]
        opposite_shaft = 1 + ((shafts_delta + main_shaft - 1) % num_shafts)
        threading[main_end] = set([main_shaft])
        warp_colors[main_end] = main_color
        threading[main_end + 1] = set([opposite_shaft])
        warp_colors[main_end + 1] = opposite_color

    tieup: dict[int, set[int]] = dict()
    all_shafts_set = set(range(1, 1 + num_shafts))
    # Use two separate for loops in order to keep the entries in order.
    # This is not essential, but makes the data less surprising.
    for shaft in range(1, 1 + num_shafts):
        treadle = shaft
        tieup[treadle] = set([shaft])
    for shaft in range(1, 1 + num_shafts):
        treadle = shaft + num_shafts
        opposite_shaft = 1 + ((shaft - 1 + shafts_delta) % num_shafts)
        all_but_opposite_shaft_set = copy.copy(all_shafts_set) - set([opposite_shaft])
        tieup[treadle] = all_but_opposite_shaft_set

    treadling: dict[int, set[int]] = dict()
    for i, treadleset in enumerate(filtered_treadling.values()):
        main_pick = i * 2 + 1
        original_treadle = treadleset.pop()
        main_treadle = treadle_dict[original_treadle]
        opposite_treadle = main_treadle + num_shafts
        treadling[main_pick] = set([main_treadle])
        weft_colors[main_pick] = main_color
        treadling[main_pick + 1] = set([opposite_treadle])
        weft_colors[main_pick + 1] = opposite_color

    new_name_components = [in_pattern.name, "as op doubleweave"]
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
        tieup=tieup,
        treadling=treadling,
        liftplan=dict(),
        color_table=in_pattern.color_table,
        color_range=in_pattern.color_range,
        warp=warp,
        weft=weft,
        warp_colors=warp_colors,
        weft_colors=weft_colors,
        source_program="as_op_doubleweave",
    )
