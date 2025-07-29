import argparse
from . import parse_and_report


def parse_and_build_report():
    """Parses command-line arguments to determine which report to generate
    and then calls the appropriate functions from the report module.
    """
    parser = argparse.ArgumentParser(description="Generate a Formula 1 race report from log files.")
    parser.add_argument(
        "--folder",
        required=True,
        help="Path to the folder containing 'start.log', 'end.log', and 'abbreviations.txt'."
    )
    parser.add_argument(
        "--racer",
        help="Display statistics for a specific racer by their full name."
    )
    order_group = parser.add_mutually_exclusive_group()
    order_group.add_argument(
        "--asc",
        action="store_true",
        help="Sort the report in ascending order of lap time (fastest first). This is the default."
    )
    order_group.add_argument(
        "--desc",
        action="store_true",
        help="Sort the report in descending order of lap time (slowest first)."
    )
    args = parser.parse_args()
    report_data = parse_and_report.build_report(args.folder)

    if args.racer:
        report_data.sort(key=lambda racer: racer.lap_time)
        racers_by_index = {racer.full_name: index for index, racer in enumerate(report_data)}
        parse_and_report.print_racer_stats(racers_by_index, report_data, args.racer)
    else:
        order = "desc" if args.desc else "asc"
        parse_and_report.print_report(report_data, order=order)

if __name__ == "__main__":
    parse_and_build_report()