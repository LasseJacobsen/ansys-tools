"""
ANSYS Bolt Force Extraction - Postprocessing Module
====================================================

Automates the extraction of force and moment reactions from bolt faces
in ANSYS Mechanical. For each face in a named selection, it creates a local
coordinate system aligned with the bolt face (Z-axis normal to face), then
creates reaction probes to measure forces and moments in this local coordinate
system. Results are evaluated across specified time steps and exported to CSV.

This module integrates with the ANSYS Tools framework, supporting YAML
configuration and following established patterns.

Usage:
    From ANSYS Mechanical:
    - Run main.py (includes all postprocessing)
    - Or run this script directly

    From command line:
    - python main.py --extract-forces

Configuration:
    Edit config/bolt_force_extraction_config.yaml

Features:
    - Reactions measured in local coordinate system aligned with each bolt face
    - Supports single or multiple named selections
    - Smart object reuse (avoids duplicates on re-runs)
    - Proper body scoping for accurate force extraction
    - Comprehensive logging with timestamps
    - Three operational modes: run_only, cleanup_only, run_cleanup

Author:
    Lasse Jacobsen (lbj@frecon.dk)
    FRECON A/S

Based on original work by:
    Ulrik Hansen and Marcus Binder Nilsen

Version: 2.1 (Integrated into ANSYS Tools framework)
Date: November 2025
"""
# pylint: disable=undefined-variable
# pyright: reportUndefinedVariable=false
# type: ignore

import sys
import os
import csv
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.logging_config import log, log_section
from utilities.config_loader import load_yaml_config, get_config_path
from utilities.named_selection_helper import (
    get_named_selection,
    named_selection_to_list,
    normalize_named_selection_list
)
from utilities.geometry_helper import (
    create_face_aligned_coordinate_system,
    create_surface_from_coordinate_system,
    get_body_from_face,
    delete_coordinate_systems_by_pattern,
    delete_surfaces_by_pattern
)
from utilities.probe_helper import (
    create_force_reaction_probe,
    create_moment_reaction_probe,
    extract_probe_results,
    manage_probe_groups,
    delete_probes_by_pattern
)

# ============================================================================
# ANSYS IronPython Environment Globals
# ============================================================================
# The following global objects are provided by ANSYS Mechanical's IronPython
# environment at runtime. This script is designed to run ONLY within ANSYS
# Mechanical - these objects will not exist in a standard Python environment.
#
# ANSYS-provided global objects (available at runtime in ANSYS Mechanical):
# - ExtAPI: ANSYS Extension API
# - Model: ANSYS Model object  
# - Tree: ANSYS Tree API for grouping
# - Transaction: Context manager for ANSYS transactions
# - DataModelObjectCategory: Enum for ANSYS data model categories
# - SelectionTypeEnum: Enum for ANSYS selection types
# - CoordinateSystemAlignmentType: Enum for coordinate system alignment
# - CoordinateSystemAxisType: Enum for coordinate system axes
# - LocationDefinitionMethod: Enum for location definition methods
# - MomentsAtSummationPointType: Enum for moment summation types


# ============================================================================
# Embedded Configuration (Fallback)
# ============================================================================

EMBEDDED_CONFIG = {
    'csv_outfile': r'C:\data\bolt_forces.csv',
    'named_selections': ['M64_export', 'M48_export'],
    'analysis_number': 0,
    'time_steps': 'first_last',  # Options: 'first_last', 'all', or list [1, 2, 5]
    'enable_logging': True,
    'operation_mode': 'run_only'  # Options: 'run_only', 'cleanup_only', 'run_cleanup'
}


# ============================================================================
# Configuration Loading
# ============================================================================

def load_config():
    """
    Load configuration from YAML file, with fallback to embedded config.
    
    Returns:
        dict: Configuration dictionary
    """
    config_path = get_config_path('bolt_force_extraction_config.yaml')
    
    yaml_config = load_yaml_config(config_path)
    
    if yaml_config:
        log("Loaded configuration from YAML file")
        return yaml_config
    else:
        log("Using embedded configuration (YAML not available)")
        return EMBEDDED_CONFIG


