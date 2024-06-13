import functools
import os
import re
import sys
from os.path import join
import difflib

# Created by Jake Skidmore
# BS - Computer Science, UNH 2024

# add a regex pattern or filename(s) of anything you don't want to run in test_files/student_files
student_excludes = []
test_excludes = []

dif = difflib.Differ()

fake_file = "badfile.txt" # a fake file
working = os.getcwd() # the working dir
test_files = join(working, "test_files") # the test files dir
student_files = join(working, "student_files") # the student files dir
out_files = join(working, "out_files") # the out files dir
temp_file = join(working, "temp.txt") # a temp file

# TODO: add code to create directories if not there

def in_excludes(test_file, excludes):
    """is this file in the excludes?"""

    def search(ex):
        return re.search(ex, test_file) is not None

    tf = list(map(search, excludes))

    return functools.reduce(lambda a, b: a or b, tf)


def pass_test_to_temp(test_name):
    """pass the file name to write_to_temp()"""
    write_to_temp(test_name)


def write_to_temp(text):
    """write a filename to temp file"""
    temp = open(temp_file, "w")
    temp.write(text)
    temp.close()


def run_student_code(student_file, test_file, file_io):
    """run the student code"""

    # check if this file is not excluded
    if not (in_excludes(test_file, test_excludes) or in_excludes(student_file, student_excludes)):

        # format the names
        out_name = format_output_name(student_file)
        student_name = join(student_files, student_file)
        test_name = join(test_files, test_file)

        # if student program accepts a file, pass that to a temp file and test_name
        if file_io == "f":
            pass_test_to_temp(test_name.split("\\")[-1])
            test_name = temp_file

        # echo the test filename to the outfile

        echo_line = f"echo -------------------------------------------------- >> {out_name}"

        os.system(echo_line)
        os.system(f"echo {test_file} >> {out_name}")
        os.system(echo_line)

        ext = student_name.split(".")[1]

        # run the student's file, redirecting input from the test file and output to the out file

        lang = "python"

        if ext == "java":
            lang = ext
            os.system(f"javac {student_name}")

        os.system(f"{lang} {student_name} < {test_name} 1>> {out_name} 2>>&1")

        # if file testing i/o, remove temp file
        if file_io == "f":
            os.remove(temp_file)


def format_output_name(student_file):
    """format the output filename"""
    return join(out_files, student_file + "_OUT.txt")


def clear_output(f):
    """clear the output file f if it exists"""
    outfile = os.fsdecode(f)
    if os.path.exists(outfile):
        os.remove(outfile)


def clear_outputs():
    """delete outputs if they already exist,
       to not concatenate additional runs"""
    for f in os.scandir(out_files):
        if f.is_file():
            clear_output(f)

def make_student_path(student_file):
    return join(student_files, student_file)

def run_test(student_file, has_fake_file, file_io):
    """run test file (.txt) against student file"""

    if " " in student_file:
        new_student_file = f"{student_file.replace(" ", "")}"
        os.system(f"mv \"{make_student_path(student_file)}\" {make_student_path(new_student_file)}")
        student_file = new_student_file

    if not (in_excludes(student_file, student_excludes) or os.path.isfile(f"{make_student_path(student_file)}")):
        print(f"File '{student_file}' does not exist")
        return False

    clear_output(format_output_name(student_file))

    if has_fake_file:
        run_student_code(student_file, fake_file, file_io)

    if os.listdir(test_files):
        # actually test files
        for test_file in os.scandir(test_files):
            run_student_code(student_file, test_file.name, file_io)
        return True
    else:
        print(f"No test files in directory {test_files}")
        return False


# TODO: add Difflib.unified_diff functionality
#   https://www.javatpoint.com/difflib-module-in-python
def main():
    """main driver to prompt TA and run tests"""

    has_fake_file = False

    if len(sys.argv) < 2:
        file_io = input("Do the programs tested accept user input or a file (i or f) ")
        if file_io == 'f':
            has_fake_file = input("Test a fake file? (y or n) ") == 'y'

        batch = input("Run single or batch? (Enter s or b) ")

    else:
        file_io = sys.argv[1]
        batch = sys.argv[2]

        if len(sys.argv) > 3:
            has_fake_file = sys.argv[3] == "ff"

    if batch == 's':
        success = False
        while not success:
            student_file = input("Enter the filename to test: ")
            success = run_test(student_file, has_fake_file, file_io)

    elif batch == 'b':
        clear_outputs()
        for student_file in os.scandir(student_files):
            run_test(student_file.name, has_fake_file, file_io)


    print("Testing finished, see out_files directory")

if __name__ == "__main__":
    main()
