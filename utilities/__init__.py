"""
ANSYS Tools - Utility Functions
================================

Common utility functions used across all automation scripts.
"""

__version__ = "0.2.0"

# Export commonly used functions for convenient importing
from .logging_config import log, log_section, set_logging
from .config_loader import load_yaml_config, get_config_path, get_project_root
from .named_selection_helper import (
    get_named_selection,
    get_faces_from_named_selection,
    named_selection_to_list,
    normalize_named_selection_list,
    refresh_tree
)
from .geometry_helper import (
    find_coordinate_system,
    create_face_aligned_coordinate_system,
    ensure_construction_geometry,
    find_surface,
    create_surface_from_coordinate_system,
    get_body_from_face,
    delete_coordinate_systems_by_pattern,
    delete_surfaces_by_pattern
)
from .probe_helper import (
    find_probe,
    create_force_reaction_probe,
    create_moment_reaction_probe,
    extract_probe_results,
    find_group,
    create_probe_group,
    manage_probe_groups,
    delete_probes_by_pattern
)

__all__ = [
    # Logging
    'log', 'log_section', 'set_logging',
    # Config
    'load_yaml_config', 'get_config_path', 'get_project_root',
    # Named Selections
    'get_named_selection', 'get_faces_from_named_selection',
    'named_selection_to_list', 'normalize_named_selection_list', 'refresh_tree',
    # Geometry
    'find_coordinate_system', 'create_face_aligned_coordinate_system',
    'ensure_construction_geometry', 'find_surface',
    'create_surface_from_coordinate_system', 'get_body_from_face',
    'delete_coordinate_systems_by_pattern', 'delete_surfaces_by_pattern',
    # Probes
    'find_probe', 'create_force_reaction_probe', 'create_moment_reaction_probe',
    'extract_probe_results', 'find_group', 'create_probe_group',
    'manage_probe_groups', 'delete_probes_by_pattern'
]
