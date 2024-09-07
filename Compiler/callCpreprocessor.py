import subprocess
import sys
import os

def run_preprocessor(input_file):
    # Ensure the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        return

    # Path to the Visual Studio developer command prompt batch file
    vs_dev_cmd_path = r'"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\Tools\VsDevCmd.bat"'
    
    # Path to cl.exe (you might need to adjust this based on your installation)
    cl_path = r'"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.26.28801\bin\Hostx64\x64\cl.exe"'

    # Output file name based on the input file
    output_file = input_file + ".i"

    # Command to preprocess the file
    command = [
        vs_dev_cmd_path,
        "&&",
        cl_path,
        "/E",  # Preprocess only
        "/P",  # Output preprocessed file
        f"/Fi{output_file}",  # Output file
        input_file
    ]

    # Run the command
    try:
        subprocess.run(" ".join(command), shell=True, check=True)
        print(f"Preprocessed file saved as '{output_file}'.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python preprocess.py <input_file>")
    else:
        input_file = sys.argv[1]
        run_preprocessor(input_file)

