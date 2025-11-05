"""
Geometry Helper Functions
==========================

Common functions for working with ANSYS geometry objects:
- Coordinate systems
- Construction geometry surfaces
- Body scoping and traversal
"""
# pylint: disable=undefined-variable
# pyright: reportUndefinedVariable=false
# type: ignore
# Note: ExtAPI, Model, DataModelObjectCategory, etc. provided by ANSYS Mechanical

from .logging_config import log


# ============================================================================
# Coordinate System Functions
# ============================================================================

def find_coordinate_system(name):
    """
    Find an existing coordinate system by name.
    
    Args:
        name (str): Name of the coordinate system to find
        
    Returns:
        Coordinate system object or None if not found
    """
    try:
        for cs in Model.CoordinateSystems.GetChildren(DataModelObjectCategory.CoordinateSystem, True):
            if cs.Name == name:
                log(f"Found existing coordinate system: {name}")
                return cs
    except Exception as e:
        log(f"Error searching for coordinate system '{name}': {str(e)}", "ERROR")
    return None


def create_face_aligned_coordinate_system(face, name):
    """
    Create a coordinate system aligned to a face with Z-axis normal to the face.
    
    If a coordinate system with the given name already exists, returns the existing one.
    
    Args:
        face: Geometry face entity
        name (str): Name for the coordinate system
        
    Returns:
        Coordinate system object
    """
    # Check if coordinate system already exists
    existing_cs = find_coordinate_system(name)
    if existing_cs is not None:
        return existing_cs
    
    try:
        # Create geometry selection for the face
        geo_selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        geo_selection.Ids = [face.Id]
        
        # Create coordinate system
        cs = Model.CoordinateSystems.AddCoordinateSystem()
        cs.Name = name
        cs.OriginLocation = geo_selection
        cs.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.Associative
        cs.PrimaryAxisLocation = geo_selection
        cs.PrimaryAxis = CoordinateSystemAxisType.PositiveZAxis
        
        log(f"Created coordinate system: {name}")
        return cs
    except Exception as e:
        log(f"Error creating coordinate system '{name}': {str(e)}", "ERROR")
        raise


# ============================================================================
# Construction Geometry Functions
# ============================================================================

def ensure_construction_geometry():
    """
    Ensure that the Construction Geometry section exists in the model.
    Creates it if it doesn't exist.
    
    Returns:
        Construction geometry object
    """
    try:
        # Check if Construction Geometry folder exists
        for child in Model.GetChildren(DataModelObjectCategory.ConstructionGeometry, False):
            return child
        
        # If it doesn't exist, add it
        construction_geo = Model.AddConstructionGeometry()
        log("Created Construction Geometry folder")
        return construction_geo
    except Exception as e:
        log(f"Error ensuring construction geometry: {str(e)}", "ERROR")
        raise


def find_surface(construction_geo, name):
    """
    Find an existing surface in construction geometry by name.
    
    Args:
        construction_geo: Construction geometry object
        name (str): Name of the surface to find
        
    Returns:
        Surface object or None if not found
    """
    try:
        for surface in construction_geo.GetChildren(DataModelObjectCategory.Surface, True):
            if surface.Name == name:
                log(f"Found existing surface: {name}")
                return surface
    except Exception as e:
        log(f"Error searching for surface '{name}': {str(e)}", "ERROR")
    return None


def create_surface_from_coordinate_system(coordinate_system, name):
    """
    Create a construction geometry surface from a coordinate system.
    
    If a surface with the given name already exists, returns the existing one.
    
    Args:
        coordinate_system: Coordinate system object
        name (str): Name for the surface
        
    Returns:
        Construction geometry surface
    """
    construction_geo = ensure_construction_geometry()
    
    # Check if surface already exists
    existing_surface = find_surface(construction_geo, name)
    if existing_surface is not None:
        return existing_surface
    
    try:
        # Create new surface
        surface = construction_geo.AddSurface()
        surface.CoordinateSystem = coordinate_system
        surface.Name = name
        log(f"Created surface: {name}")
        return surface
    except Exception as e:
        log(f"Error creating surface '{name}': {str(e)}", "ERROR")
        raise


