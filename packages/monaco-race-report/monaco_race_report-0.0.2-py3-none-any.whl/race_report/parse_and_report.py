from datetime import datetime
import os


# Constants
SEPARATOR_INDEX = 16

class Racer:
    """A data class to hold all info about a single racer"""
    def __init__(self, abbr, full_name, team, start_time, end_time):
        self.abbr = abbr
        self.full_name = full_name
        self.team = team
        self.start_time = start_time
        self.end_time = end_time
        self.lap_time = self.calculate_lap_time()

    def calculate_lap_time(self):
        """Calculates the difference between end and start time.
        If the start time is recorded as being after the end time,
        the values get swapped
        """
        if self.start_time < self.end_time:
            result = self.end_time - self.start_time
        elif self.end_time < self.start_time:
            result = self.start_time - self.end_time
        return result

    def format_lap_time(self):
        """Formats the lap time into a "M:SS.ms" string"""
        minutes, remainder_seconds = divmod(self.lap_time.total_seconds(), 60)
        seconds = int(remainder_seconds)
        milliseconds = self.lap_time.microseconds // 1000
        return f"{int(minutes)}:{seconds:02d}.{milliseconds:03d}"

def read_and_strip_lines(file_path):
    """A generator that reads a file and yields each line, stripped of
    whitespace
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                yield line.strip()
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return

def parse_log_files(file_path):
    """Parses a log files for start or end of the lap to extract the 3-letter
    racer abbreviation and the timestamp, going line by line.
    Note:
        Data in the logs is expected to be in this format: 'SVF2018-05-24_12:02:58.917'.
        Other formats will cause an error
    """
    times_data = {}
    for line in read_and_strip_lines(file_path):
        try:
            abbreviation = line[:3]
            timestamp = datetime.strptime(line[3:], "%Y-%m-%d_%H:%M:%S.%f")
            times_data[abbreviation] = timestamp
        except ValueError:
            print(f"Error: Could not parse timestamp for line: '{line}'")
    return times_data

def parse_abbreviations_file(file_path):
    """Parses the abbreviations file to get racer and team information.
    Note:
        Data in the file is expected to be in this format: 'SVF_Sebastian Vettel_FERRARI'.
        Other formats are likely cause an error
    """
    abbreviations_data = {}
    for line in read_and_strip_lines(file_path):
        try:
            abbreviation, racer_name, team_name = line.split("_")
            if not all((abbreviation, racer_name, team_name)):
                raise ValueError("One or more parts of the line are empty")
            abbreviations_data[abbreviation] = {"name": racer_name, "team": team_name}
        except ValueError:
            print(f"Warning: Skipping malformed data at line {line}")
    return abbreviations_data

def build_report(dir_name):
    """Builds a structured report of racer performance from data files"""
    start_times = parse_log_files(os.path.join(dir_name, "start.log"))
    end_times = parse_log_files(os.path.join(dir_name, "end.log"))
    racer_info = parse_abbreviations_file(os.path.join(dir_name, "abbreviations.txt"))
    report_data = []
    all_racers = set(start_times.keys()) | set(end_times.keys()) | set(racer_info.keys())
    for abbr in all_racers:
        info = racer_info.get(abbr)
        racer = Racer(
            abbr=abbr,
            full_name=info["name"],
            team=info["team"],
            start_time=start_times.get(abbr),
            end_time=end_times.get(abbr)
        )
        report_data.append(racer)
    return report_data

def print_report(report_data, order="asc"):
    """Prints a formatted race report to the console.
    The report shows each racer's place, full name, team, and lap time.
    Separates the top 15 racers from the rest with a horizontal line
    """
    reverse_order = (order == "desc")
    sorted_racers = sorted(report_data, key=lambda x: x.lap_time, reverse=reverse_order)
    print("--- F1 Monaco 2018 Race Report ---")
    for i, racer in enumerate(sorted_racers, 1):
        if i == SEPARATOR_INDEX:
            print("-" * 22 + "|" + "-" * 27 + "|" + "-" * 9)
        place = f"{i}."
        full_name = racer.full_name
        team = racer.team
        lap_time = racer.format_lap_time()
        print(f"{place:<3} {full_name:<17} | {team:<25} | {lap_time}")

def print_racer_stats(racers_by_index, report_data, racer_name):
    """Finds and prints the statistics for a single specified racer"""
    index = racers_by_index.get(racer_name)
    selected_racer = report_data[index]
    place = index + 1
    if selected_racer:
        print(f"--- Stats for {selected_racer.full_name} ---")
        print(f"Place:    {place}")
        print(f"Team:     {selected_racer.team}")
        print(f"Lap Time: {selected_racer.format_lap_time()}")
        if selected_racer.end_time < selected_racer.start_time:
            print(f"Start:    {str(selected_racer.end_time)[:-3]}")
            print(f"End:      {str(selected_racer.start_time)[:-3]}")
        else:
            print(f"Start:    {str(selected_racer.start_time)[:-3]}")
            print(f"End:      {str(selected_racer.end_time)[:-3]}")
    else:
        print(f"Racer '{racer_name}' not found in the report.")