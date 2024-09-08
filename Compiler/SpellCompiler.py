import subprocess
import sys
import json
import re

macro_script_dir = 'Compiler/cMacroSimulator.py'

def parse_line(line):
    try:
        direction, value = line.strip().split(maxsplit=1)
        value = value[0:-1]  # Remove any trailing characters
    except:
        direction = None
        value = None
    return direction, value

def direction_to_start_dir(direction):
    direction_map = {
        "<NORTH_EAST": "0b",
        "<EAST": "1b",
        "<SOUTH_EAST": "2b",
        "<SOUTH_WEST": "3b",
        "<WEST": "4b",
        "<NORTH_WEST": "5b"
    }
    return direction_map.get(direction, "0b")

def letter_to_number(letter):
    letter_map = {
        'w': 0,
        'e': 1,
        'd': 2,
        'a': 4,
        'q': 5
    }
    return letter_map.get(letter, 0)

def convert_value(value):
    if value is not None:
        numbers = [letter_to_number(letter) for letter in value]
        return f"[B; {', '.join(f'{num}B' for num in numbers)}]"
    else:
        return f"[B;]"

def generate_command(data):
    print(data)
    # Define the pattern structure
    patterns = []
    nested_level = 0
    list_stack = []

    for dat in data:
        if dat == '[':
            # If opening a list, increase the nested level and push current patterns to the stack
            nested_level += 1
            list_stack.append(patterns)
            patterns = []
        elif dat == ']':
            # If closing a list, decrease the nested level
            nested_level -= 1
            # Create a new list pattern
            list_pattern = {
                "hexcasting:type": "hexcasting:list",
                "hexcasting:data": patterns
            }

            # Append the list to the outer patterns
            if list_stack:
                outer_patterns = list_stack.pop()
                outer_patterns.append(list_pattern)
                patterns = outer_patterns
        else:
            # Handle pattern data
            if isinstance(dat, dict) and "angles" in dat and "start_dir" in dat:
                pattern = {
                    "hexcasting:type": "hexcasting:pattern",
                    "hexcasting:data": {
                        "angles": dat["angles"],
                        "start_dir": dat["start_dir"]
                    }
                }
                patterns.append(pattern)

    # Define the final command structure
    command = {
        "hexcasting:type": "hexcasting:list",
        "hexcasting:data": patterns
    }

    # Convert the command to a JSON string
    command_json = json.dumps(command, separators=(',', ':'))

    # Remove quotes from "angles" and handle the start_dir value properly
    command_str = command_json.replace('"angles":', 'angles:').replace('"start_dir":', 'start_dir:')

    # Fix the angles value
    command_str = command_str.replace('"[', '[').replace(']"', ']')

    # Remove quotes around start_dir values using regular expression
    command_str = re.sub(r':"(\d+b)"', r':\1', command_str)

    return f"/give @p hexcasting:focus{{data: {command_str}}} 1"

def process_output(output):
    data = []
    stack = []

    for line in output:
        line = line.strip()
        
        if line == "[":
            data.append("[")  # Start a new list
        elif line == "]":
            data.append("]")  # Start a new list
        else:
            direction, value = parse_line(line)
            if direction:
                start_dir = direction_to_start_dir(direction)
                angles = convert_value(value)
                pattern = {
                    "angles": angles,
                    "start_dir": start_dir
                }
                if stack:
                    stack[-1].append(pattern)
                else:
                    data.append(pattern)
    
    return f"{generate_command(data)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        result = subprocess.run(
            ['python', macro_script_dir, file_path],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("Error occurred while running the script:")
        print(e.stderr)
        sys.exit(1)
    
    output = result.stdout.splitlines()
    command = process_output(output)
    
    print(command)

if __name__ == "__main__":
    main()
