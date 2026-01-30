#!/usr/bin/env python3

"""
Analyze ALB access logs to generate request count and latency reports.
"""

import argparse
import csv
from collections import defaultdict

# Static file extensions to exclude from analysis
STATIC_EXTENSIONS = {
    '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.mp4', '.webm', '.mp3', '.wav', '.woff', '.woff2', '.ttf', '.eot',
    '.css', '.map'
}


def extract_uri_prefix(request_uri: str) -> str:
    """Extract URI path without query parameters."""
    if not request_uri:
        return ""
    # Split on ? to remove query parameters
    return request_uri.split('?')[0]


def should_exclude_uri(uri: str) -> bool:
    """Check if URI should be excluded from analysis."""
    return (uri.startswith('/assets/') or
            uri.startswith('/static/') or
            any(uri.endswith(ext) for ext in STATIC_EXTENSIONS))


def analyze_logs(input_file: str) -> tuple[list, list]:
    """
    Analyze the log file and generate request count and latency reports.

    Returns:
        tuple: (request_count_report, max_latency_report)
    """
    request_counts = defaultdict(int)
    max_latencies = defaultdict(float)

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            request_uri = row.get('request_uri', '')
            upstream_response_time = row.get('upstream_response_time', '')

            # Extract URI prefix
            uri_prefix = extract_uri_prefix(request_uri)

            # Skip excluded URIs
            if should_exclude_uri(uri_prefix):
                continue

            # Count requests
            request_counts[uri_prefix] += 1

            # Track max latency (parse float, ignore empty/invalid values)
            if upstream_response_time:
                try:
                    latency = float(upstream_response_time)
                    if latency > max_latencies[uri_prefix]:
                        max_latencies[uri_prefix] = latency
                except ValueError:
                    pass

    # Generate request count report (sorted by count descending)
    request_count_report = [
        {'request_uri': uri, 'request_count': count}
        for uri, count in sorted(request_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    # Generate max latency report (sorted by latency descending)
    max_latency_report = [
        {'request_uri': uri, 'max_latency_ms': max_latency * 1000}
        for uri, max_latency in sorted(max_latencies.items(), key=lambda x: x[1], reverse=True)
    ]

    return request_count_report, max_latency_report


def write_csv_report(report: list, output_file: str):
    """Write report data to CSV file."""
    if not report:
        print(f"No data to write to {output_file}")
        return

    fieldnames = report[0].keys()

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report)

    print(f"Report written to: {output_file}")
    print(f"Total records: {len(report)}")


def main():
    parser = argparse.ArgumentParser(description='Analyze ALB access logs to generate request count and latency reports')
    parser.add_argument('input_file', help='Path to the input CSV log file')
    args = parser.parse_args()

    input_file = args.input_file

    print(f"Analyzing log file: {input_file}")
    request_count_report, max_latency_report = analyze_logs(input_file)

    print(f"\n=== Request Count Report ===")
    write_csv_report(request_count_report, 'request_count_report.csv')

    print(f"\n=== Max Latency Report ===")
    write_csv_report(max_latency_report, 'max_latency_report.csv')


if __name__ == '__main__':
    main()