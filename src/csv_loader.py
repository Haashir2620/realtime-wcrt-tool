import csv
from task import Task


def load_tasks_from_csv(path, require_deadline_le_period=False):
    tasks = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")

        cols = set(reader.fieldnames)

        # Format A: your own simple CSVs
        format_a = {"name", "C", "T", "D"}

        # Format B: course task-sets
        format_b = {"TaskID", "WCET", "Period", "Deadline"}

        if format_a.issubset(cols):
            def extract(row):
                return (
                    row["name"].strip(),
                    float(row["C"]),
                    float(row["T"]),
                    float(row["D"]),
                )

        elif format_b.issubset(cols):
            def extract(row):
                name = f"T{row['TaskID']}"
                return (
                    name,
                    float(row["WCET"]),
                    float(row["Period"]),
                    float(row["Deadline"]),
                )

        else:
            raise ValueError(
                f"Unknown CSV format. Found columns: {reader.fieldnames}"
            )

        for line_no, row in enumerate(reader, start=2):
            name, C, T, D = extract(row)

            if C <= 0 or T <= 0 or D <= 0:
                raise ValueError(f"Line {line_no} ({name}): C, T, D must be > 0")

            if C > T:
                raise ValueError(f"Line {line_no} ({name}): C must be <= T")

            if require_deadline_le_period and D > T:
                raise ValueError(f"Line {line_no} ({name}): D must be <= T")

            tasks.append(Task(name, C, T, D))

    return tasks
