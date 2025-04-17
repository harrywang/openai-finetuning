import xml.etree.ElementTree as ET
import json
import os
import sys
from collections import Counter
from datetime import datetime

def transform_xml_to_jsonl(xml_file, output_file, format_type="standard"):
    """
    Transform XML file to JSONL format with specific structure.
    
    Args:
        xml_file (str): Path to the XML file
        output_file (str): Path to the output JSONL file
        format_type (str): Type of output format - "standard" or "chat"
        
    Returns:
        tuple: (record_count, categories, polarity_counts)
    """
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Collect all unique categories from the XML
    all_categories = set()
    for sentence in root.findall('.//sentence'):
        for aspect in sentence.find('aspectCategories').findall('aspectCategory'):
            category = aspect.get('category')
            all_categories.add(category)
    
    # Initialize counters for statistics
    record_count = 0
    polarity_counts = Counter()
    category_polarity_counts = {}
    
    # Open the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Process each sentence
        for sentence in root.findall('.//sentence'):
            record_count += 1
            
            # Get the review text
            text = sentence.find('text').text
            
            # Get all aspect categories and their polarities
            aspect_categories = {}
            for aspect in sentence.find('aspectCategories').findall('aspectCategory'):
                category = aspect.get('category')
                polarity = aspect.get('polarity')
                aspect_categories[category] = polarity
                
                # Update polarity counts
                polarity_counts[polarity] += 1
                
                # Update category-specific polarity counts
                if category not in category_polarity_counts:
                    category_polarity_counts[category] = Counter()
                category_polarity_counts[category][polarity] += 1
            
            # Create output dictionary with all categories set to "unknown" by default
            output_dict = {category: "unknown" for category in all_categories}
            
            # Update with actual polarities from the review
            for category, polarity in aspect_categories.items():
                output_dict[category] = polarity
            
            if format_type == "standard":
                # Create the standard output structure
                output = {
                    "input": text,
                    "output": output_dict
                }
            elif format_type == "chat":
                # Create the chat format output structure
                # Compact JSON without newlines or indentation for assistant content
                compact_json = json.dumps(output_dict, separators=(',', ':'))
                output = {
                    "messages": [
                        {"role": "system", "content": "you are an expert data labeling assistant that always outputs json format"},
                        {"role": "user", "content": text},
                        {"role": "assistant", "content": compact_json}
                    ]
                }
            else:
                raise ValueError(f"Unknown format type: {format_type}")
            
            # Write the JSON object to the output file
            f.write(json.dumps(output) + '\n')
    
    # Count unknown polarities added during transformation
    unknown_count = 0
    for category in all_categories:
        for _ in range(record_count - sum(category_polarity_counts.get(category, {}).values())):
            unknown_count += 1
    polarity_counts["unknown"] = unknown_count
    
    return record_count, all_categories, polarity_counts, category_polarity_counts

def generate_log_content(record_count, categories, polarity_counts, category_polarity_counts):
    """
    Generate a detailed log of the transformation process.
    
    Returns:
        str: The formatted log content
    """
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_lines = []
    log_lines.append(f"===== Transformation Log ({timestamp}) =====\n")
    log_lines.append(f"Total records processed: {record_count}")
    log_lines.append(f"\nTotal unique categories ({len(categories)}): {', '.join(sorted(categories))}")
    
    log_lines.append("\nOverall polarity distribution:")
    for polarity, count in sorted(polarity_counts.items()):
        log_lines.append(f"  {polarity}: {count} ({count/sum(polarity_counts.values())*100:.1f}%)")
    
    log_lines.append("\nCategory-specific polarity distribution:")
    for category in sorted(categories):
        log_lines.append(f"\n  {category}:")
        if category in category_polarity_counts:
            total = sum(category_polarity_counts[category].values())
            for polarity, count in sorted(category_polarity_counts[category].items()):
                log_lines.append(f"    {polarity}: {count} ({count/record_count*100:.1f}% of records, {count/total*100:.1f}% of category)")
            unknown = record_count - total
            if unknown > 0:
                log_lines.append(f"    unknown: {unknown} ({unknown/record_count*100:.1f}% of records)")
        else:
            log_lines.append(f"    unknown: {record_count} (100% of records)")
    
    return "\n".join(log_lines)

