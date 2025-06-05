#!/usr/bin/env python3
"""
Main entry point for Starbucks Survey Automation
"""

import sys
import os
import argparse
from typing import Tuple

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logging
from core.worker import excel_mode, agent_mode
from gui.main_window import create_gui

logger = setup_logging()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Starbucks Survey Automation Tool')
    parser.add_argument('--mode', choices=['gui', 'agent', 'excel'], default='gui',
                        help='Mode to run: gui (default), agent, or excel')
    parser.add_argument('--excel-file', type=str, 
                        help='Path to Excel file (required for excel mode)')
    parser.add_argument('--num-runs', type=int, default=1,
                        help='Number of survey runs (for agent mode)')
    parser.add_argument('--threads', type=int, default=1,
                        help='Number of concurrent threads')
    parser.add_argument('--submit', action='store_true',
                        help='Actually submit forms (default: test mode)')
    
    return parser.parse_args()


def run_cli_mode(args) -> Tuple[int, int]:
    """Run in command line mode"""
    if args.mode == 'agent':
        logger.info(f"Running agent mode: {args.num_runs} runs, {args.threads} threads")
        return agent_mode(
            num_runs=args.num_runs,
            num_threads=args.threads,
            submit_form=args.submit
        )
    
    elif args.mode == 'excel':
        if not args.excel_file:
            logger.error("Excel file path is required for excel mode")
            return 0, 1
        
        logger.info(f"Running excel mode: {args.excel_file}, {args.threads} threads")
        return excel_mode(
            excel_file_path=args.excel_file,
            num_threads=args.threads,
            submit_form=args.submit
        )
    
    else:
        logger.error(f"Unsupported CLI mode: {args.mode}")
        return 0, 1


def main():
    """Main function"""
    try:
        args = parse_arguments()
        
        if args.mode == 'gui':
            logger.info("Starting GUI mode")
            create_gui()
        else:
            # CLI mode
            successes, failures = run_cli_mode(args)
            
            logger.info(f"Execution completed. Successes: {successes}, Failures: {failures}")
            
            # Exit with appropriate code
            exit_code = 0 if failures == 0 else 1
            sys.exit(exit_code)
            
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()