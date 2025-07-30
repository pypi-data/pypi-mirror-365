"""Command line interface for SpreadsheetLLM."""

import argparse
import sys
from pathlib import Path

import pandas as pd

from . import SpreadsheetLLM


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SpreadsheetLLM: Encode spreadsheets for Large Language Models"
    )

    parser.add_argument(
        "input_file",
        nargs="?",  # Make input_file optional
        help="Path to input spreadsheet file (.xlsx, .xls, or .csv)",
    )

    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")

    parser.add_argument(
        "--compression-ratio", type=float, default=None, help="Target compression ratio"
    )

    parser.add_argument(
        "--vanilla",
        action="store_true",
        help="Use vanilla encoding instead of compression",
    )

    parser.add_argument("--stats", action="store_true", help="Show encoding statistics")

    parser.add_argument("--demo", action="store_true", help="Run demo with sample data")
    
    parser.add_argument("--auto-config", action="store_true", 
                       help="Automatically configure compression parameters")
    
    parser.add_argument("--format", choices=['text', 'json'], default='text',
                       help="Output format (text or json)")
    
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Handle demo mode
    if args.demo:
        from .utils import create_realistic_spreadsheet
        import json

        print("Running SpreadsheetLLM demo...")
        df = create_realistic_spreadsheet()
        sllm = SpreadsheetLLM(enable_logging=args.verbose)

        print(f"Created demo spreadsheet: {df.shape}")
        
        # Choose encoding method based on options
        if args.vanilla:
            print("Using vanilla encoding...")
            encoded = sllm.encode_vanilla(df)
            encoding_type = "vanilla"
        elif args.auto_config:
            print("Using auto-configuration...")
            encoded = sllm.compress_with_auto_config(df)
            encoding_type = "auto-compressed"
        else:
            encoded = sllm.compress_and_encode_for_llm(df)
            encoding_type = "compressed"
        
        if args.stats:
            stats = sllm.get_encoding_stats(df)
            print(f"\nEncoding Statistics ({encoding_type}):")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")

        # Handle output format
        if args.format == "json":
            # Convert numpy types to native Python types for JSON serialization
            json_stats = {}
            if args.stats:
                for key, value in stats.items():
                    if hasattr(value, 'item'):  # numpy scalar
                        json_stats[key] = value.item()
                    elif isinstance(value, tuple):  # shape tuple
                        json_stats[key] = list(value)
                    else:
                        json_stats[key] = value
            
            output_data = {
                "encoding_type": encoding_type,
                "data_shape": list(df.shape),  # Convert to list for JSON
                "output_length": len(encoded),
                "content": encoded
            }
            
            if args.stats:
                output_data["statistics"] = json_stats
            
            formatted_output = json.dumps(output_data, indent=2)
            print(f"\nJSON Output:")
            print(formatted_output)
        else:
            # Text format (default)
            print(f"\nLLM-ready output ({encoding_type}, {len(encoded)} characters):")
            print(encoded[:500] + "..." if len(encoded) > 500 else encoded)
        
        return

    # Validate input file is provided when not in demo mode
    if not args.input_file:
        print("Error: input_file is required when not using --demo", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Validate input file
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize SpreadsheetLLM
        sllm = SpreadsheetLLM()

        # Load spreadsheet
        df = sllm.load_from_file(args.input_file)
        print(f"Loaded spreadsheet: {df.shape} ({args.input_file})", file=sys.stderr)

        # Generate encoding
        if args.vanilla:
            encoded = sllm.encode_vanilla(df)
        else:
            encoded = sllm.compress_and_encode_for_llm(df)

        # Show statistics if requested
        if args.stats:
            stats = sllm.get_encoding_stats(df)
            print("\nEncoding Statistics:", file=sys.stderr)
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}", file=sys.stderr)
                else:
                    print(f"  {key}: {value}", file=sys.stderr)
            print("", file=sys.stderr)

        # Output result
        if args.output:
            with open(args.output, "w") as f:
                f.write(encoded)
            print(f"Encoded output written to: {args.output}", file=sys.stderr)
        else:
            print(encoded)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
