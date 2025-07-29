import subprocess


def get_staged_files() -> list:
    """
    Get a list of staged files in the current git repository.

    Returns:
        list: A list of staged file paths.
    """
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'],
                                check=True,
                                text=True,
                                capture_output=True)
        files = result.stdout.strip().split('\n')
        return [file for file in files if file]  # Filter out empty strings
    except subprocess.CalledProcessError as e:
        print(f"Error while getting staged files: {e}")
        return []
