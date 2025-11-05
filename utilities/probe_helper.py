"""
Probe Helper Functions
=======================

Common functions for working with ANSYS reaction probes:
- Force reaction probes
- Moment reaction probes
- Probe grouping and management
"""
# pylint: disable=undefined-variable
# pyright: reportUndefinedVariable=false
# type: ignore
# Note: ExtAPI, Model, DataModelObjectCategory, etc. provided by ANSYS Mechanical

from .logging_config import log


# ============================================================================
# Probe Search Functions
# ============================================================================

def find_probe(solution, name, probe_type):
    """
    Find an existing probe by name and type.
    
    Args:
        solution: Analysis solution object
        name (str): Name of the probe to find
        probe_type: Type category (e.g., DataModelObjectCategory.ForceReaction)
        
    Returns:
        Probe object or None if not found
    """
    try:
        for probe in solution.GetChildren(probe_type, True):
            if probe.Name == name:
                log(f"Found existing probe: {name}")
                return probe
    except Exception as e:
        log(f"Error searching for probe '{name}': {str(e)}", "ERROR")
    return None


# ============================================================================
# Probe Creation Functions
# ============================================================================

def create_force_reaction_probe(solution, surface, coordinate_system, body_selection, name):
    """
    Create a force reaction probe, or return existing one if it exists.
    
    Args:
        solution: Analysis solution object
        surface: Construction geometry surface for probe location
        coordinate_system: Coordinate system for orientation
        body_selection: Body selection info for scoping
        name (str): Name for the probe
        
    Returns:
        Force reaction probe object
    """
    # Check if probe already exists
    existing_probe = find_probe(solution, name, DataModelObjectCategory.ForceReaction)
    if existing_probe is not None:
        return existing_probe
    
    try:
        # Create new probe
        probe = solution.AddForceReaction()
        probe.LocationMethod = LocationDefinitionMethod.Surface
        probe.SurfaceSelection = surface
        probe.Orientation = coordinate_system
        probe.GeometryLocation = body_selection
        probe.Name = name
        
        log(f"Created force reaction probe: {name}")
        return probe
    except Exception as e:
        log(f"Error creating force probe '{name}': {str(e)}", "ERROR")
        raise


def create_moment_reaction_probe(solution, surface, coordinate_system, body_selection, name):
    """
    Create a moment reaction probe, or return existing one if it exists.
    
    Args:
        solution: Analysis solution object
        surface: Construction geometry surface for probe location
        coordinate_system: Coordinate system for orientation
        body_selection: Body selection info for scoping
        name (str): Name for the probe
        
    Returns:
        Moment reaction probe object
    """
    # Check if probe already exists
    existing_probe = find_probe(solution, name, DataModelObjectCategory.MomentReaction)
    if existing_probe is not None:
        return existing_probe
    
    try:
        # Create new probe
        probe = solution.AddMomentReaction()
        probe.LocationMethod = LocationDefinitionMethod.Surface
        probe.SurfaceSelection = surface
        probe.Orientation = coordinate_system
        probe.GeometryLocation = body_selection
        probe.Summation = MomentsAtSummationPointType.OrientationSystem
        probe.Name = name
        
        log(f"Created moment reaction probe: {name}")
        return probe
    except Exception as e:
        log(f"Error creating moment probe '{name}': {str(e)}", "ERROR")
        raise


# ============================================================================
# Probe Data Extraction
# ============================================================================

def extract_probe_results(force_probe, moment_probe):
    """
    Extract force and moment data from a probe pair.
    
    Args:
        force_probe: Force reaction probe
        moment_probe: Moment reaction probe
        
    Returns:
        dict: Dictionary containing:
            - name: Coordinate system name
            - fx, fy, fz: Force components
            - mx, my, mz: Moment components
            - x_pos, y_pos, z_pos: Position coordinates
    """
    try:
        results = {
            'name': force_probe.Orientation.Name,
            'fx': force_probe.XAxis.Value,
            'fy': force_probe.YAxis.Value,
            'fz': force_probe.ZAxis.Value,
            'mx': moment_probe.XAxis.Value,
            'my': moment_probe.YAxis.Value,
            'mz': moment_probe.ZAxis.Value,
            'x_pos': force_probe.Orientation.Origin[0],
            'y_pos': force_probe.Orientation.Origin[1],
            'z_pos': force_probe.Orientation.Origin[2]
        }
        return results
    except Exception as e:
        log(f"Error extracting probe results: {str(e)}", "ERROR")
        raise


# ============================================================================
# Probe Grouping Functions
# ============================================================================

def find_group(solution, group_name):
    """
    Find an existing group in the solution by name.
    
    Args:
        solution: Analysis solution object
        group_name (str): Name of the group to find
        
    Returns:
        Group object or None if not found
    """
    try:
        for child in solution.Children:
            if hasattr(child, 'Name') and child.Name == group_name:
                log(f"Found existing group: {group_name}")
                return child
    except Exception as e:
        log(f"Error searching for group '{group_name}': {str(e)}", "ERROR")
    return None


def create_probe_group(probes, group_name):
    """
    Create a group for a list of probes.
    
    Args:
        probes (list): List of probe objects
        group_name (str): Name for the group
        
    Returns:
        Group object
    """
    try:
        group = Tree.Group(probes)
        group.Name = group_name
        log(f"Created probe group: {group_name} with {len(probes)} probe(s)")
        return group
    except Exception as e:
        log(f"Error creating group '{group_name}': {str(e)}", "ERROR")
        raise


def manage_probe_groups(solution, force_probes, moment_probes, base_name):
    """
    Create or update probe groups for force and moment probes.
    
    Creates two groups:
    - Force_Probes_{base_name}
    - Moment_Probes_{base_name}
    
    Args:
        solution: Analysis solution object
        force_probes (list): List of force probe objects
        moment_probes (list): List of moment probe objects
        base_name (str): Base name for the groups (e.g., named selection name)
        
    Returns:
        tuple: (force_group, moment_group)
    """
    force_group_name = f"Force_Probes_{base_name}"
    moment_group_name = f"Moment_Probes_{base_name}"
    
    # Check if groups already exist
    existing_force_group = find_group(solution, force_group_name)
    existing_moment_group = find_group(solution, moment_group_name)
    
    if existing_force_group is not None:
        force_group = existing_force_group
    else:
        force_group = create_probe_group(force_probes, force_group_name)
    
    if existing_moment_group is not None:
        moment_group = existing_moment_group
    else:
        moment_group = create_probe_group(moment_probes, moment_group_name)
    
    return force_group, moment_group


# ============================================================================
# Probe Deletion Functions
# ============================================================================

def delete_probes_by_pattern(solution, name_pattern):
    """
    Delete all probes whose names start with the given pattern.
    
    Args:
        solution: Analysis solution object
        name_pattern (str): Name pattern to match (using startswith)
        
    Returns:
        int: Total number of probes deleted
    """
    total_count = 0
    probes_to_delete = []
    
    try:
        # Collect probes to delete
        for child in solution.Children:
            try:
                if hasattr(child, 'Name') and child.Name.startswith(name_pattern):
                    probes_to_delete.append(child)
                    total_count += 1
            except:
                continue
        
        # Delete collected probes
        with Transaction():
            for probe in probes_to_delete:
                try:
                    probe.Delete()
                except:
                    log(f"Warning: Could not delete probe: {probe.Name}", "WARNING")
        
        if total_count > 0:
            log(f"Deleted {total_count} probe(s) matching pattern '{name_pattern}'")
        
    except Exception as e:
        log(f"Error deleting probes: {str(e)}", "ERROR")
    
    return total_count
