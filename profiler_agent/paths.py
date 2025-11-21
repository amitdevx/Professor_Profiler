"""Path configuration for input and output directories."""
import os
from pathlib import Path


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input directory for exam PDFs
INPUT_DIR = PROJECT_ROOT / "input"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
LOGS_DIR = OUTPUT_DIR / "logs"
REPORTS_DIR = OUTPUT_DIR / "reports"


def ensure_directories():
    """Create input/output directories if they don't exist."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def get_input_path(filename: str) -> Path:
    """
    Get full path for an input file.
    
    Args:
        filename: Name of the input file
    
    Returns:
        Path object for the input file
    """
    ensure_directories()
    return INPUT_DIR / filename


def get_output_path(filename: str, subfolder: str = "") -> Path:
    """
    Get full path for an output file.
    
    Args:
        filename: Name of the output file
        subfolder: Optional subfolder (charts, logs, reports)
    
    Returns:
        Path object for the output file
    """
    ensure_directories()
    
    if subfolder:
        base_dir = OUTPUT_DIR / subfolder
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / filename
    
    return OUTPUT_DIR / filename


def list_input_files(extension: str = ".pdf") -> list:
    """
    List all files in the input directory with given extension.
    
    Args:
        extension: File extension to filter (default: .pdf)
    
    Returns:
        List of Path objects for matching files
    """
    ensure_directories()
    
    if not extension.startswith("."):
        extension = f".{extension}"
    
    return list(INPUT_DIR.glob(f"*{extension}"))


# Ensure directories exist on import
ensure_directories()
