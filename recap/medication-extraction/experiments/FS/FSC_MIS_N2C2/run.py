from step.exec import *
import sys


if __name__ == "__main__":
    if len(sys.argv) < 2:
        input_files = ['config_json.json', 'config_csv.json']
    else:
        input_files = sys.argv[1:]

    for input_file in input_files:
        run(input_file, True)
