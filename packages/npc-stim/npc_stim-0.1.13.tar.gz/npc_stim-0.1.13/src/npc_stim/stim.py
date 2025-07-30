from __future__ import annotations

import datetime
import io
import logging
import pickle
from collections.abc import Iterable, Mapping
from typing import Literal, SupportsFloat

import h5py
import npc_io
import npc_session
import npc_sync
import numpy as np
import numpy.typing as npt
import upath

from npc_stim.types import StimPathOrDataset

logger = logging.getLogger(__name__)


def get_stim_data(stim_path: StimPathOrDataset, **kwargs) -> h5py.File | dict:
    if isinstance(stim_path, h5py.File):
        return stim_path
    if isinstance(stim_path, Mapping):  # ie. from pkl file
        return dict(stim_path)
    path = npc_io.from_pathlike(stim_path)
    if path.suffix in (".hdf5", ".h5"):
        return get_h5_stim_data(path, **kwargs)
    if path.suffix == ".pkl":
        return get_pkl_stim_data(path, **kwargs)
    raise ValueError(f"Unknown stim file type: {path}")


def get_h5_stim_data(stim_path: StimPathOrDataset, **kwargs) -> h5py.File:
    if isinstance(stim_path, h5py.File):
        return stim_path
    if isinstance(stim_path, Mapping):
        raise ValueError("Susepcted pickle date encountered: use `get_pkl_stim_data`")
    kwargs.setdefault("mode", "r")
    path = npc_io.from_pathlike(stim_path)
    if path.protocol in ("", "file"):
        return h5py.File(io.BytesIO(path.read_bytes()), **kwargs)
    else:
        return h5py.File(path.open(mode="rb", cache_type="first"), **kwargs)


def get_pkl_stim_data(stim_path: StimPathOrDataset, **kwargs) -> dict:
    if isinstance(stim_path, Mapping):
        return dict(stim_path)
    if isinstance(stim_path, h5py.File):
        raise TypeError(
            "hdf5 data encountered when pkl data expected: use `get_h5_stim_data` instead"
        )
    kwargs.setdefault("encoding", "latin1")
    return pickle.loads(npc_io.from_pathlike(stim_path).read_bytes())


def get_input_data_times(
    stim: npc_io.PathLike,
    sync: npc_sync.SyncPathOrDataset | None = None,
) -> npt.NDArray[np.float64]:
    """Best-estimate time of `getInputData()` in psychopy event loop, in seconds, from start
    of experiment. Uses preceding frame's vsync time if sync provided"""
    stim_data = get_stim_data(stim)
    assert isinstance(stim_data, h5py.File), "Only hdf5 stim files supported for now"
    if not sync:
        return np.concatenate(([0], np.cumsum(stim_data["frameIntervals"][:])))
    return np.concatenate(
        [
            [np.nan],
            assert_stim_times(
                get_stim_frame_times(stim, sync=sync, frame_time_type="vsync")[stim]
            )[:-1],
        ]
    )


def get_flip_times(
    stim: StimPathOrDataset,
    sync: npc_sync.SyncPathOrDataset | None = None,
) -> npt.NDArray[np.float64]:
    """Best-estimate time of `flip()` at end of psychopy event loop, in seconds, from start
    of experiment. Uses frame's vsync time sync provided."""
    stim = get_stim_data(stim)
    assert isinstance(stim, h5py.File), "Only hdf5 stim files supported for now"
    if not sync:
        return np.concatenate(
            (
                (c := np.cumsum(f := stim["frameIntervals"][:])),
                [c[-1] + np.median(np.diff(f))],
            )
        )
    return assert_stim_times(
        get_stim_frame_times(stim, sync=sync, frame_time_type="vsync")[stim]
    )


def get_vis_display_times(
    stim: npc_io.PathLike,
    sync: npc_sync.SyncPathOrDataset | None = None,
) -> npt.NDArray[np.float64]:
    """Best-estimate time of monitor update. Uses photodiode if sync provided. Without sync, this equals frame times."""
    stim_data = get_stim_data(stim)
    assert isinstance(stim_data, h5py.File), "Only hdf5 stim files supported for now "
    if not sync:
        return get_flip_times(stim_data)
    return assert_stim_times(
        get_stim_frame_times(stim, sync=sync, frame_time_type="display_time")[stim]
    )


