"""
Super useful wrapper to the illumina_run_summary that will process a whole directory of stuff.

python2 generate_run_summaries_for_directory.py  -f /illumina/runs/ -op ../outputs/ -s -v
"""
import argparse
import json
import os

from main import generate_dictionary_of_run_summary


def find_subdirectories(base_path, filename, depth=None, verbose=False):
    """
    chatgpt wrote this to only search for a file down to a specific depth. For this purpose, we probably only want to go down one level,
    but your mileage may vary.

    :param base_path: where to start looking. something like /ourmount/illumina/allruns/
    :type base_path: str
    :param filename: the filename to look for. probably "CopyComplete.txt" or maybe RTAComplete.txt?
    :type filename: str
    :param depth: how far down to go. probalby 1 or maybe 2?
    :type depth: int
    :param verbose: talk to me
    :type verbose: bool
    :return: list of absolute path names that have that file (checked down to 'depth')
    :rtype: list[str]
    """
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
    parser.add_argument('--output_file_suffix', '-ofs', default="_runsummary", type=str,
                        help='A suffix to put on to json file for each output folder. You probably want an underscore or dash as the first character.')
    parser.add_argument('--output_path', '-op', type=str, default=os.getcwd(), help='Path for output files. defaults to current directory')
    parser.add_argument('--depth', '-d', type=int, default=1, help='how far down the directory tree to stop looking. Defaults to 1 level. -1 means look forever (not recommended)')
    parser.add_argument('--skip_if_output_exists', '-s', action="store_true", help='If the output json file already exists, skip it processing it.')
    parser.add_argument('--verbose', '-v', action="store_true", help='Verbose output.')

    args = parser.parse_args()
    verbose = args.verbose
    depth = args.depth if args.depth > 0 else None

    directories_that_have_copy_complete = find_subdirectories(args.folder, "CopyComplete.txt", depth=args.depth, verbose=False)
    if verbose:
        print("\n".join(directories_that_have_copy_complete))

    count = 0
    reads_pf__percents = {}
    for d in directories_that_have_copy_complete:

        output_file = os.path.join(args.output_path, os.path.basename(d) + args.output_file_suffix + ".json")
        if args.skip_if_output_exists and os.path.exists(output_file):
            if verbose:
                print(f"Skipping {d} because {output_file} already exists.")
            continue

        count += 1
        if verbose:
            print(f"\n\nprocessing {d}")
        run_summary = generate_dictionary_of_run_summary(d)

        try:
            try:
                split = os.path.basename(d).split("_")
                key_name = split[1] + "_" + split[2]  # hopefully the serial number and run number
            except IndexError:
                key_name = os.path.basename(d)
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
        # this is the stuff that the AGC is really interested in
        print("\n".join(f"{key} : {value}" for key, value in sorted(reads_pf__percents.items())))
