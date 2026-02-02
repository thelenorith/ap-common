"""
Unit tests for ap_common.calibration_matching module.

Generated to address GitHub Issue #36.
"""

import pytest
from ap_common.calibration_matching import (
    find_matching_dark,
    find_matching_bias,
    find_matching_flat,
    find_all_matching_calibrations,
    _get_float_value,
    _get_str_value,
    _matches_camera_settings,
    _is_calibration_type,
)


class TestGetFloatValue:
    """Tests for _get_float_value helper function."""

    def test_valid_float(self):
        """Test extracting a valid float value."""
        metadata = {"exposureseconds": "120.0"}
        result = _get_float_value(metadata, "exposureseconds")
        assert result == 120.0

    def test_valid_int_as_float(self):
        """Test extracting an integer value as float."""
        metadata = {"gain": "100"}
        result = _get_float_value(metadata, "gain")
        assert result == 100.0

    def test_missing_key(self):
        """Test extracting from missing key returns None."""
        metadata = {"other": "value"}
        result = _get_float_value(metadata, "exposureseconds")
        assert result is None

    def test_none_value(self):
        """Test extracting None value returns None."""
        metadata = {"exposureseconds": None}
        result = _get_float_value(metadata, "exposureseconds")
        assert result is None

    def test_invalid_value(self):
        """Test extracting non-numeric value returns None."""
        metadata = {"exposureseconds": "not_a_number"}
        result = _get_float_value(metadata, "exposureseconds")
        assert result is None


class TestGetStrValue:
    """Tests for _get_str_value helper function."""

    def test_valid_string(self):
        """Test extracting a valid string value."""
        metadata = {"camera": "ZWO ASI294"}
        result = _get_str_value(metadata, "camera")
        assert result == "ZWO ASI294"

    def test_numeric_as_string(self):
        """Test extracting a numeric value as string."""
        metadata = {"gain": 100}
        result = _get_str_value(metadata, "gain")
        assert result == "100"

    def test_missing_key(self):
        """Test extracting from missing key returns None."""
        metadata = {"other": "value"}
        result = _get_str_value(metadata, "camera")
        assert result is None

    def test_none_value(self):
        """Test extracting None value returns None."""
        metadata = {"camera": None}
        result = _get_str_value(metadata, "camera")
        assert result is None


class TestMatchesCameraSettings:
    """Tests for _matches_camera_settings helper function."""

    def test_matching_camera_only(self):
        """Test matching when only camera is specified."""
        light = {"camera": "ZWO ASI294"}
        cal = {"camera": "ZWO ASI294"}
        assert _matches_camera_settings(light, cal, match_gain=False, match_offset=False)

    def test_different_cameras(self):
        """Test non-matching when cameras differ."""
        light = {"camera": "ZWO ASI294"}
        cal = {"camera": "ZWO ASI2600"}
        assert not _matches_camera_settings(light, cal)

    def test_matching_camera_and_gain(self):
        """Test matching when camera and gain match."""
        light = {"camera": "ZWO ASI294", "gain": "100"}
        cal = {"camera": "ZWO ASI294", "gain": "100"}
        assert _matches_camera_settings(light, cal, match_offset=False)

    def test_different_gain(self):
        """Test non-matching when gain differs."""
        light = {"camera": "ZWO ASI294", "gain": "100"}
        cal = {"camera": "ZWO ASI294", "gain": "200"}
        assert not _matches_camera_settings(light, cal, match_offset=False)

    def test_matching_all_settings(self):
        """Test matching when all settings match."""
        light = {"camera": "ZWO ASI294", "gain": "100", "offset": "10"}
        cal = {"camera": "ZWO ASI294", "gain": "100", "offset": "10"}
        assert _matches_camera_settings(light, cal)

    def test_different_offset(self):
        """Test non-matching when offset differs."""
        light = {"camera": "ZWO ASI294", "gain": "100", "offset": "10"}
        cal = {"camera": "ZWO ASI294", "gain": "100", "offset": "20"}
        assert not _matches_camera_settings(light, cal)

    def test_missing_camera(self):
        """Test non-matching when camera is missing."""
        light = {"gain": "100"}
        cal = {"camera": "ZWO ASI294", "gain": "100"}
        assert not _matches_camera_settings(light, cal)

    def test_missing_gain_in_both(self):
        """Test matching when gain is missing in both."""
        light = {"camera": "ZWO ASI294"}
        cal = {"camera": "ZWO ASI294"}
        assert _matches_camera_settings(light, cal, match_offset=False)

    def test_missing_gain_in_calibration(self):
        """Test matching when gain is missing in calibration only."""
        light = {"camera": "ZWO ASI294", "gain": "100"}
        cal = {"camera": "ZWO ASI294"}
        # Should match because calibration doesn't have gain to compare
        assert _matches_camera_settings(light, cal, match_offset=False)