def get_stim_block_to_path(
    stim_paths: Iterable[npc_io.PathLike],
    sync_data: npc_sync.SyncDataset,
) -> dict[int, upath.UPath | None]:
    """
    Map sync block indices to stim file paths based on start time and frame count matching.

    Returns a dict where keys are block indices and values are either stim paths or None
    if no stim file matches that block.
    """

    block_to_stim: dict[int, upath.UPath | None] = dict.fromkeys(
        range(len(sync_data.vsync_times_in_blocks))
    )

    # get num frames in each block
    n_frames_per_block = np.asarray([len(x) for x in sync_data.vsync_times_in_blocks])
    # get first frame time in each block
    first_frame_per_block = np.asarray([x[0] for x in sync_data.vsync_times_in_blocks])

    # Track which stim files have been matched to avoid double-assignment
    matched_stims: set[npc_io.PathLike] = set()

    for stim_path in stim_paths:
        # Skip if already matched
        if stim_path in matched_stims:
            continue

        try:
            stim_data = get_h5_stim_data(stim_path)
        except OSError:
            continue  # Skip files that can't be opened

        n_stim_frames = get_total_stim_frames(stim_data)
        if n_stim_frames == 0:
            continue  # Skip files with no frames

        stim_start_time = get_stim_start_time(stim_data)
        if abs((stim_start_time - sync_data.start_time).days > 0):
            continue  # Skip files from different days

        stim_start_time_on_sync = (stim_start_time - sync_data.start_time).seconds
        matching_block_idx_by_start_time = np.argmin(
            abs(first_frame_per_block - stim_start_time_on_sync)
        )
        matching_block_idx_by_len = np.argmin(abs(n_frames_per_block - n_stim_frames))

        start_and_len_match_disagree = (
            matching_block_idx_by_start_time != matching_block_idx_by_len
        ) and (
            len(
                [
                    same_len_stims
                    for same_len_stims in n_frames_per_block
                    if same_len_stims == n_frames_per_block[matching_block_idx_by_len]
                ]
            )
            == 1
        )

        num_frames_match = (
            n_stim_frames == n_frames_per_block[matching_block_idx_by_start_time]
        )
        stim_path = npc_io.from_pathlike(stim_path)
        if num_frames_match and not start_and_len_match_disagree:
            block_to_stim[int(matching_block_idx_by_start_time)] = stim_path
            matched_stims.add(stim_path)
        elif (
            start_and_len_match_disagree
            and n_stim_frames == n_frames_per_block[matching_block_idx_by_len]
        ):
            block_to_stim[int(matching_block_idx_by_len)] = stim_path
            matched_stims.add(stim_path)

    return block_to_stim