# ============================================================================
# Logging Setup
# ============================================================================

def setup_file_logging(csv_filepath, enable=True):
    """
    Configure logging to write to a file in the same directory as the CSV output.
    
    Args:
        csv_filepath: Path to the CSV output file
        enable: Whether to enable file logging
        
    Returns:
        Path to the log file (or None if logging disabled)
    """
    if not enable:
        log("File logging disabled")
        return None
    
    # Create log file path
    directory = os.path.dirname(csv_filepath)
    if not directory:
        directory = '.'
        
    base_name = os.path.splitext(os.path.basename(csv_filepath))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = "{}_log_{}.txt".format(base_name, timestamp)
    log_filepath = os.path.join(directory, log_filename)
    
    # Ensure directory exists
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            log("Created output directory: {}".format(directory))
        except Exception as e:
            log("Warning: Could not create directory: {}".format(str(e)))
    
    # Remove any existing file handlers
    for handler in logging.root.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logging.root.removeHandler(handler)
    
    # Configure logging with explicit file handler
    try:
        file_handler = logging.FileHandler(log_filepath, mode='w')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', 
                                                      datefmt='%Y-%m-%d %H:%M:%S'))
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        
        # Force immediate write
        file_handler.flush()
        
        log("Logging to file: {}".format(log_filepath))
        return log_filepath
    except Exception as e:
        log("Warning: Could not create log file: {}".format(str(e)))
        return None


# ============================================================================
# Helper Functions
# ============================================================================

def get_time_steps_to_process(analysis_settings, time_steps_config):
    """
    Determine which time steps to process based on configuration.
    
    Args:
        analysis_settings: ANSYS analysis settings object
        time_steps_config: Configuration ('first_last', 'all', or list of steps)
        
    Returns:
        List of time step numbers (1-indexed)
    """
    num_steps = analysis_settings.NumberOfSteps
    
    if time_steps_config == 'first_last':
        return [1, num_steps]
    elif time_steps_config == 'all':
        return list(range(1, num_steps + 1))
    elif isinstance(time_steps_config, (list, tuple)):
        return list(time_steps_config)
    else:
        raise ValueError("Invalid time_steps configuration: {}".format(time_steps_config))


