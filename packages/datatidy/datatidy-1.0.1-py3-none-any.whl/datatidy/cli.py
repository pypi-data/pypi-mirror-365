"""Command-line interface for DataTidy."""

import argparse
import sys
from pathlib import Path
from .core import DataTidy


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DataTidy: Configuration-driven data processing and cleaning"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process data using configuration')
    process_parser.add_argument('config', help='Path to YAML configuration file')
    process_parser.add_argument('-i', '--input', help='Input data file (overrides config)')
    process_parser.add_argument('-o', '--output', help='Output file path')
    process_parser.add_argument('--ignore-errors', action='store_true', 
                               help='Continue processing despite validation errors')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration file')
    validate_parser.add_argument('config', help='Path to YAML configuration file')
    
    # Sample command
    sample_parser = subparsers.add_parser('sample', help='Create sample configuration file')
    sample_parser.add_argument('output', help='Output path for sample configuration')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        process_command(args)
    elif args.command == 'validate':
        validate_command(args)
    elif args.command == 'sample':
        sample_command(args)
    elif args.command == 'version':
        version_command()
    else:
        parser.print_help()


def process_command(args: argparse.Namespace) -> None:
    """Handle process command."""
    try:
        # Initialize DataTidy
        datatidy = DataTidy()
        
        # Load configuration
        print(f"Loading configuration from: {args.config}")
        datatidy.load_config(args.config)
        
        # Override ignore_errors if specified
        if args.ignore_errors and datatidy.config:
            datatidy.config["global_settings"]["ignore_errors"] = True
        
        # Process data
        input_data = args.input if args.input else None
        print("Processing data...")
        
        if args.output:
            # Process and save
            datatidy.process_and_save(args.output, input_data)
            print(f"Processed data saved to: {args.output}")
        else:
            # Process and display
            result = datatidy.process_data(input_data)
            print("Processed data:")
            print(result.to_string())
        
        # Show errors if any
        if datatidy.has_errors():
            print("\nValidation errors encountered:")
            for error in datatidy.get_errors():
                print(f"  - {error['message']}")
        
        print("Processing completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def validate_command(args: argparse.Namespace) -> None:
    """Handle validate command."""
    try:
        datatidy = DataTidy()
        datatidy.load_config(args.config)
        
        if datatidy.validate_config():
            print(f"Configuration '{args.config}' is valid!")
        else:
            print(f"Configuration '{args.config}' is invalid!", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"Validation error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def sample_command(args: argparse.Namespace) -> None:
    """Handle sample command."""
    try:
        output_path = Path(args.output)
        
        # Check if file already exists
        if output_path.exists():
            response = input(f"File '{args.output}' already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return
        
        # Create sample configuration
        DataTidy.create_sample_config(args.output)
        print(f"Sample configuration created at: {args.output}")
        
    except Exception as e:
        print(f"Error creating sample: {str(e)}", file=sys.stderr)
        sys.exit(1)


def version_command() -> None:
    """Handle version command."""
    from . import __version__
    print(f"DataTidy version {__version__}")


if __name__ == '__main__':
    main()