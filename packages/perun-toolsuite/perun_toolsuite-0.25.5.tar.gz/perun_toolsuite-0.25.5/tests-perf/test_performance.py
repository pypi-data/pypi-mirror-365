"""
Basic set of performance benchmarks for Perun

1. Handling of the profiles
  a. loading the profile from json (and converting to latest format)
  b. iterating through all of the resources
  c. converting to pandas dataframe
  d. storing the profile from json to filesystem
"""

import time
import os
import sys
import tabulate
import perun.logic.store as store
from perun.utils.common import common_kit
import perun.profile.convert as convert
import perun.utils.log as log
import perun.utils.streams as streams


RUN_SINGLE = False


def run_benchmark(benchmark_dir, performance_tests):
    """Runs the benchmark on all of the files in the given benchmark directory

    :param benchmark_dir: directory, where benchmarks are stored
    :param performance_tests: list of performance tests that should be run
    """
    possible_tests = ("load", "query", "convert", "store")
    executed_tests = performance_tests or possible_tests
    log.write("Running benchmark_dir: {}".format(log.in_color(benchmark_dir, "red")))
    results = []
    r, d = os.path.split(benchmark_dir)
    store_dir = os.path.join(r, "store-" + d)
    common_kit.touch_dir(store_dir)
    for bench in os.listdir(benchmark_dir):
        log.write(" > {}".format(log.in_color(bench, "yellow")))
        results.append(performance_test(benchmark_dir, bench, store_dir, executed_tests))
    log.write("")
    log.write("")
    headers = ["file"] + [pt for pt in possible_tests if pt in executed_tests]
    log.write(tabulate.tabulate(results, headers=headers, floatfmt=".2f"))
    with open(benchmark_dir + ".html", "w") as hh:
        hh.write(tabulate.tabulate(results, headers=headers, tablefmt="html", floatfmt=".2f"))


def performance_test(bench_dir, file, store_dir, executed_tests):
    """Runs sets of different operations over the profile stored in file

    :param bench_dir: directory, where benchmark file is stored
    :param file: file that is benchmarked
    :param store_dir:  directory, where benchmark file will be stored
    :param executed_tests: tests that should be executed
    :return: list of elapsed times in seconds
    """
    results = [file]

    before = time.time()
    profile = store.load_profile_from_file(os.path.join(bench_dir, file), True)
    elapsed = time.time() - before
    results.append(elapsed)
    log.write("Loading profile: {}".format(log.in_color("{:0.2f}s".format(elapsed), "white")))

    if "query" in executed_tests:
        before = time.time()
        _ = list(profile.all_resources())
        elapsed = time.time() - before
        results.append(elapsed)
        log.write(
            "Iterating all resources: {}".format(log.in_color("{:0.2f}s".format(elapsed), "white"))
        )

    if "convert" in executed_tests:
        before = time.time()
        _ = convert.resources_to_pandas_dataframe(profile)
        elapsed = time.time() - before
        results.append(elapsed)
        log.write(
            "Converting to dataframe: {}".format(log.in_color("{:0.2f}s".format(elapsed), "white"))
        )

    if "store" in executed_tests:
        before = time.time()
        streams.store_json(profile.serialize(), os.path.join(store_dir, file))
        elapsed = time.time() - before
        results.append(elapsed)
        log.write("Storing profile: {}".format(log.in_color("{:0.2f}s".format(elapsed), "white")))
    return results


if __name__ == "__main__":
    performance_tests = sys.argv[1:]
    start_time = time.time()
    if RUN_SINGLE:
        run_benchmark(os.path.join("tests-perf", "single-monster"), performance_tests)
    else:
        run_benchmark(os.path.join("tests-perf", "monster-profiles"), performance_tests)
    benchmark_time = time.time() - start_time
    log.write(
        "Benchmark finished in {}".format(log.in_color("{:0.2f}s".format(benchmark_time), "white"))
    )
