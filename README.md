# ANSYS Tools - Automation Scripts

A collection of Python automation scripts for ANSYS Workbench Mechanical, designed to streamline repetitive tasks in FEA workflows.

## Quick Start (5 Minutes)

### 1. Configure Your Automation

**For Contact Automation** - Edit `config/contact_config.yaml`:
```yaml
global_settings:
  pinball_radius: 1.0
  log_details: true

contacts:
  MyBoltedParts:        # Replace with your named selection name
    type: bonded

  MySlidingParts:       # Replace with your named selection name
    type: frictional
    friction_coefficient: 0.15
```

**For Bolt Pretensions** - Edit `config/bolt_pretension_config.yaml`:
```yaml
global_settings:
  log_details: true

bolt_pretensions:
  M8_Bolts:            # Replace with your named selection name
    pretension: 15000  # 15 kN

  M12_Bolts:           # Replace with your named selection name
    pretension: 35000  # 35 kN
```

**For Bolt Force Extraction** - Edit `config/bolt_force_extraction_config.yaml`:
```yaml
csv_outfile: 'C:\data\bolt_forces.csv'

named_selections:
  - 'M64_export'       # Replace with your named selection names
  - 'M48_export'

time_steps: 'first_last'  # Options: 'first_last', 'all', or [1, 2, 5]
operation_mode: 'run_only'
```

### 2. Prepare Your ANSYS Model

Create **Named Selections** in ANSYS Mechanical:
- For contacts: Select bodies that should have contacts
- For bolt pretensions: Select the pretension faces (one per bolt)
- For bolt force extraction: Select bolt faces to measure reactions
- Name them to match your config files

### 3. Run the Automation

1. Open your model in ANSYS Mechanical
2. **Tools → Scripting → Run Script File**
3. Select **`main.py`**
4. Check the console output and Connections tree

Done! Your contacts and bolt pretensions are created automatically.

---

## Project Structure

```
ANSYS Tools/
├── main.py                          # Main entry point
├── config/                          # Configuration files (YAML)
│   ├── contact_config.yaml
│   ├── bolt_pretension_config.yaml
│   └── bolt_force_extraction_config.yaml
├── preprocessing/                   # Model setup automation
│   ├── contacts.py
│   └── bolt_pretensions.py
├── postprocessing/                  # Result extraction
│   └── bolt_force_extraction.py
├── utilities/                       # Shared utilities
│   ├── logging_config.py
│   ├── named_selection_helper.py
│   └── config_loader.py
├── solving/                         # Future: solver config
├── tests/                          # Future: unit tests
├── docs/                           # Research & guides
├── requirements.txt                # Python dependencies
└── Pipfile                         # Pipenv configuration
```

## Features

### Contact Automation
- **Bonded Contacts**: MPC formulation with optimal settings
- **Frictional Contacts**: Augmented Lagrange with configurable friction
- **Automatic Detection**: Pinball radius-based contact detection
- **YAML Configuration**: Centralized, version-controlled settings

### Bolt Pretension Automation
- **Multi-Bolt Support**: One pretension per face in named selection
- **Grouped Organization**: Logical grouping by bolt type
- **Load Step Control**: Force in Step 1, Lock in subsequent steps
- **Smart Recreation**: Automatically replaces existing groups

### Bolt Force Extraction
- **Local Coordinate Systems**: Aligned with each bolt face (Z-axis normal)
- **Force & Moment Reactions**: Complete 6-DOF reaction measurements
- **CSV Export**: Timestamped results in project units
- **Smart Object Reuse**: Avoids duplicates on re-runs
- **Body Scoping**: Accurate force extraction for assemblies
- **Flexible Time Steps**: First/last, all, or custom step selection
- **Operation Modes**: Run-only, cleanup-only, or run-cleanup
- **Comprehensive Logging**: Timestamped log files for troubleshooting

---

## Installation

### Prerequisites
- ANSYS Workbench Mechanical (2022 R2 or later)
- Python 3.10+ (for external tooling, optional)

### Setup

1. Download or clone this repository

2. (Optional) Install Python dependencies for external use:
   ```bash
   cd "ANSYS Tools"
   pip install -r requirements.txt
   ```

3. Edit configuration files in `config/` directory

---

## Usage

### In ANSYS Mechanical (Recommended)

**Run all automations:**
1. Tools → Scripting → Run Script File
2. Select `main.py`

