"""
Configuration File Loader
==========================

Handles loading YAML configuration files for automation scripts.
"""
import os
import yaml


def load_yaml_config(config_path):
    """
    Load a YAML configuration file.

    Args:
        config_path (str): Path to YAML configuration file

    Returns:
        dict: Parsed configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config if config else {}


def get_project_root():
    """
    Get the project root directory (where config/ folder is located).

    Returns:
        str: Absolute path to project root
    """
    # Assumes this file is in utilities/ folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return project_root


def get_config_path(config_filename):
    """
    Get the full path to a configuration file in the config/ directory.

    Args:
        config_filename (str): Name of config file (e.g., 'contact_config.yaml')

    Returns:
        str: Full path to configuration file
    """
    project_root = get_project_root()
    config_path = os.path.join(project_root, 'config', config_filename)
    return config_path
