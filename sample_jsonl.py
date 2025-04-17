#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to randomly sample a subset from a JSONL file.
Takes command line arguments for input file, output file, and sample size.
"""

import json
import random
import sys
import os
import argparse
from datetime import datetime


def sample_jsonl(input_file, output_file, sample_size, seed=None):
    """
    Randomly sample a subset from a JSONL file.
    
    Args:
        input_file (str): Path to the input JSONL file
        output_file (str): Path to the output JSONL file
        sample_size (int): Number of samples to extract
        seed (int, optional): Random seed for reproducibility
    
    Returns:
        int: Number of samples extracted
    """
    # Set random seed if provided
    if seed is not None:
        random.seed(seed)
    
    # Read all lines from the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check if sample size is valid
    total_lines = len(lines)
    if sample_size > total_lines:
        print(f"Warning: Requested sample size ({sample_size}) is larger than the total number of lines ({total_lines}).")
        print(f"Using all available lines instead.")
        sample_size = total_lines
    
    # Randomly sample lines
    sampled_lines = random.sample(lines, sample_size)
    
    # Write sampled lines to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(sampled_lines)
    
    return sample_size


def generate_log(input_file, output_file, sample_size, actual_samples, seed=None):
    """
    Generate a log file with information about the sampling process.
    
    Args:
        input_file (str): Path to the input JSONL file
        output_file (str): Path to the output JSONL file
        sample_size (int): Requested number of samples
        actual_samples (int): Actual number of samples extracted
        seed (int, optional): Random seed used for sampling
    """
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create log file path
    log_dir = os.path.dirname(output_file)
    log_file = os.path.join(log_dir, f"sampling_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # Generate log content
    log_content = [
        f"===== Sampling Log ({timestamp}) =====\n",
        f"Input file: {input_file}",
        f"Output file: {output_file}",
        f"Requested sample size: {sample_size}",
        f"Actual samples extracted: {actual_samples}",
    ]
    
    if seed is not None:
        log_content.append(f"Random seed: {seed}")
    
    # Write log to file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_content))
    
    return log_file


def main():
    """Main function to parse arguments and run the sampling."""
    # Create argument parser
    parser = argparse.ArgumentParser(description='Randomly sample a subset from a JSONL file.')
    parser.add_argument('input_file', help='Path to the input JSONL file')
    parser.add_argument('output_file', help='Path to the output JSONL file')
    parser.add_argument('sample_size', type=int, help='Number of samples to extract')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Check if input file is a JSONL file
    if not args.input_file.lower().endswith('.jsonl'):
        print(f"Warning: Input file '{args.input_file}' does not have a .jsonl extension.")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\nSampling from {os.path.basename(args.input_file)}...")
    
    # Sample from the JSONL file
    actual_samples = sample_jsonl(args.input_file, args.output_file, args.sample_size, args.seed)
    
    # Generate log file
    log_file = generate_log(args.input_file, args.output_file, args.sample_size, actual_samples, args.seed)
    
    print(f"Sampling complete. {actual_samples} samples saved to {args.output_file}")
    print(f"Log saved to {log_file}")


if __name__ == "__main__":
    main()
