import re
import os
from pathlib import Path

def safe_slug(text: str) -> str:
    """
    Sanitize a string to be safe for filenames and path components.
    Removes anything that isn't alphanumeric, underscores, or hyphens.
    Prevents path traversal.
    """
    if not text:
        return ""
    # Remove any path traversal attempts
    text = os.path.basename(text)
    # Replace spaces with underscores
    text = text.replace(" ", "_")
    # Remove non-alphanumeric/hyphen/underscore
    return re.sub(r'[^a-zA-Z0-9\-_]', '', text)

def get_project_root() -> Path:
    """Get the absolute path to the project root."""
    return Path(__file__).resolve().parent.parent

def get_env_var(name: str, default=None) -> str:
    """
    Get environment variable with Doppler-ready naming support.
    Will eventually support mapping generic names to project-specific ones.
    """
    # Doppler naming convention: [PROJECT]_[VAR]
    doppler_name = f"D3D_POSE_FACTORY_{name}"
    return os.getenv(doppler_name) or os.getenv(name) or default

# DNA Resilience: Centralized Constants to eliminate Magic Numbers
SDXL_RESOLUTION = 1024
EEVEE_RESOLUTION = 512
DEFAULT_JOB_TIMEOUT = 3600
DEFAULT_SSH_TIMEOUT = 300
STABILITY_COST_PER_IMAGE = 0.04