**Run specific automation:**
- Run `preprocessing/contacts.py` for contacts only
- Run `preprocessing/bolt_pretensions.py` for bolts only
- Run `postprocessing/bolt_force_extraction.py` for force extraction only

### From Command Line

```bash
python main.py --all             # Run everything
python main.py --contacts        # Contacts only
python main.py --bolts           # Bolt pretensions only
python main.py --extract-forces  # Bolt force extraction only
python main.py --interactive     # Interactive menu
```

---

## Configuration Guide

### Contact Configuration

Edit `config/contact_config.yaml`:

```yaml
global_settings:
  pinball_radius: 1.0  # mm - search distance
  log_details: true

contacts:
  # Bonded contact example
  Bolted_Connection:
    type: bonded

  # Frictional contact examples
  Sliding_Parts:
    type: frictional
    friction_coefficient: 0.1  # Steel on steel (lubricated)

  Steel_Interface:
    type: frictional
    friction_coefficient: 0.2  # Steel on steel (dry)
```

**Common friction coefficients:**
- Steel on steel (dry): 0.15-0.25
- Steel on steel (lubricated): 0.05-0.10
- Aluminum on steel: 0.45-0.60
- Steel on bronze: 0.15-0.20

### Bolt Pretension Configuration

Edit `config/bolt_pretension_config.yaml`:

```yaml
global_settings:
  log_details: true

bolt_pretensions:
  M8_Bolts:
    pretension: 15000   # Newtons

  M12_Bolts:
    pretension: 35000   # Newtons

  M16_Bolts:
    pretension: 63000   # Newtons
```

**Typical bolt pretension values (60-75% proof load):**

| Bolt Size | Pretension (kN) | Pretension (N) |
|-----------|-----------------|----------------|
| M6        | 8-10            | 8,000-10,000   |
| M8        | 15-18           | 15,000-18,000  |
| M10       | 24-30           | 24,000-30,000  |
| M12       | 35-42           | 35,000-42,000  |
| M16       | 63-78           | 63,000-78,000  |
| M20       | 98-122          | 98,000-122,000 |

### Bolt Force Extraction Configuration

Edit `config/bolt_force_extraction_config.yaml`:

```yaml
# CSV output file path
csv_outfile: 'C:\data\bolt_forces.csv'

# Named selections containing bolt faces to analyze
named_selections:
  - 'M64_export'
  - 'M48_export'

# Analysis index (0-based)
analysis_number: 0

# Time steps to process
# Options: 'first_last', 'all', or list [1, 2, 5]
time_steps: 'first_last'

# Enable detailed logging to file
enable_logging: true

# Operation mode
# Options: 'run_only', 'cleanup_only', 'run_cleanup'
operation_mode: 'run_only'
```

**Time Step Options:**
- `first_last`: Only first and last steps (fastest, good for quick checks)
- `all`: All time steps (comprehensive, slower)
- `[1, 2, 5]`: Specific steps as list (custom selection)

**Operation Modes:**
- `run_only`: Create probes and export CSV (default)
- `cleanup_only`: Delete all generated objects without running
- `run_cleanup`: Run analysis, export CSV, then cleanup

**CSV Output Format:**
- Header: name, time, Fx, Fy, Fz, Mx, My, Mz, x_pos, y_pos, z_pos
- All values in project units (typically N, N·mm, mm)
- Log file created alongside CSV with timestamp

---

## Best Practices

### Contact Settings (from ANSYS research)
- **Bonded**: MPC formulation (most efficient)
- **Frictional**: Augmented Lagrange formulation
- **Behavior**: Asymmetric
- **Detection Method**: NodalProjectedNormalFromContact
- **Interface Treatment**: AdjustToTouch (eliminates initial gaps)

### Named Selection Naming
- **Contacts**: `<Component>_Interface`, `<Part>_Connections`
- **Bolts**: `M<size>_Bolts`, `<Location>_Bolts`
- **Bolt Force Extraction**: `M<size>_export`, `<Location>_BoltFaces`
- Use descriptive, consistent names
- Avoid spaces and special characters

### Bolt Pretension Guidelines
- Use 60-75% of proof load for typical applications
- Group by bolt size for easy management
- Verify face normals point in correct direction

### Bolt Force Extraction Guidelines
- Create named selections with bolt faces (not edges or vertices)
- Each face gets a local coordinate system aligned with face normal
- Ensure solution is evaluated before running extraction
- Use 'first_last' for quick checks, 'all' for complete history
- Check log files if results seem incorrect
- Use 'cleanup_only' mode to remove old probes before re-running

---