def get_stim_frame_times(
    *stim_paths: npc_io.PathLike,
    sync: npc_sync.SyncPathOrDataset,
    frame_time_type: Literal["display_time", "vsync"] = "display_time",
) -> dict[npc_io.PathLike, Exception | npt.NDArray[np.float64]]:
    """
    - keys are the stim paths provided as inputs

    >>> bad_stim = 's3://aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/DynamicRouting1_670248_20230802_120703.hdf5'
    >>> good_stim_1 = 's3://aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/Spontaneous_670248_20230802_114611.hdf5'
    >>> good_stim_2 = 's3://aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/SpontaneousRewards_670248_20230802_130736.hdf5'
    >>> sync = 's3://aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/20230802T113053.h5'

    Returns the frame times for each stim file based on start time and number
    of frames - can be provided in any order:
    >>> frame_times = get_stim_frame_times(good_stim_2, good_stim_1, sync=sync)
    >>> len(frame_times[good_stim_2])
    36000

    Returns Exception if the stim file can't be opened, or it has no frames.
    Should be used with `assert_stim_times` to raise a possible exception:
    >>> frame_times = get_stim_frame_times(bad_stim, sync=sync)
    >>> assert_stim_times(frame_times[bad_stim])
    Traceback (most recent call last):
    ...
    FileNotFoundError: aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/DynamicRouting1_670248_20230802_120703.hdf5
    """

    # load sync file once
    sync_data = npc_sync.get_sync_data(sync)

    # Get mapping of block indices to stim paths
    block_to_stim = get_stim_block_to_path(stim_paths, sync_data)

    # get num frames in each block
    n_frames_per_block = np.asarray([len(x) for x in sync_data.vsync_times_in_blocks])
    # get first frame time in each block
    first_frame_per_block = np.asarray([x[0] for x in sync_data.vsync_times_in_blocks])

    stim_frame_times: dict[npc_io.PathLike, Exception | npt.NDArray] = {}

    # Process each stim file and generate appropriate result (frame times or exception)
    for stim_path in stim_paths:

        try:
            stim_data = get_h5_stim_data(stim_path)
        except OSError as exc:
            stim_frame_times[stim_path] = exc
            continue

        n_stim_frames = get_total_stim_frames(stim_data)
        if n_stim_frames == 0:
            stim_frame_times[stim_path] = ValueError(
                f"No frames found in {stim_path = }"
            )
            continue

        stim_start_time = get_stim_start_time(stim_data)
        if abs((stim_start_time - sync_data.start_time).days > 0):
            logger.error(
                f"Skipping {stim_path =}, sync data is from a different day: {stim_start_time = }, {sync_data.start_time = }"
            )
            continue

        # Find which block this stim file was matched to
        matched_block_idx = None
        for block_idx, matched_stim in block_to_stim.items():
            if matched_stim == npc_io.from_pathlike(stim_path):
                matched_block_idx = block_idx
                break

        if matched_block_idx is None:

            stim_start_time_on_sync = (stim_start_time - sync_data.start_time).seconds
            matching_block_idx_by_start_time = np.argmin(
                abs(first_frame_per_block - stim_start_time_on_sync)
            )
            matching_block_idx_by_len = np.argmin(
                abs(n_frames_per_block - n_stim_frames)
            )

            start_and_len_match_disagree = (
                matching_block_idx_by_start_time != matching_block_idx_by_len
            )
            num_frames_match = (
                n_stim_frames == n_frames_per_block[matching_block_idx_by_start_time]
            )

            if not num_frames_match and not start_and_len_match_disagree:
                frame_diff = (
                    n_stim_frames - n_frames_per_block[matching_block_idx_by_start_time]
                )
                stim_frame_times[stim_path] = IndexError(
                    f"Closest match with {stim_path!r} has a mismatch of {frame_diff} frames."
                )
            elif start_and_len_match_disagree:
                time_diff_len = (
                    stim_start_time_on_sync
                    - first_frame_per_block[matching_block_idx_by_len]
                )
                time_diff_start = (
                    stim_start_time_on_sync
                    - first_frame_per_block[matching_block_idx_by_start_time]
                )
                stim_frame_times[stim_path] = IndexError(
                    f"{matching_block_idx_by_start_time=} != {matching_block_idx_by_len=} for {stim_path!r}: failed to match frame times using start time. Closest match by start time has a mismatch of {time_diff_start:.1f} seconds. Closest match by number of frames has a mismatch of {time_diff_len:.1f} seconds."
                )
            continue
        if frame_time_type == "display_time":
            stim_frame_times[stim_path] = sync_data.frame_display_time_blocks[
                matched_block_idx
            ]
        elif frame_time_type == "vsync":
            stim_frame_times[stim_path] = sync_data.vsync_times_in_blocks[
                matched_block_idx
            ]
        else:
            raise ValueError(
                f"Unknown frame time type: {frame_time_type}. Expected 'display_time' or 'vsync'."
            )
    # Sort keys by first frame time, or by exception if present
    sorted_keys = sorted(
        stim_frame_times.keys(),
        key=lambda x: (
            0 if isinstance(stim_frame_times[x], Exception) else stim_frame_times[x][0]  # type: ignore[index]
        ),
    )
    return {k: stim_frame_times[k] for k in sorted_keys}


def assert_stim_times(result: Exception | npt.NDArray) -> npt.NDArray:
    """Raise exception if result is an exception, otherwise return result"""
    if isinstance(result, Exception):
        raise result from None
    return result