class TestIsCalibrationTypeDark:
    """Tests for _is_calibration_type with dark frames."""

    def test_dark_type(self):
        """Test detection of DARK type."""
        metadata = {"type": "DARK"}
        assert _is_calibration_type(metadata, "DARK", "MASTER DARK")

    def test_master_dark_type(self):
        """Test detection of MASTER DARK type."""
        metadata = {"type": "MASTER DARK"}
        assert _is_calibration_type(metadata, "DARK", "MASTER DARK")

    def test_lowercase_dark(self):
        """Test detection of lowercase dark type."""
        metadata = {"type": "dark"}
        assert _is_calibration_type(metadata, "DARK", "MASTER DARK")

    def test_not_dark_type(self):
        """Test non-dark type returns False."""
        metadata = {"type": "LIGHT"}
        assert not _is_calibration_type(metadata, "DARK", "MASTER DARK")

    def test_missing_type(self):
        """Test missing type returns False."""
        metadata = {"camera": "ZWO"}
        assert not _is_calibration_type(metadata, "DARK", "MASTER DARK")


class TestFindMatchingDark:
    """Tests for find_matching_dark function."""

    def test_exact_exposure_match(self):
        """Test finding dark with exact exposure match."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "gain": "100",
            "offset": "10",
        }
        calibration_data = {
            "/path/dark_60s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "60.0",
                "gain": "100",
                "offset": "10",
            },
            "/path/dark_120s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
                "offset": "10",
            },
            "/path/dark_300s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "300.0",
                "gain": "100",
                "offset": "10",
            },
        }

        result = find_matching_dark(light, calibration_data)

        assert result == "/path/dark_120s.fits"

    def test_longer_exposure_when_no_exact_match(self):
        """Test finding longer dark when no exact match available."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "90.0",
            "gain": "100",
            "offset": "10",
        }
        calibration_data = {
            "/path/dark_60s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "60.0",
                "gain": "100",
                "offset": "10",
            },
            "/path/dark_120s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
                "offset": "10",
            },
            "/path/dark_300s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "300.0",
                "gain": "100",
                "offset": "10",
            },
        }

        result = find_matching_dark(light, calibration_data)

        # Should pick the closest longer dark (120s)
        assert result == "/path/dark_120s.fits"

    def test_no_match_when_camera_differs(self):
        """Test no match when camera doesn't match."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "gain": "100",
        }
        calibration_data = {
            "/path/dark_120s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI2600",
                "exposureseconds": "120.0",
                "gain": "100",
            },
        }

        result = find_matching_dark(light, calibration_data)

        assert result is None

    def test_no_match_when_gain_differs(self):
        """Test no match when gain doesn't match."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "gain": "100",
        }
        calibration_data = {
            "/path/dark_120s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "200",
            },
        }

        result = find_matching_dark(light, calibration_data)

        assert result is None

    def test_temperature_tolerance(self):
        """Test temperature tolerance matching."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "gain": "100",
            "settemp": "-10.0",
        }
        calibration_data = {
            "/path/dark_temp5.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
                "settemp": "-5.0",  # 5 degrees difference
            },
            "/path/dark_temp20.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
                "settemp": "10.0",  # 20 degrees difference
            },
        }

        result = find_matching_dark(light, calibration_data, temperature_tolerance=5.0)

        assert result == "/path/dark_temp5.fits"

    def test_temperature_outside_tolerance(self):
        """Test no match when temperature is outside tolerance."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "gain": "100",
            "settemp": "-10.0",
        }
        calibration_data = {
            "/path/dark_temp20.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
                "settemp": "10.0",  # 20 degrees difference
            },
        }

        result = find_matching_dark(light, calibration_data, temperature_tolerance=5.0)

        assert result is None

    def test_master_dark_type(self):
        """Test finding MASTER DARK frames."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "gain": "100",
        }
        calibration_data = {
            "/path/master_dark.fits": {
                "type": "MASTER DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
            },
        }

        result = find_matching_dark(light, calibration_data)

        assert result == "/path/master_dark.fits"

    def test_no_match_when_exposure_too_short(self):
        """Test no match when all darks have shorter exposure."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "300.0",
            "gain": "100",
        }
        calibration_data = {
            "/path/dark_60s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "60.0",
                "gain": "100",
            },
            "/path/dark_120s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
            },
        }

        result = find_matching_dark(light, calibration_data)

        assert result is None

    def test_no_exposure_in_light(self):
        """Test no match when light has no exposure."""
        light = {
            "camera": "ZWO ASI294",
            "gain": "100",
        }
        calibration_data = {
            "/path/dark_120s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
            },
        }

        result = find_matching_dark(light, calibration_data)

        assert result is None

    def test_empty_calibration_data(self):
        """Test no match with empty calibration data."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "gain": "100",
        }

        result = find_matching_dark(light, {})

        assert result is None

    def test_match_without_gain_requirement(self):
        """Test matching when gain requirement is disabled."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "gain": "100",
        }
        calibration_data = {
            "/path/dark_120s.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "200",  # Different gain
            },
        }

        result = find_matching_dark(light, calibration_data, match_gain=False)

        assert result == "/path/dark_120s.fits"


