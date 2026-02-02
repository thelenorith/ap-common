"""
Calibration frame matching functions for astrophotography processing.

This module provides functions to find matching master calibration frames
(darks, biases, flats) for light frames based on their metadata properties.

Generated to address GitHub Issue #36 - Extract master frame matching logic
from ap-copy-master-to-blink.
"""

from datetime import datetime, timedelta
from typing import Optional

from ap_common.constants import (
    NORMALIZED_HEADER_CAMERA,
    NORMALIZED_HEADER_EXPOSURESECONDS,
    NORMALIZED_HEADER_FILTER,
    NORMALIZED_HEADER_GAIN,
    NORMALIZED_HEADER_OFFSET,
    NORMALIZED_HEADER_SETTEMP,
    NORMALIZED_HEADER_DATE,
    NORMALIZED_HEADER_TYPE,
    TYPE_MASTER_DARK,
    TYPE_MASTER_BIAS,
    TYPE_MASTER_FLAT,
    TYPE_DARK,
    TYPE_BIAS,
    TYPE_FLAT,
)


def _get_float_value(metadata: dict, key: str) -> Optional[float]:
    """
    Safely extract a float value from metadata.

    Args:
        metadata: Dictionary containing frame metadata
        key: The key to extract

    Returns:
        Float value or None if not present or not convertible
    """
    value = metadata.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _get_str_value(metadata: dict, key: str) -> Optional[str]:
    """
    Safely extract a string value from metadata.

    Args:
        metadata: Dictionary containing frame metadata
        key: The key to extract

    Returns:
        String value or None if not present
    """
    value = metadata.get(key)
    if value is None:
        return None
    return str(value)


def _matches_camera_settings(
    light_metadata: dict,
    calibration_metadata: dict,
    match_gain: bool = True,
    match_offset: bool = True,
) -> bool:
    """
    Check if calibration frame matches the camera settings of a light frame.

    Args:
        light_metadata: Dictionary containing light frame metadata
        calibration_metadata: Dictionary containing calibration frame metadata
        match_gain: Whether to require gain match
        match_offset: Whether to require offset match

    Returns:
        True if the camera settings match, False otherwise
    """
    # Camera must match
    light_camera = _get_str_value(light_metadata, NORMALIZED_HEADER_CAMERA)
    cal_camera = _get_str_value(calibration_metadata, NORMALIZED_HEADER_CAMERA)

    if light_camera is None or cal_camera is None:
        return False
    if light_camera != cal_camera:
        return False

    # Gain must match if required
    if match_gain:
        light_gain = _get_float_value(light_metadata, NORMALIZED_HEADER_GAIN)
        cal_gain = _get_float_value(calibration_metadata, NORMALIZED_HEADER_GAIN)

        # If both have gain values, they must match
        if light_gain is not None and cal_gain is not None:
            if light_gain != cal_gain:
                return False

    # Offset must match if required
    if match_offset:
        light_offset = _get_float_value(light_metadata, NORMALIZED_HEADER_OFFSET)
        cal_offset = _get_float_value(calibration_metadata, NORMALIZED_HEADER_OFFSET)

        # If both have offset values, they must match
        if light_offset is not None and cal_offset is not None:
            if light_offset != cal_offset:
                return False

    return True


def _is_calibration_type(metadata: dict, calibration_type: str, master_type: str) -> bool:
    """
    Check if metadata represents a specific calibration type.

    Args:
        metadata: Dictionary containing frame metadata
        calibration_type: The raw calibration type (e.g., "DARK")
        master_type: The master calibration type (e.g., "MASTER DARK")

    Returns:
        True if the frame is of the specified calibration type
    """
    frame_type = _get_str_value(metadata, NORMALIZED_HEADER_TYPE)
    if frame_type is None:
        return False
    frame_type_upper = frame_type.upper()
    return frame_type_upper == calibration_type or frame_type_upper == master_type


