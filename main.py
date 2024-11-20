import json

from interop import py_interop_run_metrics, py_interop_run, py_interop_summary


def create_method_dictionary(summary_item):
    summary_dict = {}
    for method in dir(summary_item):
        if not method.startswith('_') and method not in ("this", "thisown", "resize") and callable(getattr(summary_item, method)):
            method = getattr(summary_item, method)
            summary_dict[method.__name__] = method()
    return summary_dict


def round_floats(the_dict):
    new_dict = {}
    for k, v in the_dict.items():
        if isinstance(v, float):
            new_dict[k] = round(v, 2)
    return new_dict


if __name__ == '__main__':
    run_folder = "/Volumes/SharedHITSX/AGC-Tris/Illumina/runs/Next2kA-157/241113_VH00887_157_AAG5FJHM5/"

    run_metrics = py_interop_run_metrics.run_metrics()
    valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
    py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)
    run_folder = run_metrics.read(run_folder, valid_to_load)
    summary = py_interop_summary.run_summary()
    py_interop_summary.summarize_run_metrics(run_metrics, summary)

    # print("All the possible values we could display for total_summary:" )
    # print(", ".join([method for method in dir(summary.total_summary()) if not method.startswith('_') and method not in ("this", "thisown", "resize")]))

    # note that there is also a summary.nonindex_summary().*, with I think mostly the same stuff...

    total_summary = create_method_dictionary(summary.total_summary())
    total_summary['percent_reads_pf'] = (summary.total_summary().reads_pf() / summary.total_summary().reads()) * 100
    total_summary['percent_clusters_pf'] = (summary.total_summary().cluster_count_pf() / summary.total_summary().cluster_count()) * 100

    nonindex_summary = create_method_dictionary(summary.nonindex_summary())
    nonindex_summary['percent_reads_pf'] = (summary.nonindex_summary().reads_pf() / summary.nonindex_summary().reads()) * 100
    nonindex_summary['percent_clusters_pf'] = (summary.nonindex_summary().cluster_count_pf() / summary.nonindex_summary().cluster_count()) * 100

    # round all floats to 2 digits because they can be really long
    total_summary = round_floats(total_summary)
    nonindex_summary = round_floats(nonindex_summary)

    big_summary = {'total_summary': total_summary, 'nonindex_summary': nonindex_summary}

    print(json.dumps(big_summary, indent=4))