class TestFindMatchingBias:
    """Tests for find_matching_bias function."""

    def test_basic_bias_match(self):
        """Test basic bias matching."""
        light = {
            "camera": "ZWO ASI294",
            "gain": "100",
            "offset": "10",
        }
        calibration_data = {
            "/path/bias.fits": {
                "type": "BIAS",
                "camera": "ZWO ASI294",
                "gain": "100",
                "offset": "10",
            },
        }

        result = find_matching_bias(light, calibration_data)

        assert result == "/path/bias.fits"

    def test_master_bias_match(self):
        """Test matching MASTER BIAS frame."""
        light = {
            "camera": "ZWO ASI294",
            "gain": "100",
            "offset": "10",
        }
        calibration_data = {
            "/path/master_bias.fits": {
                "type": "MASTER BIAS",
                "camera": "ZWO ASI294",
                "gain": "100",
                "offset": "10",
            },
        }

        result = find_matching_bias(light, calibration_data)

        assert result == "/path/master_bias.fits"

    def test_no_match_when_camera_differs(self):
        """Test no match when camera differs."""
        light = {
            "camera": "ZWO ASI294",
            "gain": "100",
        }
        calibration_data = {
            "/path/bias.fits": {
                "type": "BIAS",
                "camera": "ZWO ASI2600",
                "gain": "100",
            },
        }

        result = find_matching_bias(light, calibration_data)

        assert result is None

    def test_no_match_when_gain_differs(self):
        """Test no match when gain differs."""
        light = {
            "camera": "ZWO ASI294",
            "gain": "100",
        }
        calibration_data = {
            "/path/bias.fits": {
                "type": "BIAS",
                "camera": "ZWO ASI294",
                "gain": "200",
            },
        }

        result = find_matching_bias(light, calibration_data)

        assert result is None

    def test_match_without_offset_requirement(self):
        """Test matching when offset requirement is disabled."""
        light = {
            "camera": "ZWO ASI294",
            "gain": "100",
            "offset": "10",
        }
        calibration_data = {
            "/path/bias.fits": {
                "type": "BIAS",
                "camera": "ZWO ASI294",
                "gain": "100",
                "offset": "20",  # Different offset
            },
        }

        result = find_matching_bias(light, calibration_data, match_offset=False)

        assert result == "/path/bias.fits"

    def test_empty_calibration_data(self):
        """Test no match with empty calibration data."""
        light = {
            "camera": "ZWO ASI294",
            "gain": "100",
        }

        result = find_matching_bias(light, {})

        assert result is None

    def test_skips_non_bias_frames(self):
        """Test that non-bias frames are skipped."""
        light = {
            "camera": "ZWO ASI294",
            "gain": "100",
        }
        calibration_data = {
            "/path/dark.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "gain": "100",
            },
            "/path/flat.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "gain": "100",
            },
        }

        result = find_matching_bias(light, calibration_data)

        assert result is None


