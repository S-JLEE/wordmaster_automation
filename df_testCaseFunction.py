import os
import subprocess


# python file 실행 코드
def runPythonFiles():
    # Get the current directory
    current_directory = os.getcwd()

    # Path to the tests directory
    tests_directory = os.path.join(current_directory, 'tests')

    # List all .py files in the tests directory
    test_files = sorted([file for file in os.listdir(tests_directory) if file.endswith('.py')])

    for test_file in test_files:
        try:
            # Construct the full path to the test file
            test_file_path = os.path.join(tests_directory, test_file)

            # Run the test file using the command: python -m unittest test_file -v
            subprocess.run(["python", "-m", "unittest", test_file_path, "-v"])
            print(f"{test_file} executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {test_file}: {e}")


# TESTCASE 실행 목록 생성 함수
def find_tc_python_files(folder_path):
    python_files = []

    # Ensure the provided path is a directory
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        return python_files

    # Iterate through the files in the directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if the file is a Python file
        if os.path.isfile(file_path) and filename.endswith('.py'):
            python_files.append(filename)  # Append only the filename, not the full path

    return python_files