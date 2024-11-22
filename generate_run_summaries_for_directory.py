import argparse
import json
import os

from main import generate_dictionary_of_run_summary


def find_subdirectories(base_path, filename, depth=None, verbose=False):
    result_dirs = []
    for root, dirs, files in os.walk(base_path):
        # Calculate the relative depth of the current directory
        relative_depth = root[len(base_path):].count(os.sep)
        if relative_depth >= depth:
            # Clear dirs to prevent os.walk from descending further
            if verbose:
                print(f"Stopping at {os.path.abspath(root)}")
            dirs[:] = []
        if filename in files:
            if verbose:
                print(f"Adding {root}")
            result_dirs.append(os.path.abspath(root))
    return result_dirs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Illumina run summary information.')
    parser.add_argument('--folder', '-f', required=True, type=str, help='Path to a folder that contains Illumina run folders.')
    parser.add_argument('--output_file_suffix', '-ofs', required=True, type=str,
                        help='A suffix to put on to json file for each output folder. You probably want an underscore or dash as the first character.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable debug mode')
    parser.add_argument('--depth', '-d', type=int, default=1, help='how far down the directory tree to stop looking. Defaults to 1 level. -1 means look forever (not recommended)')

    args = parser.parse_args()

    verbose = args.verbose

    directories_that_have_copy_complete = find_subdirectories(args.folder, "CopyComplete.txt", depth=args.depth, verbose=False)

    if verbose:
        print("\n".join(directories_that_have_copy_complete))

    count = 0
    reads_pf__percents = {}
    for d in directories_that_have_copy_complete:
        count += 1
        if verbose:
            print(f"\n\nprocessing {d}")
        run_summary = generate_dictionary_of_run_summary(d)

        output_file = os.path.basename(d) + args.output_file_suffix + ".json"

        try:
            try:
                split = os.path.basename(d).split("_")
                key_name = split[1] + "_" + split[2]  # hopefully the serial number and run number
            except IndexError:
                key_name = output_file
            reads_pf__percents[key_name] = run_summary["total_summary"]["reads_pf__percent"]
        except KeyError:
            if verbose:
                print(f"No reads_pf__percent for {d}")
            pass

        if verbose:
            print(f"writing to {output_file}")
            print(json.dumps(run_summary, indent=4, sort_keys=True))

        with open(output_file, 'w') as outfile:
            json.dump(run_summary, outfile, indent=4, sort_keys=True)

    print(f"Completed {count} runs")

    if verbose:
        print("\n".join(f"{key} : {value}" for key, value in sorted(reads_pf__percents.items())))
