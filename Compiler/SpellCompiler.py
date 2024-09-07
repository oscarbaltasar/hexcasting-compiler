#This file will take the output of cMacroSimulator and create a give command with the spell in it

import subprocess
import sys
import json
import re

macro_script_dir = 'Compiler/cMacroSimulator.py'

def parse_line(line):
    direction, value = line.strip().split(maxsplit=1)
    value = value[0:-1]  # Remove any trailing characters
    return direction, value

def direction_to_start_dir(direction):
    # Map directions to start_dir values
    direction_map = {
        "<NORTH_EAST": "0b",
        "<EAST": "1b",
        "<SOUTH_EAST": "2b",
        "<SOUTH_WEST": "3b",
        "<WEST": "4b",
        "<NORTH_WEST": "5b"
    }
    return direction_map.get(direction, "0b")  # Default to "0b" if direction is not found

def letter_to_number(letter):
    # Map letters to numbers (assuming 'a' = 4 and 'q' = 5 as provided)
    letter_map = {
        'w': 0,
        'e': 1,
        'd': 2,
        'a': 4,
        'q': 5
    }
    return letter_map.get(letter, 0)  # Default to 0 if letter is not found

def convert_value(value):
    # Convert value string to the format [B; 5B, 4B, 5B]
    numbers = [letter_to_number(letter) for letter in value]
    return f"[B; {', '.join(f'{num}B' for num in numbers)}]"

def generate_command(data):
    # Define the pattern structure
    patterns = []
    for dat in data:
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
    
    for line in output:
        line = line.strip()
        if line:
            direction, value = parse_line(line)
            start_dir = direction_to_start_dir(direction)
            
            # Convert value to angle representation
            angles = convert_value(value)
            pattern = {
                "angles": angles,
                "start_dir": start_dir
            }
            data.append(pattern)
    
    # Generate the command from data
    command = generate_command(data)
    
    return command

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Run 'cMacroSimulator.py' and pass the file_path as an argument
        result = subprocess.run(
            ['python', macro_script_dir, file_path],
            capture_output=True,
            text=True,
            check=True  # This will raise an exception if the command returns a non-zero exit code
        )
    except subprocess.CalledProcessError as e:
        print("Error occurred while running the script:")
        print(e.stderr)  # Print any error messages from the first script
        sys.exit(1)
    
    # Process the output from the other program
    output = result.stdout.splitlines()
    command = process_output(output)
    
    print(command)

if __name__ == "__main__":
    main()
