import re


def scan_line_for_secrets(line: str, compiled_patterns: dict) -> list:
    """
    Scan a single line for secrets using compiled regex patterns.

    Args:
        line (str): The line of text to scan.
        compiled_patterns (dict): A dictionary of compiled regex patterns.

    Returns:
        list: A list of found secrets in the line.
    """
    findings = []
    for pattern_name, regex in compiled_patterns.items():
        match = regex.search(line)
        if match:
            findings.append({
                "pattern": pattern_name,
                "match": match.group()
            })
    return findings


def scan_file_for_secrets(file_path: str, compiled_patterns: dict) -> list:
    """
    Scan a file line by line for secrets using compiled regex patterns.

    Args:
        file_path (str): The path to the file to scan.
        compiled_patterns (dict): A dictionary of compiled regex patterns.

    Returns:
        list: A list of findings, each containing the pattern and matched secret.
    """

    file_findings = []

    with open(file_path, 'r') as file:
        for idx, line in enumerate(file, 1):
            line_findings = scan_line_for_secrets(
                line, compiled_patterns)

            for finding in line_findings:
                file_findings.append({
                    "file": file_path,
                    "line_number": idx,
                    "pattern": finding["pattern"],
                    "match": finding["match"],
                    "code": line.strip()
                })

    return file_findings