## Troubleshooting

### "Named selection not found"
- Check spelling (case-sensitive!)
- Ensure named selection exists at Model level
- Verify it contains correct geometry type

### "Could not load YAML config"
- Script falls back to embedded config automatically
- Install PyYAML: `pip install pyyaml`
- Or edit embedded config in script files

### No contacts created
- Increase pinball radius if surfaces are far apart
- Check named selections contain appropriate geometry
- Review console output for specific errors

### Import errors
- Ensure all `__init__.py` files exist
- Check file structure matches documentation
- Verify Python path includes project root

### No forces extracted / CSV file empty
- Verify solution has been evaluated (solve completed)
- Check named selections contain faces (not edges/vertices)
- Ensure analysis_number in config matches your analysis
- Review log file for specific errors
- Try 'cleanup_only' mode first, then re-run

### Probe creation fails
- Check body scoping - face must belong to a valid body
- Verify coordinate systems can be created on selected faces
- Ensure Construction Geometry section exists in model
- Review console/log output for specific error messages

---

## Example: Complete Workflow

### Scenario: Bolted Assembly with Sliding Interface

**1. Model Preparation:**
- Named selection "BoltFaces_M8" with 4 bolt faces
- Named selection "BoltedInterface" with mating surfaces
- Named selection "SlidingRail" with sliding surfaces

**2. Contact Config (`config/contact_config.yaml`):**
```yaml
global_settings:
  pinball_radius: 1.0
  log_details: true

contacts:
  BoltedInterface:
    type: bonded

  SlidingRail:
    type: frictional
    friction_coefficient: 0.1
```

**3. Bolt Config (`config/bolt_pretension_config.yaml`):**
```yaml
global_settings:
  log_details: true

bolt_pretensions:
  BoltFaces_M8:
    pretension: 15000
```

**4. Force Extraction Config (`config/bolt_force_extraction_config.yaml`):**
```yaml
csv_outfile: 'C:\data\M8_bolt_forces.csv'

named_selections:
  - 'BoltFaces_M8'

time_steps: 'all'
operation_mode: 'run_only'
```

**5. Run `main.py` in ANSYS**

**6. Result:**
- Bonded contact for BoltedInterface
- Frictional contact (μ=0.1) for SlidingRail
- Bolt group with 4 pretensions @ 15 kN each
- CSV file with force/moment reactions for all 4 bolts across all time steps
- Log file documenting the extraction process

---

## Development

### Adding New Automation

1. **Create script** in appropriate directory:
   - `preprocessing/` - Model setup
   - `postprocessing/` - Result extraction
   - `solving/` - Solver configuration

2. **Follow patterns:**
   - Import from `utilities/` for common functions
   - Support YAML configuration
   - Include fallback embedded config
   - Add pylint/pyright suppression comments

3. **Create config** file in `config/`

4. **Import in `main.py`**

### Utility Modules

**`utilities/logging_config.py`:**
- `log(message, level)` - Consistent logging
- `log_section(title)` - Section headers
- `set_logging(enabled)` - Enable/disable

**`utilities/named_selection_helper.py`:**
- `get_named_selection(name)` - Get NS by name
- `get_faces_from_named_selection(ns)` - Extract faces
- `refresh_tree()` - Update ANSYS tree

**`utilities/config_loader.py`:**
- `load_yaml_config(path)` - Load YAML
- `get_config_path(filename)` - Get config path

---

## References

- **ANSYS Best Practices**: [docs/claude_research.MD](docs/claude_research.MD)
- **ANSYS Developer Portal**: https://developer.ansys.com
- **PyAnsys Documentation**: https://docs.pyansys.com

---

## Version Control

This project uses Git for version control:
- **Branch**: `master`
- **Initial Commit**: v0.1.0 - ANSYS Tools automation framework

To track your own changes:
```bash
git add .
git commit -m "Your commit message"
```

---

## Version

**v0.2.0** - Postprocessing Integration
- Contact automation (bonded, frictional)
- Bolt pretension automation
- **Bolt force extraction (NEW)**
  - Local coordinate systems aligned with bolt faces
  - Force and moment reaction probes
  - CSV export with timestamped logging
  - Smart object reuse and cleanup modes
- YAML configuration system
- Shared utility modules
- Unified entry point

---

## License

Internal tool for ANSYS automation workflows.

---

**Note**: These scripts require ANSYS Workbench Mechanical with ExtAPI access. Tested with ANSYS 2022 R2+. Some features may require 2023 R1 or later.
