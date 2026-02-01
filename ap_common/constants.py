"""
Constants for headers and directories used across ap-common tools.

This module centralizes all constants that are peppered throughout
related projects, making them easier to maintain and use consistently.

Generated to address GitHub Issue #9.
"""

# =============================================================================
# Directory Constants
# =============================================================================

# The canonical "accept" directory in file paths
# Used to identify where OBJECT names should be extracted from parent directory
DIRECTORY_ACCEPT = "accept"

# =============================================================================
# FITS Header Constants - Standard Keys
# =============================================================================

# Date and time headers
HEADER_DATE_OBS = "DATE-OBS"

# Image type header
HEADER_IMAGETYP = "IMAGETYP"

# Telescope/Optic header
HEADER_TELESCOP = "TELESCOP"

# Focal ratio header
HEADER_FOCRATIO = "FOCRATIO"

# Camera/Instrument header
HEADER_INSTRUME = "INSTRUME"

# Object/Target header
HEADER_OBJECT = "OBJECT"

# Filter header
HEADER_FILTER = "FILTER"

# Exposure time headers (multiple alternatives)
HEADER_EXPOSURE = "EXPOSURE"
HEADER_EXPTIME = "EXPTIME"
HEADER_EXP = "EXP"

# Temperature headers
HEADER_CCD_TEMP = "CCD-TEMP"
HEADER_SETTEMP = "SETTEMP"
HEADER_SET_TEMP = "SET-TEMP"

# Location headers
HEADER_SITELAT = "SITELAT"
HEADER_SITELONG = "SITELONG"
HEADER_OBSGEO_B = "OBSGEO-B"
HEADER_OBSGEO_L = "OBSGEO-L"

# Readout mode header
HEADER_READOUTM = "READOUTM"

# Camera settings headers
HEADER_GAIN = "GAIN"
HEADER_OFFSET = "OFFSET"

# Focal length header
HEADER_FOCALLEN = "FOCALLEN"

# =============================================================================
# Normalized Header Names
# These are the standardized keys used internally after header normalization
# =============================================================================

NORMALIZED_HEADER_DATE = "date"
NORMALIZED_HEADER_DATETIME = "datetime"
NORMALIZED_HEADER_TYPE = "type"
NORMALIZED_HEADER_OPTIC = "optic"
NORMALIZED_HEADER_FOCAL_RATIO = "focal_ratio"
NORMALIZED_HEADER_CAMERA = "camera"
NORMALIZED_HEADER_TARGETNAME = "targetname"
NORMALIZED_HEADER_FILTER = "filter"
NORMALIZED_HEADER_EXPOSURESECONDS = "exposureseconds"
NORMALIZED_HEADER_TEMP = "temp"
NORMALIZED_HEADER_SETTEMP = "settemp"
NORMALIZED_HEADER_LATITUDE = "latitude"
NORMALIZED_HEADER_LONGITUDE = "longitude"
NORMALIZED_HEADER_READOUTMODE = "readoutmode"
NORMALIZED_HEADER_GAIN = "gain"
NORMALIZED_HEADER_OFFSET = "offset"
NORMALIZED_HEADER_FOCALLEN = "focallen"
NORMALIZED_HEADER_PANEL = "panel"
NORMALIZED_HEADER_FILENAME = "filename"
NORMALIZED_HEADER_HFR = "hfr"
NORMALIZED_HEADER_STARS = "stars"
NORMALIZED_HEADER_RMSAC = "rmsac"

# =============================================================================
# Image Type Constants - Raw Frames
# =============================================================================

TYPE_LIGHT = "LIGHT"
TYPE_DARK = "DARK"
TYPE_FLAT = "FLAT"
TYPE_BIAS = "BIAS"

# =============================================================================
# Image Type Constants - Master (Stacked) Frames
# =============================================================================

TYPE_MASTER_LIGHT = "MASTER LIGHT"
TYPE_MASTER_DARK = "MASTER DARK"
TYPE_MASTER_FLAT = "MASTER FLAT"
TYPE_MASTER_BIAS = "MASTER BIAS"

# =============================================================================
# Calibration Frame Type Lists
# These lists are useful for filtering/grouping calibration frames
# =============================================================================

# Raw calibration frame types (individual sub-exposures)
CALIBRATION_TYPES = [TYPE_DARK, TYPE_FLAT, TYPE_BIAS]

# Master calibration frame types (stacked calibration frames)
MASTER_CALIBRATION_TYPES = [TYPE_MASTER_DARK, TYPE_MASTER_FLAT, TYPE_MASTER_BIAS]

# All calibration types (both raw and master)
ALL_CALIBRATION_TYPES = CALIBRATION_TYPES + MASTER_CALIBRATION_TYPES

# =============================================================================
# File Extension Constants
# =============================================================================

FILE_EXTENSION_FITS = ".fits"
FILE_EXTENSION_XISF = ".xisf"
FILE_EXTENSION_CR2 = ".cr2"

# Default file patterns
DEFAULT_FITS_PATTERN = r".*\.fits$"
DEFAULT_XISF_PATTERN = r".*\.xisf$"
DEFAULT_CR2_PATTERN = r".*\.cr2$"
DEFAULT_IMAGE_PATTERNS = [DEFAULT_FITS_PATTERN]