class TestFindMatchingFlat:
    """Tests for find_matching_flat function."""

    def test_basic_flat_match(self):
        """Test basic flat matching by filter."""
        light = {
            "camera": "ZWO ASI294",
            "filter": "Ha",
            "gain": "100",
        }
        calibration_data = {
            "/path/flat_ha.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "Ha",
                "gain": "100",
            },
        }

        result = find_matching_flat(light, calibration_data)

        assert result == "/path/flat_ha.fits"

    def test_master_flat_match(self):
        """Test matching MASTER FLAT frame."""
        light = {
            "camera": "ZWO ASI294",
            "filter": "OIII",
            "gain": "100",
        }
        calibration_data = {
            "/path/master_flat.fits": {
                "type": "MASTER FLAT",
                "camera": "ZWO ASI294",
                "filter": "OIII",
                "gain": "100",
            },
        }

        result = find_matching_flat(light, calibration_data)

        assert result == "/path/master_flat.fits"

    def test_no_match_when_filter_differs(self):
        """Test no match when filter differs."""
        light = {
            "camera": "ZWO ASI294",
            "filter": "Ha",
            "gain": "100",
        }
        calibration_data = {
            "/path/flat_oiii.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "OIII",
                "gain": "100",
            },
        }

        result = find_matching_flat(light, calibration_data)

        assert result is None

    def test_no_match_when_camera_differs(self):
        """Test no match when camera differs."""
        light = {
            "camera": "ZWO ASI294",
            "filter": "Ha",
            "gain": "100",
        }
        calibration_data = {
            "/path/flat_ha.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI2600",
                "filter": "Ha",
                "gain": "100",
            },
        }

        result = find_matching_flat(light, calibration_data)

        assert result is None

    def test_date_tolerance_match(self):
        """Test matching with date tolerance."""
        light = {
            "camera": "ZWO ASI294",
            "filter": "Ha",
            "gain": "100",
            "date": "2024-01-15",
        }
        calibration_data = {
            "/path/flat_old.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "Ha",
                "gain": "100",
                "date": "2024-01-01",  # 14 days old
            },
            "/path/flat_recent.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "Ha",
                "gain": "100",
                "date": "2024-01-14",  # 1 day old
            },
        }

        result = find_matching_flat(light, calibration_data, date_tolerance_days=7)

        # Should pick the closer date
        assert result == "/path/flat_recent.fits"

    def test_date_tolerance_no_match(self):
        """Test no match when dates are outside tolerance."""
        light = {
            "camera": "ZWO ASI294",
            "filter": "Ha",
            "gain": "100",
            "date": "2024-01-15",
        }
        calibration_data = {
            "/path/flat_old.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "Ha",
                "gain": "100",
                "date": "2023-12-01",  # 45 days old
            },
        }

        result = find_matching_flat(light, calibration_data, date_tolerance_days=30)

        assert result is None

    def test_no_filter_in_light(self):
        """Test no match when light has no filter."""
        light = {
            "camera": "ZWO ASI294",
            "gain": "100",
        }
        calibration_data = {
            "/path/flat_ha.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "Ha",
                "gain": "100",
            },
        }

        result = find_matching_flat(light, calibration_data)

        assert result is None

    def test_empty_calibration_data(self):
        """Test no match with empty calibration data."""
        light = {
            "camera": "ZWO ASI294",
            "filter": "Ha",
            "gain": "100",
        }

        result = find_matching_flat(light, {})

        assert result is None

    def test_match_without_gain_requirement(self):
        """Test matching when gain requirement is disabled."""
        light = {
            "camera": "ZWO ASI294",
            "filter": "Ha",
            "gain": "100",
        }
        calibration_data = {
            "/path/flat_ha.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "Ha",
                "gain": "200",  # Different gain
            },
        }

        result = find_matching_flat(light, calibration_data, match_gain=False)

        assert result == "/path/flat_ha.fits"


