import argparse
import json

from interop import py_interop_run_metrics, py_interop_run, py_interop_summary


def create_method_dictionary(summary_item):
    summary_dict = {}
    for attribute in dir(summary_item):
        if not attribute.startswith('_') and attribute not in ("this", "thisown", "resize") and callable(getattr(summary_item, attribute)):
            method = getattr(summary_item, attribute)
            summary_dict[method.__name__] = method()

            if method.__name__.endswith('_pf'):
                # pf is the Illumina speak for pass-filter.
                #Things with a pf number usually have a total counterpart, we can calculate a percentage
                pf_value = method()
                total_counterpart_name = method.__name__[:-len('_pf')]
                try:
                    total_counterpart = getattr(summary_item, total_counterpart_name)
                    percent_name = f"{method.__name__}__percent"  # yes, two underscores on purpose to separate ourselves from the real data
                    if percent_name not in summary_dict:
                        # don't replace a real thing!
                        summary_dict[percent_name] = (method()/total_counterpart())*100
                except AttributeError:
                    # trying and failing is OK, maybe there isn't a counterpart.
                    pass

    return summary_dict


def round_floats(the_dict, digits=2):
    new_dict = {}
    for k, v in the_dict.items():
        if isinstance(v, float):
            new_dict[k] = round(v, digits)
        else:
            new_dict[k] = v
    return new_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Illumina run summary information.')
    parser.add_argument('--run_folder', '-r',  required=True, type=str, help='Path to the Illumina run folder. usually in the form of <date>_<serial-number>_<run>_<flowcell-id>.')
    parser.add_argument('--output_file', '-o', required=True, type=str, help='Path to the output file, which will contain JSON of the run summaries.')
    parser.add_argument('--round_to', default=2, type=int, help='Round floats to this value; negative values turn off rounding')
    parser.add_argument('--verbose','-v', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    #
    # This is the magic, and it's all lifted from https://notebook.community/Illumina/interop/docs/src/Tutorial_01_Intro
    #
    run_metrics = py_interop_run_metrics.run_metrics()
    valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
    py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)
    run_folder = run_metrics.read(args.run_folder, valid_to_load)
    summary = py_interop_summary.run_summary()
    py_interop_summary.summarize_run_metrics(run_metrics, summary)

    # this gives us back a summary.total_summary() and a summary.nonindex_summary().  We will put both into the json.
    total_summary = create_method_dictionary(summary.total_summary())
    nonindex_summary = create_method_dictionary(summary.nonindex_summary())

    if args.round_to >= 0:
        total_summary = round_floats(total_summary, args.round_to)
        nonindex_summary = round_floats(nonindex_summary, args.round_to)

    everything = {'total_summary': total_summary, 'nonindex_summary': nonindex_summary}

    if args.verbose:
        print(json.dumps(everything, indent=4, sort_keys=True))

    with open(args.output_file, 'w') as outfile:
        json.dump(everything, outfile, indent=4, sort_keys=True)

