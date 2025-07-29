"""
Command-line interface for ML Sniff.

This module provides CLI functionality to analyze CSV files
and generate ML problem detection reports with advanced features.
"""

import argparse
import sys
from pathlib import Path
from .sniffer import Sniffer


def main():
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="ML Sniff - Advanced Machine Learning Problem Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ml-sniff data.csv                                    # Analyze a CSV file
  ml-sniff data.csv --visualize                       # Analyze and show visualizations
  ml-sniff data.csv --interactive                     # Create interactive dashboard
  ml-sniff data.csv --output report.txt               # Save report to file
  ml-sniff data.csv --export report.json --format json # Export detailed report
  ml-sniff data.csv --target target_column            # Specify target column manually
  ml-sniff data.csv --preprocessing                   # Show preprocessing suggestions
        """
    )
    
    parser.add_argument(
        'file',
        type=str,
        help='Path to the CSV file to analyze'
    )
    
    parser.add_argument(
        '--target', '-t',
        type=str,
        help='Manually specify target column name'
    )
    
    parser.add_argument(
        '--visualize', '-v',
        action='store_true',
        help='Show data visualizations'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Create interactive Plotly dashboard'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Save report to file instead of printing to console'
    )
    
    parser.add_argument(
        '--export', '-e',
        type=str,
        help='Export detailed analysis report to file'
    )
    
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['json', 'csv', 'txt'],
        default='json',
        help='Export format (default: json)'
    )
    
    parser.add_argument(
        '--summary', '-s',
        action='store_true',
        help='Show only summary information'
    )
    
    parser.add_argument(
        '--preprocessing', '-p',
        action='store_true',
        help='Show preprocessing suggestions'
    )
    
    parser.add_argument(
        '--no-auto-analyze',
        action='store_true',
        help='Skip automatic analysis on initialization'
    )
    
    parser.add_argument(
        '--feature-importance',
        action='store_true',
        help='Show feature importance analysis'
    )
    
    parser.add_argument(
        '--data-quality',
        action='store_true',
        help='Show detailed data quality report'
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    
    if not file_path.suffix.lower() == '.csv':
        print(f"Warning: File '{args.file}' doesn't have a .csv extension.")
    
    try:
        # Create sniffer instance
        auto_analyze = not args.no_auto_analyze
        sniffer = Sniffer(args.file, target_column=args.target, auto_analyze=auto_analyze)
        
        # Handle export
        if args.export:
            sniffer.export_report(args.export, args.format)
            return
        
        # Handle output
        if args.output:
            # Redirect stdout to file
            with open(args.output, 'w') as f:
                import contextlib
                with contextlib.redirect_stdout(f):
                    if args.summary:
                        summary = sniffer.get_summary()
                        print("ML SNIFF SUMMARY")
                        print("=" * 40)
                        print(f"Target Column: {summary['target_column']}")
                        print(f"Problem Type: {summary['problem_type']}")
                        print(f"Suggested Model: {summary['suggested_model']['name']}")
                        print(f"Rows: {summary['basic_stats']['rows']:,}")
                        print(f"Columns: {summary['basic_stats']['columns']}")
                    else:
                        sniffer.report()
            print(f"Report saved to: {args.output}")
        else:
            # Print to console
            if args.summary:
                summary = sniffer.get_summary()
                print("ML SNIFF SUMMARY")
                print("=" * 40)
                print(f"Target Column: {summary['target_column']}")
                print(f"Problem Type: {summary['problem_type']}")
                print(f"Suggested Model: {summary['suggested_model']['name']}")
                print(f"Rows: {summary['basic_stats']['rows']:,}")
                print(f"Columns: {summary['basic_stats']['columns']}")
            else:
                sniffer.report()
        
        # Show preprocessing suggestions
        if args.preprocessing:
            print("\n" + "=" * 50)
            print("PREPROCESSING SUGGESTIONS")
            print("=" * 50)
            suggestions = sniffer.suggest_preprocessing()
            for category, items in suggestions.items():
                if items:
                    print(f"\n{category.replace('_', ' ').title()}:")
                    for item in items:
                        print(f"  • {item}")
                else:
                    print(f"\n{category.replace('_', ' ').title()}: No suggestions")
        
        # Show feature importance
        if args.feature_importance:
            print("\n" + "=" * 50)
            print("FEATURE IMPORTANCE ANALYSIS")
            print("=" * 50)
            if sniffer.feature_importance:
                for method in ['random_forest', 'mutual_info', 'correlation']:
                    importance = sniffer.get_feature_importance(method)
                    if importance:
                        print(f"\n{method.replace('_', ' ').title()}:")
                        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
                        for feature, score in sorted_features[:5]:
                            print(f"  • {feature}: {score:.4f}")
            else:
                print("No feature importance analysis available.")
        
        # Show data quality report
        if args.data_quality:
            print("\n" + "=" * 50)
            print("DETAILED DATA QUALITY REPORT")
            print("=" * 50)
            for col, metrics in sniffer.data_quality_report.items():
                print(f"\n{col}:")
                print(f"  • Missing: {metrics['missing_count']} ({metrics['missing_percentage']:.1f}%)")
                print(f"  • Unique: {metrics['unique_count']} ({metrics['unique_percentage']:.1f}%)")
                print(f"  • Duplicates: {metrics['duplicate_count']} ({metrics['duplicate_percentage']:.1f}%)")
                
                if 'outlier_count' in metrics:
                    print(f"  • Outliers: {metrics['outlier_count']}")
        
        # Show visualizations
        if args.visualize:
            sniffer.visualize_data()
        
        # Show interactive dashboard
        if args.interactive:
            sniffer.create_interactive_dashboard()
            
    except Exception as e:
        print(f"Error analyzing file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 