import re
import sys
import os

# Dictionary to store macro definitions
macros = {}

# Function to remove comments from a line of code
def remove_comments(code):
    # Remove single-line comments (//)
    code = re.sub(r'//.*', '', code)
    # Remove multi-line comments (/* ... */)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code

# Function to evaluate special numerical patterns
def evaluate_numerical_pattern(number):
    base_pattern = "aqaa"
    operations = {"w": 1, "q": 5, "e": 10}
    current_value = 0
    pattern = []

    while number > 0:
        if number >= 10:
            pattern.append("e")
            number -= 10
        elif number >= 5:
            pattern.append("q")
            number -= 5
        elif number >= 1:
            pattern.append("w")
            number -= 1

    return f"<EAST {base_pattern}{''.join(pattern)}>"

# Function to process a file and simulate C Macros
def process_file(file_path, processed_files=set()):
    if file_path in processed_files:
        return []  # Prevent reprocessing the same file (to avoid infinite loops in case of circular includes)
    processed_files.add(file_path)

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    output_lines = []
    skip_block = False  # Used for conditional compilation (#ifdef, #ifndef)
    macro_name = None
    macro_value = []
    in_macro_definition = False

    for line in lines:
        # Remove comments before processing the line
        line = remove_comments(line).rstrip()

        # Handle #include
        include_match = re.match(r'#include\s+[<"]([^>"]+)[>"]', line)
        if include_match:
            include_file = include_match.group(1)
            include_file_path = include_file
            if not os.path.isabs(include_file):
                include_file_path = os.path.join(os.path.dirname(file_path), include_file)
            # Process macros from the included file, but don't add its contents to output
            process_file(include_file_path, processed_files)
            continue

        # Handle multi-line #define
        if in_macro_definition:
            if line.endswith('\\'):
                # Continue accumulating lines for the current macro definition
                macro_value.append(line[:-1].strip())  # Remove the backslash and strip whitespace
                continue
            else:
                # End of the current multi-line #define
                macro_value.append(line.strip())  # Add the last line without a backslash
                macros[macro_name] = ' '.join(macro_value).replace('\\', '').strip()
                in_macro_definition = False
                macro_name = None
                macro_value = []
                continue

        # Handle single-line #define
        define_match = re.match(r'#define\s+"([^"]+)"\s*(.*)', line)
        if define_match:
            macro_name = define_match.group(1)
            macro_value = define_match.group(2).replace('\\', '').strip()  # Ensure no backslashes
            macros[macro_name] = macro_value
            continue

        # Handle normal #define
        define_match = re.match(r"#define\s+(\w+)\s+(.*)", line)
        if define_match:
            macro_name = define_match.group(1)
            macro_value = define_match.group(2).replace('\\', '').strip()  # Ensure no backslashes
            macros[macro_name] = macro_value
            continue

        # Start of multi-line #define
        define_match = re.match(r'#define\s+(\w+)\s+(.*)\\$', line)
        if define_match:
            macro_name = define_match.group(1)
            macro_value = [define_match.group(2).strip()]  # Start with the first line (remove trailing backslash)
            in_macro_definition = True
            continue

        # Handle #undef
        undef_match = re.match(r"#undef\s+(\w+)", line)
        if undef_match:
            macro_name = undef_match.group(1)
            if macro_name in macros:
                del macros[macro_name]
            continue

        # Handle #ifdef (skip lines if macro is not defined)
        ifdef_match = re.match(r"#ifdef\s+(\w+)", line)
        if ifdef_match:
            macro_name = ifdef_match.group(1)
            skip_block = macro_name not in macros
            continue

        # Handle #ifndef (skip lines if macro is defined)
        ifndef_match = re.match(r"#ifndef\s+(\w+)", line)
        if ifndef_match:
            macro_name = ifndef_match.group(1)
            skip_block = macro_name in macros
            continue

        # Handle #endif (end of a conditional block)
        if re.match(r"#endif", line):
            skip_block = False
            continue

        # Skip lines if we're in a block that's being skipped (#ifdef/#ifndef)
        if skip_block:
            continue

        # Replace macros in the current line
        for macro_name, macro_value in sorted(macros.items(), key=lambda x: -len(x[0])):  # Sort by macro length
            # Escape any regex special characters in macro names
            escaped_macro_name = re.escape(macro_name)
            # Replace macro in the line with its value
            line = re.sub(rf'\b{escaped_macro_name}\b', macro_value, line)

        # After macros are replaced, check for numeric special case
        if line.isdigit() and int(line) < 1000:
            line = evaluate_numerical_pattern(int(line))

        output_lines.append(line)

    return output_lines

# Main execution
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cMacroSimulator.py <file_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_lines = process_file(input_file)

    # Output the processed lines to the console
    print("\n".join(output_lines).replace("\\", ""))