def get_num_trials(
    stim_path_or_data: npc_io.PathLike | h5py.File,
) -> int:
    """
    >>> get_num_trials('s3://aind-ephys-data/ecephys_668755_2023-08-31_12-33-31/behavior/DynamicRouting1_668755_20230831_131418.hdf5')
    524
    """
    stim_data = get_h5_stim_data(stim_path_or_data)
    return len(
        stim_data.get("trialEndFrame")
        or stim_data.get("stimStartFrame")
        or stim_data.get("trialOptoOnsetFrame")  # for optoTagging
    )


def get_stim_start_time(
    stim_path_or_data: npc_io.PathLike | h5py.File,
) -> datetime.datetime:
    """Absolute datetime of the first frame, according to the stim file
    >>> get_stim_start_time('s3://aind-ephys-data/ecephys_668755_2023-08-31_12-33-31/behavior/DynamicRouting1_668755_20230831_131418.hdf5')
    datetime.datetime(2023, 8, 31, 13, 14, 18)
    """
    # TODO make compatible with pkl files
    stim_data = get_h5_stim_data(stim_path_or_data)
    # get stim start time & convert to datetime
    return npc_session.DatetimeRecord(stim_data["startTime"][()].decode()).dt


def get_total_stim_frames(stim_path_or_data: npc_io.PathLike | h5py.File) -> int:
    """
    >>> get_total_stim_frames('s3://aind-ephys-data/ecephys_668755_2023-08-31_12-33-31/behavior/DynamicRouting1_668755_20230831_131418.hdf5')
    217261
    """
    # TODO make compatible with pkl files
    stim_data = get_h5_stim_data(stim_path_or_data)
    frame_intervals = stim_data["frameIntervals"][:]
    if len(frame_intervals) == 0:
        return 0
    return len(frame_intervals) + 1


def get_stim_duration(stim_path_or_data: npc_io.PathLike | h5py.File) -> float:
    """
    >>> get_stim_duration('s3://aind-ephys-data/ecephys_668755_2023-08-31_12-33-31/behavior/DynamicRouting1_668755_20230831_131418.hdf5')
    3647.0994503999827
    """
    # TODO make compatible with pkl files
    stim_data = get_h5_stim_data(stim_path_or_data)
    return np.sum(stim_data["frameIntervals"][:])


def get_stim_trigger_frames(
    stim_path_or_data: npc_io.PathLike | h5py.File,
    stim_type: str | Literal["opto"] = "stim",
) -> tuple[int | None, ...]:
    """Frame index of stim command being sent. len() == num trials.

    - for DynamicRouting1 files, use `stim_type='opto'` to get the trigger frames for opto

    >>> path = 's3://aind-ephys-data/ecephys_668755_2023-08-31_12-33-31/behavior/DynamicRouting1_668755_20230831_131418.hdf5'
    >>> frames = get_stim_trigger_frames(path)
    >>> len(frames)
    524

    >>> frames = get_stim_trigger_frames(path, stim_type='opto')
    >>> len(frames)
    0
    """
    stim_data = get_h5_stim_data(stim_path_or_data)
    start_frames = (
        (stim_data.get("trialStimStartFrame") or stim_data.get("stimStartFrame"))
        if stim_type != "opto"
        else (opto := stim_data.get("trialOptoOnsetFrame"))
    )

    if start_frames is None and opto is not None:
        # optoTagging experiments use "trialOptoOnsetFrame" instead of
        # "trialStimStartFrame" - should be safe to switch.. the stim_type
        # parameter just wasn't set to 'opto' when the function was called
        if (
            "optoFeedbackBlocks" in stim_data
            or "feedback" in stim_data["taskVersion"].asstr()[()]
        ):
            logger.info("Feedback opto experiment detected")
        start_frames = opto  # may be adjusted below
        if stim_data.get("optoTaggingLocs") is None:
            logger.warning(
                'Using "trialOptoOnsetFrame" instead of "trialStimStartFrame" - this is likely an old optoTagging experiment, and `stim_type` was specified as `stim` instead of `opto`.'
            )

    start_frames = start_frames[: get_num_trials(stim_data)].squeeze()
    monotonic_increase = np.all(
        (without_nans := start_frames[~np.isnan(start_frames)])[1:] > without_nans[:-1]
    )
    if not monotonic_increase:
        # behavior files with opto report the onset frame of opto relative to stim onset for
        # each trial. OptoTagging files specify absolute frame index
        start_frames += stim_data.get("trialStimStartFrame")[
            : get_num_trials(stim_data)
        ].squeeze()

    return tuple(
        int(v) if ~np.isnan(v) else None
        for v in safe_index(start_frames, np.arange(len(start_frames)))
    )