# ============================================================================
# Body Scoping Functions
# ============================================================================

def get_body_from_face(face_id):
    """
    Get the body that owns a given face.
    
    This function traverses the geometry hierarchy to find the body containing
    the specified face. Each call creates a NEW selection object to avoid
    reference issues in ANSYS.
    
    Args:
        face_id: ID of the face
        
    Returns:
        tuple: (body_selection, body_id, body_name)
            - body_selection: SelectionInfo object scoped to the body
            - body_id: Integer ID of the body
            - body_name: String name of the body
            
    Raises:
        ValueError: If the body cannot be determined from the face
    """
    try:
        # Get the geometry entity for this face
        geo_entity = ExtAPI.DataModel.GeoData.GeoEntityById(face_id)
        
        # The face directly knows which body it belongs to
        if not geo_entity.Bodies or len(geo_entity.Bodies) == 0:
            raise ValueError(f"Could not get body from face {face_id}")
        
        body = geo_entity.Bodies[0]
        
        # Create a NEW selection info for the body (important: new object each time)
        body_selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        body_selection.Ids = [body.Id]
        
        # Get body name for logging
        try:
            body_name = body.Name
        except:
            body_name = f"Body_{body.Id}"
        
        log(f"Face ID {face_id} -> Body: {body_name} (ID: {body.Id})")
        return body_selection, body.Id, body_name
        
    except Exception as e:
        log(f"Error getting body from face {face_id}: {str(e)}", "ERROR")
        raise ValueError(f"Could not determine body for face {face_id}: {str(e)}")


# ============================================================================
# Deletion/Cleanup Functions
# ============================================================================

def delete_coordinate_systems_by_pattern(name_pattern):
    """
    Delete all coordinate systems whose names start with the given pattern.
    
    Args:
        name_pattern (str): Name pattern to match (using startswith)
        
    Returns:
        int: Number of coordinate systems deleted
    """
    count = 0
    cs_to_delete = []
    
    try:
        # Collect coordinate systems to delete
        for cs in Model.CoordinateSystems.GetChildren(DataModelObjectCategory.CoordinateSystem, True):
            try:
                if cs.Name.startswith(name_pattern):
                    cs_to_delete.append(cs)
                    count += 1
            except:
                continue
        
        # Delete collected coordinate systems
        with Transaction():
            for cs in cs_to_delete:
                try:
                    cs.Delete()
                except:
                    log(f"Warning: Could not delete coordinate system: {cs.Name}", "WARNING")
        
        if count > 0:
            log(f"Deleted {count} coordinate system(s) matching pattern '{name_pattern}'")
        
    except Exception as e:
        log(f"Error deleting coordinate systems: {str(e)}", "ERROR")
    
    return count


def delete_surfaces_by_pattern(name_pattern):
    """
    Delete all construction geometry surfaces whose names start with the given pattern.
    
    Args:
        name_pattern (str): Name pattern to match (using startswith)
        
    Returns:
        int: Number of surfaces deleted
    """
    count = 0
    
    try:
        construction_geo = ensure_construction_geometry()
        if construction_geo is None:
            return 0
        
        # Collect surfaces to delete
        surfaces_to_delete = []
        for surface in construction_geo.GetChildren(DataModelObjectCategory.Surface, True):
            try:
                if surface.Name.startswith(name_pattern):
                    surfaces_to_delete.append(surface)
                    count += 1
            except:
                continue
        
        # Delete collected surfaces
        with Transaction():
            for surface in surfaces_to_delete:
                try:
                    surface.Delete()
                except:
                    log(f"Warning: Could not delete surface: {surface.Name}", "WARNING")
        
        if count > 0:
            log(f"Deleted {count} surface(s) matching pattern '{name_pattern}'")
        
    except Exception as e:
        log(f"Error deleting surfaces: {str(e)}", "ERROR")
    
    return count