def print_and_save_log(record_count, categories, polarity_counts, category_polarity_counts, log_file):
    """
    Print a detailed log of the transformation process and save it to a file.
    
    Args:
        record_count: Number of records processed
        categories: Set of unique categories
        polarity_counts: Counter of polarity occurrences
        category_polarity_counts: Dictionary of category-specific polarity counters
        log_file: Path to save the log file
    """
    log_content = generate_log_content(record_count, categories, polarity_counts, category_polarity_counts)
    
    # Print to console
    print("\n" + log_content)
    
    # Save to file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(log_content)

def process_file(input_file, format_type="standard"):
    """
    Process a single XML file and transform it to JSONL.
    
    Args:
        input_file: Path to the input XML file
        format_type: Type of output format - "standard" or "chat"
    """
    # Get current timestamp for file naming
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define output and log file paths based on input file
    base_dir = os.path.dirname(input_file)
    file_name = os.path.basename(input_file)
    file_base = os.path.splitext(file_name)[0]
    
    # Add format type to output filename if it's not standard
    if format_type == "standard":
        output_file = os.path.join(base_dir, f"{file_base}.jsonl")
    else:
        output_file = os.path.join(base_dir, f"{file_base}_{format_type}.jsonl")
        
    log_file = os.path.join(base_dir, f"transformation_log_{file_base}_{format_type}_{timestamp_str}.txt")
    
    print(f"\nProcessing {file_name} with format type '{format_type}'...")
    
    # Transform the XML file to JSONL and get statistics
    record_count, categories, polarity_counts, category_polarity_counts = transform_xml_to_jsonl(input_file, output_file, format_type)
    
    # Print the log and save it to a file
    print_and_save_log(record_count, categories, polarity_counts, category_polarity_counts, log_file)
    
    print(f"Transformation complete. Output saved to {output_file}")
    print(f"Log saved to {log_file}")

def print_usage():
    """
    Print usage information for the script.
    """
    print("Usage: python transform_to_jsonl.py <xml_file_path> [--format FORMAT]")
    print("Example: python transform_to_jsonl.py /Users/harrywang/sandbox/led/mams/MAMS-ACSA/raw/test.xml")
    print("         python transform_to_jsonl.py /Users/harrywang/sandbox/led/mams/MAMS-ACSA/raw/train.xml --format chat")
    print("\nOptions:")
    print("  --format FORMAT    Output format type (standard or chat, default: standard)")

if __name__ == "__main__":
    # Check if a file path is provided as a command line argument
    if len(sys.argv) < 2:
        print("Error: No XML file specified.")
        print_usage()
        sys.exit(1)
    
    # Get the input file path from command line arguments
    input_file = sys.argv[1]
    
    # Check for format option
    format_type = "standard"
    if "--format" in sys.argv:
        try:
            format_index = sys.argv.index("--format")
            if format_index + 1 < len(sys.argv):
                format_type = sys.argv[format_index + 1]
                if format_type not in ["standard", "chat"]:
                    print(f"Error: Invalid format type '{format_type}'. Must be 'standard' or 'chat'.")
                    print_usage()
                    sys.exit(1)
            else:
                print("Error: --format option requires a value.")
                print_usage()
                sys.exit(1)
        except ValueError:
            pass
    
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)
    
    # Check if the input file is an XML file
    if not input_file.lower().endswith('.xml'):
        print(f"Error: File '{input_file}' is not an XML file.")
        sys.exit(1)
    
    # Process the file
    process_file(input_file, format_type)