def find_matching_dark(
    light_metadata: dict,
    calibration_data: dict,
    temperature_tolerance: float = 5.0,
    prefer_exact_exposure: bool = True,
    match_gain: bool = True,
    match_offset: bool = True,
) -> Optional[str]:
    """
    Find a matching dark frame for a given light frame.

    The matching logic prioritizes:
    1. Exact exposure time match (if prefer_exact_exposure is True)
    2. Longest exposure time that is less than or equal to the light exposure
    3. Temperature within tolerance (if set temperature is available)
    4. Camera, gain, and offset must match

    Args:
        light_metadata: Dictionary containing light frame metadata
        calibration_data: Dictionary mapping filenames to metadata dictionaries
            for calibration frames
        temperature_tolerance: Maximum temperature difference in degrees to consider
            a match (default: 5.0)
        prefer_exact_exposure: If True, prefer exact exposure match over longer darks
            (default: True)
        match_gain: Whether to require gain match (default: True)
        match_offset: Whether to require offset match (default: True)

    Returns:
        Filename of the best matching dark frame, or None if no match found
    """
    light_exposure = _get_float_value(light_metadata, NORMALIZED_HEADER_EXPOSURESECONDS)
    light_temp = _get_float_value(light_metadata, NORMALIZED_HEADER_SETTEMP)

    if light_exposure is None:
        return None

    candidates = []

    for filename, cal_metadata in calibration_data.items():
        # Check if it's a dark frame
        if not _is_calibration_type(cal_metadata, TYPE_DARK, TYPE_MASTER_DARK):
            continue

        # Check camera settings match
        if not _matches_camera_settings(
            light_metadata, cal_metadata, match_gain=match_gain, match_offset=match_offset
        ):
            continue

        # Get dark exposure
        dark_exposure = _get_float_value(cal_metadata, NORMALIZED_HEADER_EXPOSURESECONDS)
        if dark_exposure is None:
            continue

        # Dark exposure must be >= light exposure (or can use shorter darks)
        # Typically we want dark exposure >= light exposure
        if dark_exposure < light_exposure:
            continue

        # Check temperature tolerance if both have temperature data
        dark_temp = _get_float_value(cal_metadata, NORMALIZED_HEADER_SETTEMP)
        if light_temp is not None and dark_temp is not None:
            if abs(light_temp - dark_temp) > temperature_tolerance:
                continue

        # Calculate match score (exact exposure match is best)
        is_exact = abs(dark_exposure - light_exposure) < 0.001
        exposure_diff = dark_exposure - light_exposure

        candidates.append({
            "filename": filename,
            "is_exact": is_exact,
            "exposure_diff": exposure_diff,
            "exposure": dark_exposure,
        })

    if not candidates:
        return None

    # Sort candidates:
    # - If prefer_exact_exposure: exact matches first, then by smallest exposure difference
    # - Otherwise: just by smallest exposure difference (closest to light exposure)
    if prefer_exact_exposure:
        candidates.sort(key=lambda x: (not x["is_exact"], x["exposure_diff"]))
    else:
        candidates.sort(key=lambda x: x["exposure_diff"])

    return candidates[0]["filename"]


def find_matching_bias(
    light_metadata: dict,
    calibration_data: dict,
    match_gain: bool = True,
    match_offset: bool = True,
) -> Optional[str]:
    """
    Find a matching bias frame for a given light frame.

    Bias frames are matched based on:
    1. Camera must match
    2. Gain must match (if available and match_gain is True)
    3. Offset must match (if available and match_offset is True)

    Args:
        light_metadata: Dictionary containing light frame metadata
        calibration_data: Dictionary mapping filenames to metadata dictionaries
            for calibration frames
        match_gain: Whether to require gain match (default: True)
        match_offset: Whether to require offset match (default: True)

    Returns:
        Filename of the matching bias frame, or None if no match found
    """
    for filename, cal_metadata in calibration_data.items():
        # Check if it's a bias frame
        if not _is_calibration_type(cal_metadata, TYPE_BIAS, TYPE_MASTER_BIAS):
            continue

        # Check camera settings match
        if not _matches_camera_settings(
            light_metadata, cal_metadata, match_gain=match_gain, match_offset=match_offset
        ):
            continue

        # Found a matching bias
        return filename

    return None


