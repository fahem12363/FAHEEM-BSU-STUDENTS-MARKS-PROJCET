#!/usr/bin/env python3
"""Process student assessment marks supplied in a CSV file.

Usage:
    python student_data_processor.py input_data.csv
"""

import argparse
import csv
import os
import sys
from statistics import mean


REQUIRED_FIELDS = {
    "student_id",
    "student_name",
    "assessment1",
    "assessment2",
    "assessment3",
}


def validate_mark(value, field_name, line_number):
    """Convert a mark to float and ensure it is in the range 0 to 100."""
    try:
        mark = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Line {line_number}: {field_name} must be a number; received {value!r}."
        ) from exc

    if not 0 <= mark <= 100:
        raise ValueError(
            f"Line {line_number}: {field_name} must be between 0 and 100; "
            f"received {mark}."
        )
    return mark


def classification_from_average(average):
    """Return a UK-style degree classification for an average mark."""
    if average >= 70:
        return "First"
    if average >= 60:
        return "2:1"
    if average >= 50:
        return "2:2"
    if average >= 40:
        return "Third"
    return "Fail"


def process_file(input_path):
    """Read, validate and transform student records from a CSV file."""
    processed_rows = []
    warnings = []

    with open(input_path, "r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError("The input file does not contain a header row.")

        missing_fields = REQUIRED_FIELDS.difference(reader.fieldnames)
        if missing_fields:
            raise ValueError(
                "Missing required column(s): " + ", ".join(sorted(missing_fields))
            )

        for line_number, row in enumerate(reader, start=2):
            if not any((value or "").strip() for value in row.values()):
                continue

            try:
                student_id = (row["student_id"] or "").strip()
                student_name = (row["student_name"] or "").strip()
                if not student_id or not student_name:
                    raise ValueError(
                        f"Line {line_number}: student_id and student_name are required."
                    )

                marks = [
                    validate_mark(row[field], field, line_number)
                    for field in ("assessment1", "assessment2", "assessment3")
                ]
            except ValueError as error:
                warnings.append(str(error))
                continue

            total = sum(marks)
            average = total / len(marks)
            classification = classification_from_average(average)

            processed_rows.append(
                {
                    "student_id": student_id,
                    "student_name": student_name,
                    "assessment1": f"{marks[0]:.1f}",
                    "assessment2": f"{marks[1]:.1f}",
                    "assessment3": f"{marks[2]:.1f}",
                    "total": f"{total:.1f}",
                    "average": f"{average:.2f}",
                    "classification": classification,
                    "result": "Pass" if average >= 40 else "Fail",
                }
            )

    if not processed_rows:
        raise ValueError("No valid student records were found in the input file.")
    return processed_rows, warnings


def write_output(processed_rows, output_path):
    """Write detailed calculated results to a new CSV file."""
    fieldnames = [
        "student_id",
        "student_name",
        "assessment1",
        "assessment2",
        "assessment3",
        "total",
        "average",
        "classification",
        "result",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)


def write_report(processed_rows, warnings, report_path, input_path, output_path):
    """Create a readable summary of the processing activity and class results."""
    averages = [float(row["average"]) for row in processed_rows]
    pass_count = sum(row["result"] == "Pass" for row in processed_rows)
    top_student = max(processed_rows, key=lambda row: float(row["average"]))
    lowest_student = min(processed_rows, key=lambda row: float(row["average"]))

    with open(report_path, "w", encoding="utf-8") as report:
        report.write("STUDENT MARKS DATA PROCESSING REPORT\n")
        report.write("=" * 36 + "\n")
        report.write(f"Input file: {os.path.basename(input_path)}\n")
        report.write(f"Output file: {os.path.basename(output_path)}\n")
        report.write(f"Valid records processed: {len(processed_rows)}\n")
        report.write(f"Invalid records skipped: {len(warnings)}\n")
        report.write(f"Overall class average: {mean(averages):.2f}\n")
        report.write(f"Passed: {pass_count}\n")
        report.write(f"Failed: {len(processed_rows) - pass_count}\n")
        report.write(
            f"Highest average: {top_student['student_name']} "
            f"({top_student['average']})\n"
        )
        report.write(
            f"Lowest average: {lowest_student['student_name']} "
            f"({lowest_student['average']})\n"
        )

        if warnings:
            report.write("\nVALIDATION WARNINGS\n")
            report.write("-" * 19 + "\n")
            for warning in warnings:
                report.write(f"- {warning}\n")


def parse_arguments():
    """Read the input filename and optional output paths from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", help="CSV file containing student marks")
    parser.add_argument("--output", default="processed_results.csv")
    parser.add_argument("--report", default="processing_report.txt")
    return parser.parse_args()


def main():
    """Coordinate input, processing and output; return a command-line exit code."""
    args = parse_arguments()
    input_path = os.path.abspath(args.input_file)
    input_directory = os.path.dirname(input_path)
    output_path = os.path.join(input_directory, args.output)
    report_path = os.path.join(input_directory, args.report)

    try:
        processed_rows, warnings = process_file(input_path)
        write_output(processed_rows, output_path)
        write_report(processed_rows, warnings, report_path, input_path, output_path)
    except (FileNotFoundError, PermissionError, ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Processed {len(processed_rows)} valid student record(s).")
    print(f"Results written to: {output_path}")
    print(f"Report written to: {report_path}")
    if warnings:
        print(f"Warning: {len(warnings)} invalid row(s) were skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
