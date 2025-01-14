import subprocess
import os

# 1. python file 실행 코드
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

############
# 테스트 실행
############
if __name__ == "__main__":
    # 테스트 케이스 실행
    runPythonFiles()

