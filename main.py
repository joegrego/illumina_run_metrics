import json

from interop import py_interop_run_metrics, py_interop_run, py_interop_summary

if __name__ == '__main__':
    run_folder = "/Volumes/SharedHITSX/AGC-Tris/Illumina/runs/Next2kA-157/241113_VH00887_157_AAG5FJHM5/"

    run_metrics = py_interop_run_metrics.run_metrics()
    valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
    py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)
    run_folder = run_metrics.read(run_folder, valid_to_load)
    summary = py_interop_summary.run_summary()
    py_interop_summary.summarize_run_metrics(run_metrics, summary)

    # print("All of the possible values we could display for total_summary:" )
    # print(", ".join([method for method in dir(summary.total_summary()) if not method.startswith('_') and method not in ("this", "thisown", "resize")]))
    # '''
    # cluster_count
    # cluster_count_pf
    # error_rate
    # first_cycle_intensity
    # percent_aligned
    # percent_gt_q30
    # percent_occupancy_proxy
    # percent_occupied
    # projected_yield_g
    # reads
    # reads_pf
    # yield_g
    # '''

    # note that there is also a summary.nonindex_summary().*, with I think mostly the same stuff...

    total_reads = {}

    for method in dir(summary.total_summary()):
        if not method.startswith('_') and method not in ("this", "thisown", "resize") and callable(getattr(summary.total_summary(), method)):
            method = getattr(summary.total_summary(), method)
            total_reads[method.__name__] = method()

    # total_reads['cluster_count'] = summary.total_summary().cluster_count()
    # total_reads['cluster_count_pf'] = summary.total_summary().cluster_count_pf()
    # total_reads['error_rate'] = summary.total_summary().error_rate()
    # total_reads['first_cycle_intensity'] = summary.total_summary().first_cycle_intensity()
    # total_reads['percent_aligned'] = summary.total_summary().percent_aligned()
    # total_reads['percent_gt_q30'] = summary.total_summary().percent_gt_q30()
    # total_reads['percent_occupancy_proxy'] = summary.total_summary().percent_occupancy_proxy()
    # total_reads['percent_occupied'] = summary.total_summary().percent_occupied()
    # total_reads['projected_yield_g'] = summary.total_summary().projected_yield_g()
    # total_reads['reads'] = summary.total_summary().reads()
    # total_reads['reads_pf'] = summary.total_summary().reads_pf()
    # total_reads['yield_g'] = summary.total_summary().yield_g()

    total_reads['percent_reads_pf'] = (summary.total_summary().reads_pf() / summary.total_summary().reads())*100
    total_reads['percent_clusters_pf'] = (summary.total_summary().cluster_count_pf() / summary.total_summary().cluster_count())*100

    # round all floats to 2 digits becaue they can be really long
    for k, v in total_reads.items():
        if isinstance(v, float):
            total_reads[k] = round(v, 2)

    print(json.dumps(total_reads, indent=4))
