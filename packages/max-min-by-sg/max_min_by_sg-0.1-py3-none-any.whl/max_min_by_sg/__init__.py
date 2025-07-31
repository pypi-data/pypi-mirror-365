import os
import subprocess
import platform

def run_solver():
    cpp_path = os.path.join(os.path.dirname(__file__), "solving_maxima_minima_for_2_variables.cpp")
    executable = os.path.join(os.path.dirname(__file__), "solver")

    if platform.system() == "Windows":
        executable += ".exe"

    print("Compiling C++ code...")
    try:
        subprocess.run(["g++", cpp_path, "-o", executable], check=True)
        print("Compilation successful.")
    except subprocess.CalledProcessError:
        print("❌ Compilation failed. Make sure g++ is installed.")
        return

    print("Running solver...")
    try:
        subprocess.run([executable], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error during execution.")
