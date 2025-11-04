"""
ANSYS Workbench Mechanical - Automated Contact Creation
========================================================

This script automates the creation of contact regions based on named selections.
Supports both bonded and frictional contacts with customizable parameters.

Configuration is loaded from config/contact_config.yaml

Usage:
    Run this script from within ANSYS Workbench Mechanical using the scripting console
    or as an external script file.
"""
# pylint: disable=undefined-variable
# pyright: reportUndefinedVariable=false
# type: ignore
# Note: ExtAPI, ContactType, Quantity, etc. are provided by ANSYS Mechanical runtime environment

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.logging_config import log, log_section, set_logging
from utilities.named_selection_helper import get_named_selection, refresh_tree


def create_bonded_contacts(named_selection_name, named_selection, pinball_radius=1.0):
    """
    Create automatic bonded contacts between bodies in a named selection.
    Uses MPC formulation for better efficiency and robustness.

    Args:
        named_selection_name (str): Name of the named selection
        named_selection: Named selection object
        pinball_radius (float): Pinball radius in mm
    """
    log(f"\n--- Creating Bonded Contacts for '{named_selection_name}' ---")

    try:
        # Create contact region
        connections = ExtAPI.DataModel.Project.Model.Connections
        contact_region = connections.AddContactRegion()
        contact_region.Name = f"Bonded_{named_selection_name}"

        # Scope to named selection
        contact_region.SourceLocation = named_selection
        contact_region.TargetLocation = named_selection

        # Configure as bonded with MPC formulation (best practice per ANSYS docs)
        contact_region.ContactType = ContactType.Bonded
        contact_region.ContactFormulation = ContactFormulation.MPC
        contact_region.Behavior = ContactBehavior.Asymmetric
        contact_region.DetectionMethod = ContactDetectionPoint.NodalProjectedNormalFromContact

        # Set pinball radius for automatic detection
        contact_region.PinballRegion = ContactPinballType.Radius
        contact_region.PinballRadius = Quantity(pinball_radius, "mm")

        # Use automatic contact detection across all bodies
        contact_region.SearchAcross = ContactSearchAcrossType.AllBodies

        log(f"  Contact Type: Bonded")
        log(f"  Formulation: MPC")
        log(f"  Behavior: Asymmetric")
        log(f"  Pinball Radius: {pinball_radius} mm")
        log(f"Successfully created bonded contact region: {contact_region.Name}")

    except Exception as e:
        log(f"Error creating bonded contacts: {str(e)}", "ERROR")


def create_frictional_contacts(named_selection_name, named_selection, friction_coefficient=0.2, pinball_radius=1.0):
    """
    Create automatic frictional contacts between bodies in a named selection.
    Uses Augmented Lagrange formulation with proper behavior settings.

    Args:
        named_selection_name (str): Name of the named selection
        named_selection: Named selection object
        friction_coefficient (float): Coefficient of friction
        pinball_radius (float): Pinball radius in mm
    """
    log(f"\n--- Creating Frictional Contacts for '{named_selection_name}' ---")

    try:
        # Create contact region
        connections = ExtAPI.DataModel.Project.Model.Connections
        contact_region = connections.AddContactRegion()
        contact_region.Name = f"Frictional_{named_selection_name}"

        # Scope to named selection
        contact_region.SourceLocation = named_selection
        contact_region.TargetLocation = named_selection

        # Configure contact type and formulation
        contact_region.ContactType = ContactType.Frictional
        contact_region.ContactFormulation = ContactFormulation.AugmentedLagrange
        contact_region.Behavior = ContactBehavior.Asymmetric
        contact_region.DetectionMethod = ContactDetectionPoint.NodalProjectedNormalFromContact

        # Friction coefficients (static and dynamic)
        contact_region.FrictionCoefficient = friction_coefficient
        contact_region.DynamicCoefficient = friction_coefficient

        # Set pinball radius for contact detection
        contact_region.PinballRegion = ContactPinballType.Radius
        contact_region.PinballRadius = Quantity(pinball_radius, "mm")

        # Update stiffness each iteration (best for nonlinear)
        contact_region.UpdateStiffness = UpdateContactStiffness.EachIteration

        # Interface treatment: Adjust to Touch (eliminates initial gaps)
        contact_region.InterfaceTreatment = ContactInterfaceTreatmentType.AdjustToTouch

        # Use automatic contact detection across all bodies
        contact_region.SearchAcross = ContactSearchAcrossType.AllBodies

        log(f"  Contact Type: Frictional")
        log(f"  Friction Coefficient (Static): {friction_coefficient}")
        log(f"  Friction Coefficient (Dynamic): {friction_coefficient}")
        log(f"  Formulation: Augmented Lagrange")
        log(f"  Behavior: Asymmetric")
        log(f"  Detection Method: Nodal Projected Normal From Contact")
        log(f"  Update Stiffness: Each Iteration")
        log(f"  Interface Treatment: Adjust to Touch")
        log(f"  Pinball Radius: {pinball_radius} mm")
        log(f"Successfully created frictional contact region: {contact_region.Name}")

    except Exception as e:
        log(f"Error creating frictional contacts: {str(e)}", "ERROR")


def run_from_config(config):
    """
    Run contact automation based on configuration dictionary.

    Args:
        config (dict): Configuration dictionary with contacts and settings
    """
    # Get global settings
    global_settings = config.get('global_settings', {})
    pinball_radius = global_settings.get('pinball_radius', 1.0)
    log_enabled = global_settings.get('log_details', True)
    set_logging(log_enabled)

    log_section("ANSYS Mechanical - Automated Contact Creation Script")
    log(f"Pinball Radius: {pinball_radius} mm\n")

    # Get contact definitions
    contacts = config.get('contacts', {})

    if not contacts:
        log("No contact configurations defined in config file.", "WARNING")
        return

    # Process each named selection
    for ns_name, contact_config in contacts.items():
        log(f"\nProcessing Named Selection: '{ns_name}'")

        # Get named selection object
        named_selection = get_named_selection(ns_name)

        if not named_selection:
            continue

        # Create contacts based on type
        contact_type = contact_config.get("type", "bonded").lower()

        if contact_type == "bonded":
            create_bonded_contacts(ns_name, named_selection, pinball_radius)

        elif contact_type == "frictional":
            friction_coef = contact_config.get("friction_coefficient", 0.2)
            create_frictional_contacts(ns_name, named_selection, friction_coef, pinball_radius)

        else:
            log(f"Unknown contact type '{contact_type}' for '{ns_name}'", "WARNING")

    # Refresh tree to show new contacts
    refresh_tree()

    log("")
    log_section("Contact creation complete!")


def main():
    """
    Main function to load configuration and create contacts.

    Attempts to load from YAML config. If running in ANSYS without YAML support,
    falls back to embedded configuration.
    """
    try:
        # Try to load from YAML config file
        from utilities.config_loader import load_yaml_config, get_config_path

        config_path = get_config_path('contact_config.yaml')
        config = load_yaml_config(config_path)
        log(f"Loaded configuration from: {config_path}")

    except (ImportError, FileNotFoundError) as e:
        # Fallback: Use embedded configuration if YAML loading fails
        log(f"Could not load YAML config: {str(e)}", "WARNING")
        log("Using embedded configuration")

        config = {
            'global_settings': {
                'pinball_radius': 1.0,
                'log_details': True
            },
            'contacts': {
                # Add your configurations here if running without YAML support
                # "NamedSelection1": {"type": "bonded"},
                # "NamedSelection2": {"type": "frictional", "friction_coefficient": 0.2},
            }
        }

    run_from_config(config)


# Run the script
if __name__ == "__main__":
    main()
