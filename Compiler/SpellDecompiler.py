import re
import sys
import os

# Dictionary to store hex pattern macros (sequence -> name)
macro_patterns = {}

# Function to load macros from a file, and process includes recursively
def load_macros(file_path, processed_files=None):
    if processed_files is None:
        processed_files = set()

    # Check if the file has already been processed to avoid circular includes
    if file_path in processed_files:
        return

    # Mark the current file as processed
    processed_files.add(file_path)

    # Read the file
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    for line in lines:
        # Handle include directives: #include "filename"
        include_match = re.match(r'#include\s+"([^"]+)"', line)
        if include_match:
            include_file = include_match.group(1)
            include_file_path = os.path.join(os.path.dirname(file_path), include_file)
            load_macros(include_file_path, processed_files)

        # Match macro definitions: #define "name" <pattern>
        macro_match = re.match(r'#define\s+"([^"]+)"\s+<[^ ]+\s+([^>]+)>', line)
        if macro_match:
            macro_name = macro_match.group(1)
            macro_sequence = macro_match.group(2).strip()
            macro_patterns[macro_sequence] = macro_name

# Function to evaluate special numerical patterns
def evaluate_numerical_pattern(pattern):
    base_pattern = "aqaa"
    operations = {"w": 1, "q": 5, "e": 10}
    current_value = 0
    
    if pattern.startswith(base_pattern):
        pattern = pattern[len(base_pattern):]  # Strip the base pattern
    
        for char in pattern:
            if char in operations:
                current_value += operations[char]
            elif char == "a":
                current_value *= 2
            elif char == "d":
                current_value /= 2

    return f"<NORTH aqaa{pattern}> //Numerical Reflection: {current_value}"

# Function to process input patterns and reverse them to macro names
def reverse_hex_patterns(input_data):
    output_lines = []
    
    # Regex to match HexPattern(X Y), ignoring the direction
    hex_pattern_regex = re.compile(r'HexPattern\([^ ]+ ([^)]+)\)')
    
    for pattern in input_data:
        # Extract the sequence (e.g., qaq)
        match = hex_pattern_regex.match(pattern)
        if match:
            hex_sequence = match.group(1).strip()
            # Try to find the sequence in the macro dictionary
            if hex_sequence in macro_patterns:
                output_lines.append(macro_patterns[hex_sequence])
            else:
                # Evaluate numerical patterns
                numerical_result = evaluate_numerical_pattern(hex_sequence)
                output_lines.append(numerical_result)
        else:
            # If the pattern doesn't match HexPattern(), append it directly
            output_lines.append(f"<EAST> //{pattern}")
    
    return output_lines

# Function to process the entire file with #include directives and hex patterns
def process_input_file(file_path):
    input_patterns = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        # Handle include directives to load macros from external files
        include_match = re.match(r'#include\s+"([^"]+)"', line)
        if include_match:
            include_file = include_match.group(1)
            include_file_path = os.path.join(os.path.dirname(file_path), include_file)
            load_macros(include_file_path)
        
        # Extract HexPattern(...) list from the input file
        pattern_list_match = re.search(r'\[(.+?)\]', line)
        if pattern_list_match:
            input_patterns = pattern_list_match.group(1).split(", ")
        else:
            # Append non-HexPattern lines directly
            input_patterns.append(line.strip())
    
    # Process the extracted patterns
    reversed_output = reverse_hex_patterns(input_patterns)
    
    # Output the result
    return reversed_output

# Main function to execute the reversal process
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reverse_macro.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Process the input file and handle includes
    output_lines = process_input_file(input_file)

    # Print the results
    print("\n".join(output_lines))
