"""
ANSYS Tools - Main Entry Point
===============================

Unified entry point for all ANSYS automation scripts.
Allows running specific automation modules or all at once.

Usage:
    From ANSYS Mechanical:
    - Run this script via Tools > Scripting > Run Script File
    - Or execute specific modules directly

    From command line (for external orchestration):
    - python main.py --help
"""
# pylint: disable=undefined-variable
# pyright: reportUndefinedVariable=false
# type: ignore

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utilities.logging_config import log, log_section


def run_contact_automation():
    """Run contact automation script."""
    log_section("Running Contact Automation")
    from preprocessing import contacts
    contacts.main()


def run_bolt_pretension_automation():
    """Run bolt pretension automation script."""
    log_section("Running Bolt Pretension Automation")
    from preprocessing import bolt_pretensions
    bolt_pretensions.main()


def run_all():
    """Run all automation scripts in sequence."""
    log_section("ANSYS Tools - Running All Automation Scripts")

    log("\n=== Step 1: Contact Automation ===")
    run_contact_automation()

    log("\n=== Step 2: Bolt Pretension Automation ===")
    run_bolt_pretension_automation()

    log("")
    log_section("All automation scripts completed!")


def print_menu():
    """Print interactive menu for script selection."""
    print("\n" + "="*70)
    print("ANSYS Tools - Automation Script Menu")
    print("="*70)
    print("\n1. Run Contact Automation")
    print("2. Run Bolt Pretension Automation")
    print("3. Run All Automation Scripts")
    print("4. Exit")
    print("\n" + "="*70)


def interactive_mode():
    """Run in interactive mode with menu selection."""
    while True:
        print_menu()

        try:
            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                run_contact_automation()
            elif choice == "2":
                run_bolt_pretension_automation()
            elif choice == "3":
                run_all()
            elif choice == "4":
                print("\nExiting...")
                break
            else:
                print("\nInvalid choice. Please enter 1-4.")

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


def main():
    """
    Main entry point.

    Detects if running in ANSYS Mechanical or from command line.
    """
    # Check if running with command line arguments
    if len(sys.argv) > 1:
        import argparse

        parser = argparse.ArgumentParser(description='ANSYS Automation Tools')
        parser.add_argument('--contacts', action='store_true',
                          help='Run contact automation')
        parser.add_argument('--bolts', action='store_true',
                          help='Run bolt pretension automation')
        parser.add_argument('--all', action='store_true',
                          help='Run all automation scripts')
        parser.add_argument('--interactive', '-i', action='store_true',
                          help='Run in interactive mode with menu')

        args = parser.parse_args()

        if args.interactive:
            interactive_mode()
        elif args.contacts:
            run_contact_automation()
        elif args.bolts:
            run_bolt_pretension_automation()
        elif args.all:
            run_all()
        else:
            parser.print_help()
    else:
        # Running in ANSYS Mechanical without arguments - run all by default
        try:
            # Check if ExtAPI is available (indicates running in ANSYS)
            ExtAPI
            log("Running in ANSYS Mechanical environment")
            run_all()
        except NameError:
            # Not in ANSYS - show interactive menu
            interactive_mode()


if __name__ == "__main__":
    main()
