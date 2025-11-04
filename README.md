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

### 2. Prepare Your ANSYS Model

Create **Named Selections** in ANSYS Mechanical:
- For contacts: Select bodies that should have contacts
- For bolt pretensions: Select the pretension faces (one per bolt)
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
│   └── bolt_pretension_config.yaml
├── preprocessing/                   # Automation scripts
│   ├── contacts.py
│   └── bolt_pretensions.py
├── utilities/                       # Shared utilities
│   ├── logging_config.py
│   ├── named_selection_helper.py
│   └── config_loader.py
├── postprocessing/                  # Future: result extraction
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

### From Command Line

```bash
python main.py --all          # Run everything
python main.py --contacts     # Contacts only
python main.py --bolts        # Bolt pretensions only
python main.py --interactive  # Interactive menu
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
- Use descriptive, consistent names
- Avoid spaces and special characters

### Bolt Pretension Guidelines
- Use 60-75% of proof load for typical applications
- Group by bolt size for easy management
- Verify face normals point in correct direction

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

**4. Run `main.py` in ANSYS**

**5. Result:**
- Bonded contact for BoltedInterface
- Frictional contact (μ=0.1) for SlidingRail
- Bolt group with 4 pretensions @ 15 kN each

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

## Version

**v0.1.0** - Initial release
- Contact automation (bonded, frictional)
- Bolt pretension automation
- YAML configuration system
- Shared utility modules
- Unified entry point

---

## License

Internal tool for ANSYS automation workflows.

---

**Note**: These scripts require ANSYS Workbench Mechanical with ExtAPI access. Tested with ANSYS 2022 R2+. Some features may require 2023 R1 or later.
