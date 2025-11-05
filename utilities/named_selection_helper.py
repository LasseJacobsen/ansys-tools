"""
Named Selection Helper Functions
=================================

Common functions for working with ANSYS named selections.
"""
# pylint: disable=undefined-variable
# pyright: reportUndefinedVariable=false
# type: ignore
# Note: ExtAPI is provided by ANSYS Mechanical runtime environment

from .logging_config import log


def get_named_selection(named_selection_name):
    """
    Retrieve a named selection by name using ANSYS best practice API.

    Args:
        named_selection_name (str): Name of the named selection

    Returns:
        Named selection object or None if not found
    """
    try:
        # Use GetObjectsByName as per ANSYS best practices
        results = ExtAPI.DataModel.GetObjectsByName(named_selection_name)

        if results and len(results) > 0:
            log(f"Found named selection '{named_selection_name}'")
            return results[0]
        else:
            log(f"Named selection '{named_selection_name}' not found", "WARNING")
            return None

    except Exception as e:
        log(f"Error getting named selection '{named_selection_name}': {str(e)}", "ERROR")
        return None


def get_faces_from_named_selection(named_selection):
    """
    Extract individual faces from a named selection.

    Args:
        named_selection: Named selection object

    Returns:
        list: List of face objects from the named selection
    """
    try:
        faces = []
        selection_info = named_selection.Location

        # Convert to list if it's a single item
        if hasattr(selection_info, '__iter__'):
            for item in selection_info:
                faces.append(item)
        else:
            faces.append(selection_info)

        log(f"Extracted {len(faces)} face(s) from named selection")
        return faces

    except Exception as e:
        log(f"Error extracting faces from named selection: {str(e)}", "ERROR")
        return []


def refresh_tree():
    """
    Refresh the ANSYS Mechanical object tree to show changes.
    """
    try:
        ExtAPI.DataModel.Tree.Refresh()
        log("Refreshed object tree")
    except Exception as e:
        log(f"Error refreshing tree: {str(e)}", "ERROR")


def named_selection_to_list(named_selection):
    """
    Convert a named selection to an iterable list of geometry entities.
    
    Uses the selection manager to properly extract entities from named selections.
    This is the recommended approach for working with named selection contents.
    
    Args:
        named_selection: ANSYS named selection object
        
    Returns:
        list: List of geometry entities from the named selection
    """
    try:
        selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        selection.Ids = named_selection.Ids
        entities = list(selection.Entities)
        log(f"Extracted {len(entities)} entities from named selection")
        return entities
    except Exception as e:
        log(f"Error converting named selection to list: {str(e)}", "ERROR")
        return []


def normalize_named_selection_list(ns_config):
    """
    Normalize the named selection configuration to a list.
    
    Handles both single string and list/tuple inputs, converting to a standardized list format.
    
    Args:
        ns_config: Either a string (single name) or list/tuple of strings (multiple names)
        
    Returns:
        list: List of named selection names
        
    Raises:
        ValueError: If input is not a string or list/tuple
    """
    if isinstance(ns_config, str):
        return [ns_config]
    elif isinstance(ns_config, (list, tuple)):
        return list(ns_config)
    else:
        raise ValueError("Named selection configuration must be a string or list/tuple")