def safe_index(
    array: npt.ArrayLike, indices: SupportsFloat | Iterable[SupportsFloat]
) -> npt.NDArray:
    """Checks `indices` can be safely used as array indices (i.e. all
    numerical float values are integers), then indexes into `array` using `np.where`.

    - returns nans where `indices` is nan
    - returns a scalar if `indices` is a scalar #TODO use @overload: current type annotation is insufficient

    >>> safe_index([1, 2], 0)
    1
    >>> safe_index([1., 2.], 0)
    1.0
    >>> safe_index([1., 2.], np.nan)
    nan
    >>> safe_index([1., 2., 3.1], [0, np.nan, 2.0])
    array([1. , nan, 3.1])

    Type of array is preserved, if possible:
    >>> safe_index([1, 2, 3], [0., 1., 2.])
    array([1, 2, 3])

    Type of array can't be preserved if any indices are nan:
    >>> safe_index([1, 2, 3], [0, np.nan, 2.0])
    array([ 1., nan,  3.])
    """
    idx: npt.NDArray = np.array(indices)  # copy
    if not all(idx[~np.isnan(idx)] == idx[~np.isnan(idx)].astype(np.int32)):
        raise TypeError(
            f"Non-integer numerical values cannot be used as indices: {idx[np.isnan(idx)][0]}"
        )
    array = np.array(array)  # copy/make sure array can be fancy-indexed
    int_idx = np.where(np.isnan(idx), -1, idx)
    result = np.where(np.isnan(idx), np.nan, array[int_idx.astype(np.int32)])
    # np.where casts indexed array to floats just because of the
    # possibility of nans being in result, even if they aren't:
    # cast back if appropriate
    if not np.isnan(result).any():
        result = result.astype(array.dtype)
    # if indices was a scalar, return a scalar instead of a 0d array
    if not isinstance(indices, Iterable):
        assert result.size == 1
        return result.item()
    return result


def validate_stim(
    *stim_paths: npc_io.PathLike,
    sync: npc_sync.SyncPathOrDataset,
) -> None:
    """
    Check that the stim files can be opened and have valid data that corresponds
    to the sync file. Raises an AssertionError if any of the stim files fail to
    open or can't be identified on sync.

    - validation of other properties (trial starts, display times, etc.) is
      specific to the type of stim and file format

    >>> good_stim_1 = 's3://aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/Spontaneous_670248_20230802_114611.hdf5'
    >>> good_stim_2 = 's3://aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/SpontaneousRewards_670248_20230802_130736.hdf5'
    >>> sync = 's3://aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/20230802T113053.h5'
    >>> validate_stim(good_stim_1, good_stim_2, sync=sync)

    # stim file that doesn't open or has bad data:
    >>> bad_stim = 's3://aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/DynamicRouting1_670248_20230802_120703.hdf5'
    >>> validate_stim(bad_stim, sync=sync)
    Traceback (most recent call last):
    ...
    AssertionError: Failed to validate stim_path = 's3://aind-ephys-data/ecephys_670248_2023-08-02_11-30-53/behavior/DynamicRouting1_670248_20230802_120703.hdf5'
    """

    def validate_single_stim(stim_path, sync=sync) -> None:
        for v in get_stim_frame_times(
            stim_path, sync=sync
        ).values():  # should be only one entry
            assert_stim_times(v)

    logger.info(f"Validating {len(stim_paths)} stim files with sync data")
    for stim_path in stim_paths:
        logger.debug(f"Validating {stim_path = }")
        try:
            validate_single_stim(stim_path)
        except Exception as exc:
            raise AssertionError(f"Failed to validate {stim_path = }") from exc
        logger.info(f"Validated {stim_path = }")


if __name__ == "__main__":
    from npc_stim import testmod

    testmod()