def find_matching_flat(
    light_metadata: dict,
    calibration_data: dict,
    date_tolerance_days: Optional[int] = None,
    match_gain: bool = True,
    match_offset: bool = True,
) -> Optional[str]:
    """
    Find a matching flat frame for a given light frame.

    Flat frames are matched based on:
    1. Filter must match
    2. Camera must match
    3. Gain and offset must match (if required)
    4. Date within tolerance (if date_tolerance_days is specified)

    Args:
        light_metadata: Dictionary containing light frame metadata
        calibration_data: Dictionary mapping filenames to metadata dictionaries
            for calibration frames
        date_tolerance_days: Maximum number of days difference between light
            and flat capture dates. If None, date is not considered.
        match_gain: Whether to require gain match (default: True)
        match_offset: Whether to require offset match (default: True)

    Returns:
        Filename of the best matching flat frame, or None if no match found
    """
    light_filter = _get_str_value(light_metadata, NORMALIZED_HEADER_FILTER)
    light_date_str = _get_str_value(light_metadata, NORMALIZED_HEADER_DATE)

    if light_filter is None:
        return None

    # Parse light date if date tolerance is specified
    light_date = None
    if date_tolerance_days is not None and light_date_str is not None:
        try:
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%Y%m%d", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    light_date = datetime.strptime(light_date_str[:len(fmt.replace("%", "").replace("-", "").replace(":", "").replace("T", "")) + 4], fmt)
                    break
                except ValueError:
                    continue
            # If the above fails, try a simpler approach
            if light_date is None:
                # Just try to parse YYYY-MM-DD from the beginning
                light_date = datetime.strptime(light_date_str[:10], "%Y-%m-%d")
        except (ValueError, IndexError):
            light_date = None

    candidates = []

    for filename, cal_metadata in calibration_data.items():
        # Check if it's a flat frame
        if not _is_calibration_type(cal_metadata, TYPE_FLAT, TYPE_MASTER_FLAT):
            continue

        # Check camera settings match
        if not _matches_camera_settings(
            light_metadata, cal_metadata, match_gain=match_gain, match_offset=match_offset
        ):
            continue

        # Filter must match
        flat_filter = _get_str_value(cal_metadata, NORMALIZED_HEADER_FILTER)
        if flat_filter is None or flat_filter != light_filter:
            continue

        # Check date tolerance if specified
        days_diff = None
        if date_tolerance_days is not None and light_date is not None:
            flat_date_str = _get_str_value(cal_metadata, NORMALIZED_HEADER_DATE)
            if flat_date_str is not None:
                try:
                    # Try to parse flat date
                    flat_date = None
                    for fmt in ["%Y-%m-%d", "%Y%m%d", "%Y-%m-%dT%H:%M:%S"]:
                        try:
                            flat_date = datetime.strptime(flat_date_str[:len(fmt.replace("%", "").replace("-", "").replace(":", "").replace("T", "")) + 4], fmt)
                            break
                        except ValueError:
                            continue
                    if flat_date is None:
                        flat_date = datetime.strptime(flat_date_str[:10], "%Y-%m-%d")

                    days_diff = abs((light_date - flat_date).days)
                    if days_diff > date_tolerance_days:
                        continue
                except (ValueError, IndexError):
                    # If we can't parse the date, skip date check
                    pass

        candidates.append({
            "filename": filename,
            "days_diff": days_diff if days_diff is not None else float("inf"),
        })

    if not candidates:
        return None

    # Sort by date difference (closest date first)
    candidates.sort(key=lambda x: x["days_diff"])

    return candidates[0]["filename"]


def find_all_matching_calibrations(
    light_metadata: dict,
    calibration_data: dict,
    temperature_tolerance: float = 5.0,
    date_tolerance_days: Optional[int] = None,
    prefer_exact_exposure: bool = True,
    match_gain: bool = True,
    match_offset: bool = True,
) -> dict:
    """
    Find all matching calibration frames (dark, bias, flat) for a light frame.

    This is a convenience function that calls find_matching_dark, find_matching_bias,
    and find_matching_flat and returns the results in a dictionary.

    Args:
        light_metadata: Dictionary containing light frame metadata
        calibration_data: Dictionary mapping filenames to metadata dictionaries
            for calibration frames
        temperature_tolerance: Maximum temperature difference for dark matching
        date_tolerance_days: Maximum days difference for flat matching (None = ignore)
        prefer_exact_exposure: If True, prefer exact exposure match for darks
        match_gain: Whether to require gain match
        match_offset: Whether to require offset match

    Returns:
        Dictionary with keys 'dark', 'bias', 'flat' containing the matching
        filename for each type, or None if no match found
    """
    return {
        "dark": find_matching_dark(
            light_metadata=light_metadata,
            calibration_data=calibration_data,
            temperature_tolerance=temperature_tolerance,
            prefer_exact_exposure=prefer_exact_exposure,
            match_gain=match_gain,
            match_offset=match_offset,
        ),
        "bias": find_matching_bias(
            light_metadata=light_metadata,
            calibration_data=calibration_data,
            match_gain=match_gain,
            match_offset=match_offset,
        ),
        "flat": find_matching_flat(
            light_metadata=light_metadata,
            calibration_data=calibration_data,
            date_tolerance_days=date_tolerance_days,
            match_gain=match_gain,
            match_offset=match_offset,
        ),
    }
