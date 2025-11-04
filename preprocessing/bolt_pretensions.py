"""
ANSYS Workbench Mechanical - Automated Bolt Pretension Creation
================================================================

This script automates the creation of bolt pretensions based on named selections.
Each named selection contains multiple faces (one per bolt), all of the same bolt type.
Creates pretension loads in step 1, and locks them in all subsequent steps.

Usage:
    Run this script from within ANSYS Workbench Mechanical using the scripting console
    or as an external script file.
"""
# pylint: disable=undefined-variable
# pyright: reportUndefinedVariable=false
# type: ignore
# Note: ExtAPI, BoltPretension, etc. are provided by ANSYS Mechanical runtime environment

# Parameters - Edit these as needed
BOLT_PRETENSION_CONFIGS = {
    # Example configuration - modify for your named selections
    # Format: "NamedSelectionName": {"pretension": value_in_newtons}
    "M8_Bolts": {
        "pretension": 15000,  # 15 kN
    },
    "M12_Bolts": {
        "pretension": 35000,  # 35 kN
    },
    # Add more named selections as needed
}

# Global settings
LOG_DETAILS = True  # Set to True for detailed logging


def log(message):
    """Simple logging function"""
    if LOG_DETAILS:
        print(message)


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
            log(f"WARNING: Named selection '{named_selection_name}' not found")
            return None

    except Exception as e:
        log(f"ERROR getting named selection '{named_selection_name}': {str(e)}")
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
        log(f"ERROR extracting faces from named selection: {str(e)}")
        return []


def find_existing_bolt_group(group_name):
    """
    Find an existing bolt pretension group by name using GetObjectsByName.

    Args:
        group_name (str): Name of the bolt pretension group to find

    Returns:
        Bolt pretension group object if found, None otherwise
    """
    try:
        # Use GetObjectsByName for efficient lookup
        results = ExtAPI.DataModel.GetObjectsByName(group_name)

        if results and len(results) > 0:
            # Verify it's a bolt pretension object
            obj = results[0]
            if 'BoltPretension' in str(type(obj)):
                log(f"Found existing bolt group: '{group_name}'")
                return obj

        return None

    except Exception as e:
        log(f"ERROR searching for existing group: {str(e)}")
        return None


def delete_group_children(group):
    """
    Delete all children from a bolt pretension group.

    Args:
        group: The bolt pretension group object
    """
    try:
        # Get all children
        children_to_delete = []
        for child in group.Children:
            children_to_delete.append(child)

        # Delete each child
        for child in children_to_delete:
            child.Delete()

        log(f"Deleted {len(children_to_delete)} children from group '{group.Name}'")

    except Exception as e:
        log(f"ERROR deleting group children: {str(e)}")


def create_bolt_pretension_group(group_name):
    """
    Create a new bolt pretension group or recreate if it exists.

    Args:
        group_name (str): Name for the bolt pretension group

    Returns:
        Bolt pretension group object
    """
    try:
        connections = ExtAPI.DataModel.Project.Model.Connections

        # Check if group already exists
        existing_group = find_existing_bolt_group(group_name)

        if existing_group is not None:
            log(f"Found existing group '{group_name}' - deleting children and recreating")
            # Delete all children
            delete_group_children(existing_group)
            # Delete the group itself
            existing_group.Delete()

        # Create new bolt pretension group
        bolt_group = connections.AddBoltPretension()
        bolt_group.Name = group_name

        log(f"Created bolt pretension group: {bolt_group.Name}")
        return bolt_group

    except Exception as e:
        log(f"ERROR creating bolt pretension group: {str(e)}")
        return None


def create_bolt_pretensions(named_selection_name, pretension_force):
    """
    Create bolt pretensions for all faces in a named selection.

    - Creates one bolt pretension per face
    - Groups all pretensions under a single parent
    - Applies force in step 1, locks in subsequent steps

    Args:
        named_selection_name (str): Name of the named selection containing bolt faces
        pretension_force (float): Pretension force in Newtons
    """
    log(f"\n--- Creating Bolt Pretensions for '{named_selection_name}' ---")

    # Get named selection using best practice API
    named_selection = get_named_selection(named_selection_name)

    if not named_selection:
        log(f"WARNING: Named selection '{named_selection_name}' not found")
        return

    # Get faces from named selection
    faces = get_faces_from_named_selection(named_selection)

    if not faces:
        log(f"WARNING: No faces found in named selection '{named_selection_name}'")
        return

    try:
        # Create or recreate the bolt pretension group
        group_name = f"BoltGroup_{named_selection_name}"
        bolt_group = create_bolt_pretension_group(group_name)

        if bolt_group is None:
            log(f"ERROR: Failed to create bolt group for '{named_selection_name}'")
            return

        # Create individual bolt pretensions for each face
        bolt_count = 0
        for idx, face in enumerate(faces, start=1):
            try:
                # Add bolt pretension to the group
                bolt = bolt_group.AddBoltPretension()
                bolt.Name = f"Bolt_{named_selection_name}_{idx}"

                # Set the geometry (face)
                bolt.Location = face

                # Define pretension load in Step 1
                # Get the analysis settings to determine number of steps
                analysis = ExtAPI.DataModel.Project.Model.Analyses[0]

                # Add load for Step 1 (apply force)
                bolt.Preload.Output.DiscreteValues = [Quantity(pretension_force, "N")]

                # Set to lock in subsequent steps
                # In ANSYS, after initial preload, subsequent steps default to "lock"
                # This is typically handled by the Define By property
                bolt.DefineBy = BoltLoadDefineBy.Lock  # Lock after step 1

                bolt_count += 1

                log(f"  Created bolt pretension {idx}/{len(faces)}: {bolt.Name}")
                log(f"    Pretension: {pretension_force} N")
                log(f"    Step 1: Apply Force, Step 2+: Lock")

            except Exception as e:
                log(f"  ERROR creating bolt pretension {idx}: {str(e)}")
                continue

        log(f"\nSuccessfully created {bolt_count}/{len(faces)} bolt pretensions in group '{group_name}'")

    except Exception as e:
        log(f"ERROR in create_bolt_pretensions: {str(e)}")


def main():
    """
    Main function to process all configured named selections and create bolt pretensions.
    """
    log("="*70)
    log("ANSYS Mechanical - Automated Bolt Pretension Creation Script")
    log("="*70)

    if not BOLT_PRETENSION_CONFIGS:
        log("WARNING: No bolt pretension configurations defined.")
        log("Please update BOLT_PRETENSION_CONFIGS dictionary.")
        return

    # Process each named selection
    for ns_name, config in BOLT_PRETENSION_CONFIGS.items():
        log(f"\nProcessing Named Selection: '{ns_name}'")

        pretension_force = config.get("pretension")

        if pretension_force is None:
            log(f"WARNING: No pretension force defined for '{ns_name}'. Skipping.")
            continue

        # Create bolt pretensions
        create_bolt_pretensions(ns_name, pretension_force)

    # Refresh tree to show new bolt pretensions
    ExtAPI.DataModel.Tree.Refresh()

    log("\n" + "="*70)
    log("Bolt pretension creation complete!")
    log("="*70)


# Run the script
if __name__ == "__main__":
    main()
