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
