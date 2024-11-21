"""

This is an example of how the UMich AGC uses the Illumina interop library to get sequencer run summary information.

"""
import argparse
import json

from interop import py_interop_run_metrics, py_interop_run, py_interop_summary


def create_method_dictionary(the_object):
    """
    Given an object, find all "callable" methods and return a dictionary with the key as the method name,
    and the value as the result of the callable function.

    I built this so that we always have everything that the interop library returns as it evolves over time.

    This will try to detect "pass filter" (_pf) items, and if there is a matching not-_pf-item, it will calculate
    the percentage with the suffix __percent. So, if there is a "read" and a "read_pf", we'll calculate a "read_pf_percent"
    and put that value in the returned dictionary.

    :param the_object: the object to find callable methods for
    :type the_object: Any
    :return: a new dictionary with the key as the method name, and the value as the result of the callable function
    :rtype: dict
    """
    summary_dict = {}
    for attribute in dir(the_object):
        if not attribute.startswith('_') and attribute not in ("this", "thisown", "resize") and callable(getattr(the_object, attribute)):
            method = getattr(the_object, attribute)
            summary_dict[method.__name__] = method()

            if method.__name__.endswith('_pf'):
                # pf is the Illumina speak for pass-filter.
                # Things with a pf number usually have a total counterpart, we can calculate a percentage
                total_counterpart_name = method.__name__[:-len('_pf')]
                try:
                    total_counterpart = getattr(the_object, total_counterpart_name)
                    percent_name = f"{method.__name__}__percent"  # yes, two underscores on purpose to separate ourselves from the real data
                    if percent_name not in summary_dict:
                        # don't replace a real thing!
                        summary_dict[percent_name] = (method() / total_counterpart()) * 100
                except AttributeError:
                    # trying and failing is OK, maybe there isn't a counterpart.
                    pass

    return summary_dict


def round_floats(the_dict, digits=2):
    """
    Given a dictionary, round each key and its value to the given number of digits. Default is 2 digits.

    :param the_dict: a dictionary with values to round
    :type the_dict: dict
    :param digits: the number of digits to round to. Default is 2.
    :type digits: int
    :return: a new dictionary with values of all floats rounded to the given number of digits
    :rtype: dict
    """
    new_dict = {}
    for k, v in the_dict.items():
        if isinstance(v, float):
            new_dict[k] = round(v, digits)
        else:
            new_dict[k] = v
    return new_dict


def get_illumina_run_summary(run_folder_path):
    """
    Given a folder path, return a summary of the illumina run.

    This is magic, and it's all lifted from https://notebook.community/Illumina/interop/docs/src/Tutorial_01_Intro

    :param run_folder_path: path to the illumina run folder
    :type run_folder_path: str
    :return: Illumina run summary (complex type, see interop docs for details)
    :rtype: Any
    """
    run_metrics = py_interop_run_metrics.run_metrics()
    valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
    py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)
    run_metrics.read(run_folder_path, valid_to_load)
    run_summary = py_interop_summary.run_summary()
    py_interop_summary.summarize_run_metrics(run_metrics, run_summary)

    return run_summary


def generate_dictionary_of_run_summary(run_folder_path, round_to_digits=2):
    """
    Given a run folder path, return a summary of an illumina run, per the interop library from illumina.

    :param run_folder_path: path to the run folder. usually in the form date_serial-number_run-id-flowcell or somesuch
    :type run_folder_path: str
    :param round_to_digits: number of digits to round floats to. Default is 2.
    :type round_to_digits: int
    :return: dictionary containing the total_summary and nonindex_summary, per the interop api from illumina
    :rtype: dict
    """

    summary = get_illumina_run_summary(run_folder_path)

    # this gives us back a summary.total_summary() and a summary.nonindex_summary(). create a dict from each.
    total_summary = create_method_dictionary(summary.total_summary())
    nonindex_summary = create_method_dictionary(summary.nonindex_summary())

    if round_to_digits >= 0:
        total_summary = round_floats(total_summary, round_to_digits)
        nonindex_summary = round_floats(nonindex_summary, round_to_digits)

    return {'total_summary': total_summary, 'nonindex_summary': nonindex_summary}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Illumina run summary information.')
    parser.add_argument('--run_folder', '-r', required=True, type=str, help='Path to the Illumina run folder. usually in the form of <date>_<serial-number>_<run>_<flowcell-id>.')
    parser.add_argument('--output_file', '-o', required=True, type=str, help='Path to the output file, which will contain JSON of the run summaries.')
    parser.add_argument('--round_to', default=2, type=int, help='Round floats to this value; negative values turn off rounding')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    the_run_summary = generate_dictionary_of_run_summary(args.run_folder, args.round_to)

    if args.verbose:
        print(json.dumps(the_run_summary, indent=4, sort_keys=True))

    with open(args.output_file, 'w') as outfile:
        json.dump(the_run_summary, outfile, indent=4, sort_keys=True)