def ensure_output_directory(filepath):
    """
    Ensure the output directory exists.
    
    Args:
        filepath: Full path to the output file
        
    Raises:
        IOError: If directory cannot be created
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            log("Created output directory: {}".format(directory))
        except Exception as e:
            raise IOError("Could not create output directory: {}".format(str(e)))


def write_csv_header(writer):
    """
    Write the CSV file header.
    
    Args:
        writer: CSV writer object
    """
    writer.writerow(['Bolt Force Extraction Results - All values in project units'])
    writer.writerow(['name', 'time', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz', 'x_pos', 'y_pos', 'z_pos'])


# ============================================================================
# Cleanup Functions
# ============================================================================

def delete_probes_for_named_selection(solution, ns_name):
    """
    Delete all force and moment probes associated with a named selection.
    
    Args:
        solution: Analysis solution object
        ns_name: Named selection name to match
        
    Returns:
        Tuple of (force_count, moment_count) - number of probes deleted
    """
    force_pattern = "Force_{}_".format(ns_name)
    moment_pattern = "Moment_{}_".format(ns_name)
    
    force_count = delete_probes_by_pattern(solution, force_pattern)
    moment_count = delete_probes_by_pattern(solution, moment_pattern)
    
    return force_count, moment_count


def cleanup_named_selection(solution, ns_name):
    """
    Clean up all generated objects for a named selection.
    
    Args:
        solution: Analysis solution object
        ns_name: Named selection name
        
    Returns:
        Tuple of (force_count, moment_count, surface_count, cs_count)
    """
    log("Cleaning up objects for named selection: {}".format(ns_name))
    
    # Delete probes
    force_count, moment_count = delete_probes_for_named_selection(solution, ns_name)
    if force_count > 0 or moment_count > 0:
        log("  Deleted {} force probes and {} moment probes".format(force_count, moment_count))
    
    # Delete surfaces
    surface_pattern = "Surface_{}_".format(ns_name)
    surface_count = delete_surfaces_by_pattern(surface_pattern)
    
    # Delete coordinate systems
    cs_pattern = "CS_{}_".format(ns_name)
    cs_count = delete_coordinate_systems_by_pattern(cs_pattern)
    
    # Refresh tree
    ExtAPI.DataModel.Tree.Refresh()
    
    return force_count, moment_count, surface_count, cs_count


def cleanup_all_named_selections(solution, ns_list):
    """
    Clean up all generated objects for all named selections.
    
    Args:
        solution: Analysis solution object
        ns_list: List of named selection names
    """
    log_section("Cleaning Up Generated Objects")
    
    total_force = 0
    total_moment = 0
    total_surface = 0
    total_cs = 0
    
    for ns_name in ns_list:
        force_count, moment_count, surface_count, cs_count = cleanup_named_selection(solution, ns_name)
        total_force += force_count
        total_moment += moment_count
        total_surface += surface_count
        total_cs += cs_count
    
    log("")
    log("Cleanup Summary:")
    log("  Total force probes deleted: {}".format(total_force))
    log("  Total moment probes deleted: {}".format(total_moment))
    log("  Total surfaces deleted: {}".format(total_surface))
    log("  Total coordinate systems deleted: {}".format(total_cs))


# ============================================================================
# Main Processing Functions
# ============================================================================

def process_named_selection(ns_name, solution, analysis):
    """
    Process a single named selection: create probes for all faces.
    
    Args:
        ns_name: Name of the named selection
        solution: Analysis solution object
        analysis: Analysis object
        
    Returns:
        Tuple of (force_probes, moment_probes) lists
    """
    log("Processing named selection: {}".format(ns_name))
    
    # Find named selection using utility function
    named_sel = get_named_selection(ns_name)
    if named_sel is None:
        log("  ERROR: Named selection '{}' not found!".format(ns_name))
        return [], []
    
    # Convert to list of faces using utility function
    faces = named_selection_to_list(named_sel)
    log("  Found {} faces in named selection".format(len(faces)))
    
    if len(faces) == 0:
        log("  WARNING: No faces found in named selection!")
        return [], []
    
    force_probes = []
    moment_probes = []
    
    # Process each face
    with Transaction():
        for i, face in enumerate(faces):
            log("  Processing face {} of {}".format(i + 1, len(faces)))
            
            # Create coordinate system aligned to face using utility function
            cs_name = "CS_{}_{}".format(ns_name, i + 1)
            cs = create_face_aligned_coordinate_system(face, cs_name)
            
            # Create surface from coordinate system using utility function
            surface_name = "Surface_{}_{}".format(ns_name, i + 1)
            surface = create_surface_from_coordinate_system(cs, surface_name)
            
            # Get body that owns this face using utility function
            try:
                body_selection, body_id, body_name = get_body_from_face(face.Id)
            except ValueError as e:
                log("    ERROR: {}".format(str(e)))
                continue
            
            # Create force probe using utility function
            force_probe_name = "Force_{}_{}".format(ns_name, i + 1)
            force_probe = create_force_reaction_probe(solution, surface, cs, body_selection, force_probe_name)
            force_probes.append(force_probe)
            
            # Create moment probe using utility function
            moment_probe_name = "Moment_{}_{}".format(ns_name, i + 1)
            moment_probe = create_moment_reaction_probe(solution, surface, cs, body_selection, moment_probe_name)
            moment_probes.append(moment_probe)
    
    # Create groups for organization using utility function
    manage_probe_groups(solution, force_probes, moment_probes, ns_name)
    
    # Refresh tree to see all changes
    ExtAPI.DataModel.Tree.Refresh()
    
    log("  Created {} force probes and {} moment probes".format(len(force_probes), len(moment_probes)))
    
    return force_probes, moment_probes


def evaluate_probes_and_export(solution, analysis, all_force_probes, all_moment_probes, 
                               csv_filepath, time_steps_config):
    """
    Evaluate probes across time steps and export to CSV.
    
    Args:
        solution: Analysis solution object
        analysis: Analysis object
        all_force_probes: List of all force probes
        all_moment_probes: List of all moment probes
        csv_filepath: Path to CSV output file
        time_steps_config: Time steps configuration
    """
    log_section("Evaluating Probes and Exporting Results")
    
    # Get analysis settings
    analysis_settings = analysis.AnalysisSettings
    
    # Determine which time steps to process
    time_steps = get_time_steps_to_process(analysis_settings, time_steps_config)
    log("Processing time steps: {}".format(time_steps))
    
    # Ensure output directory exists
    ensure_output_directory(csv_filepath)
    
    # Open CSV file for writing
    with open(csv_filepath, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        write_csv_header(writer)
        
        # Process each time step
        for step in time_steps:
            log("Evaluating time step {}...".format(step))
            
            # Set current time step for all probes
            for probe in all_force_probes + all_moment_probes:
                probe.DisplayTime = Quantity("{} [sec]".format(step))
            
            # Force evaluation
            solution.EvaluateAllResults()
            
            # Extract data from each probe pair using utility function
            for force_probe, moment_probe in zip(all_force_probes, all_moment_probes):
                results = extract_probe_results(force_probe, moment_probe)
                writer.writerow([
                    results['name'], step,
                    results['fx'], results['fy'], results['fz'],
                    results['mx'], results['my'], results['mz'],
                    results['x_pos'], results['y_pos'], results['z_pos']
                ])
    
    log("Results exported to: {}".format(csv_filepath))


def main():
    """
    Main execution function.
    """
    log_section("Bolt Force Extraction - Postprocessing")
    
    # Load configuration
    config = load_config()
    
    # Extract configuration values
    csv_outfile = config.get('csv_outfile', EMBEDDED_CONFIG['csv_outfile'])
    named_selections = normalize_named_selection_list(config.get('named_selections', EMBEDDED_CONFIG['named_selections']))
    analysis_number = config.get('analysis_number', EMBEDDED_CONFIG['analysis_number'])
    time_steps = config.get('time_steps', EMBEDDED_CONFIG['time_steps'])
    enable_logging = config.get('enable_logging', EMBEDDED_CONFIG['enable_logging'])
    operation_mode = config.get('operation_mode', EMBEDDED_CONFIG['operation_mode'])
    
    # Setup file logging
    log_filepath = setup_file_logging(csv_outfile, enable_logging)
    
    # Log configuration
    log("Configuration:")
    log("  CSV Output: {}".format(csv_outfile))
    log("  Named Selections: {}".format(', '.join(named_selections)))
    log("  Analysis Number: {}".format(analysis_number))
    log("  Time Steps: {}".format(time_steps))
    log("  Operation Mode: {}".format(operation_mode))
    log("  File Logging: {}".format('Enabled' if enable_logging else 'Disabled'))
    log("")
    
    # Get analysis and solution objects
    try:
        analysis = Model.Analyses[analysis_number]
        solution = analysis.Solution
        log("Using analysis: {}".format(analysis.Name))
    except:
        log("ERROR: Could not access analysis at index {}".format(analysis_number))
        return
    
    # Execute based on operation mode
    if operation_mode == 'cleanup_only':
        cleanup_all_named_selections(solution, named_selections)
        log_section("Cleanup Complete")
        return
    
    # Run mode: Create probes and export
    all_force_probes = []
    all_moment_probes = []
    
    for ns_name in named_selections:
        force_probes, moment_probes = process_named_selection(ns_name, solution, analysis)
        all_force_probes.extend(force_probes)
        all_moment_probes.extend(moment_probes)
    
    if len(all_force_probes) == 0:
        log("ERROR: No probes were created! Check named selections.")
        return
    
    # Evaluate probes and export to CSV
    evaluate_probes_and_export(solution, analysis, all_force_probes, all_moment_probes, 
                               csv_outfile, time_steps)
    
    # Cleanup if requested
    if operation_mode == 'run_cleanup':
        log("")
        cleanup_all_named_selections(solution, named_selections)
    
    log_section("Bolt Force Extraction Complete")
    if log_filepath:
        log("Log saved to: {}".format(log_filepath))


# Execute main function when run directly
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("ERROR: {}".format(str(e)))
        import traceback
        log(traceback.format_exc())
