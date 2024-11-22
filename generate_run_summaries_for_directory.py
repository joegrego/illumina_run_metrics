import argparse
import os


def find_subdirectories(base_path, filename, depth=None, verbose=False):
    result_dirs = []
    for root, dirs, files in os.walk(base_path):
        # Calculate the relative depth of the current directory
        relative_depth = root[len(base_path):].count(os.sep)
        if relative_depth >= 2:
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
    parser.add_argument('--output_file_suffix', '-ofs', required=True, type=str, help='A suffix to put on to json file for each output folder.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    directories_that_have_copy_complete = find_subdirectories(args.folder, "CopyComplete.txt", depth=2)

    if args.verbose:
        print("\n".join(directories_that_have_copy_complete))
