import sys
import click
from .patterns import load_patterns
from .scanner import scan_file_for_secrets
from .utils import get_staged_files


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    git-shield: Advanced secret detection for git repositories.
    """
    pass


@cli.command()
@click.option('--staged', is_flag=True, help='Scan staged files for secrets')
def scan(staged):
    """
    Scan files for potential secrets.
    """
    try:
        staged_files = get_staged_files()
    except Exception as e:
        print(f"❌ Could not get staged files. Are you in a Git repo? Is Git installed?")
        sys.exit(2)

    if not staged_files:
        print("✅ No files to scan")
        sys.exit(0)

    try:
        compiled_patterns = load_patterns()
        if not compiled_patterns:
            print(f"Problem loading patterns (zero patterns found)")
            sys.exit(2)
    except Exception as e:
        print(f"Problem loading patterns: {e}")
        sys.exit(2)

    findings = []
    for file in staged_files:
        try:
            results = scan_file_for_secrets(file, compiled_patterns)
            for result in results:
                findings.append(result)

        except PermissionError as e:
            print(f"Cannot read file {file}: {e}")
            sys.exit(2)

    if findings:
        print(f"❌ Secrets detected:")
        for result in findings:
            masked = result['match'][:4] + \
                '*' * max(0, len(result['match']) - 4)
            print(
                f"Secrets found in {result['file']} at line {result['line_number']} [{result['pattern']}] -> {masked}")

        sys.exit(1)
    else:
        print(f"✅ No secrets detected. Safe to commit.")
        sys.exit(0)


if __name__ == '__main__':
    cli()