class TestFindAllMatchingCalibrations:
    """Tests for find_all_matching_calibrations convenience function."""

    def test_finds_all_calibrations(self):
        """Test finding all calibration types."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "filter": "Ha",
            "gain": "100",
            "offset": "10",
        }
        calibration_data = {
            "/path/dark.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
                "offset": "10",
            },
            "/path/bias.fits": {
                "type": "BIAS",
                "camera": "ZWO ASI294",
                "gain": "100",
                "offset": "10",
            },
            "/path/flat.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "Ha",
                "gain": "100",
                "offset": "10",
            },
        }

        result = find_all_matching_calibrations(light, calibration_data)

        assert result["dark"] == "/path/dark.fits"
        assert result["bias"] == "/path/bias.fits"
        assert result["flat"] == "/path/flat.fits"

    def test_partial_matches(self):
        """Test when only some calibrations match."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "filter": "Ha",
            "gain": "100",
        }
        calibration_data = {
            "/path/dark.fits": {
                "type": "DARK",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
            },
            "/path/bias_wrong_camera.fits": {
                "type": "BIAS",
                "camera": "ZWO ASI2600",  # Different camera
                "gain": "100",
            },
            "/path/flat_wrong_filter.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "OIII",  # Different filter
                "gain": "100",
            },
        }

        result = find_all_matching_calibrations(light, calibration_data)

        assert result["dark"] == "/path/dark.fits"
        assert result["bias"] is None
        assert result["flat"] is None

    def test_no_matches(self):
        """Test when no calibrations match."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "filter": "Ha",
            "gain": "100",
        }
        calibration_data = {
            "/path/light.fits": {
                "type": "LIGHT",
                "camera": "ZWO ASI294",
                "exposureseconds": "120.0",
                "gain": "100",
            },
        }

        result = find_all_matching_calibrations(light, calibration_data)

        assert result["dark"] is None
        assert result["bias"] is None
        assert result["flat"] is None

    def test_empty_calibration_data(self):
        """Test with empty calibration data."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "filter": "Ha",
            "gain": "100",
        }

        result = find_all_matching_calibrations(light, {})

        assert result["dark"] is None
        assert result["bias"] is None
        assert result["flat"] is None

    def test_passes_parameters_correctly(self):
        """Test that parameters are passed to individual functions."""
        light = {
            "camera": "ZWO ASI294",
            "exposureseconds": "120.0",
            "filter": "Ha",
            "gain": "100",
            "date": "2024-01-15",
        }
        calibration_data = {
            "/path/flat.fits": {
                "type": "FLAT",
                "camera": "ZWO ASI294",
                "filter": "Ha",
                "gain": "200",  # Different gain
                "date": "2024-01-10",
            },
        }

        # With match_gain=True (default), should not match
        result1 = find_all_matching_calibrations(light, calibration_data)
        assert result1["flat"] is None

        # With match_gain=False, should match
        result2 = find_all_matching_calibrations(
            light, calibration_data, match_gain=False
        )
        assert result2["flat"] == "/path/flat.fits"
