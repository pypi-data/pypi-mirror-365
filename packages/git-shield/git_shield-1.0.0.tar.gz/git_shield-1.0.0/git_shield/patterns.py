import re

patterns = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "Private Key": r"-----BEGIN PRIVATE KEY-----",
    "Password": r"password\s*=\s*['\"].+?['\"]",
    "API Key": r"api_key\s*=\s*['\"].+?['\"]",
    "GitHub Token": r"gh[0-9a-z]{36}",
    "Public Key": r"-----BEGIN PUBLIC KEY-----",
    "JWT Token": r"eyJ[a-zA-Z0-9_-]+.[a-zA-Z0-9_-]+.[a-zA-Z0-9_-]+",
}


def load_patterns() -> dict:
    """
    Load patterns from a predefined dictionary.

    Returns:
        dict: A dictionary containing various patterns.
    """
    compiled_patterns = {}
    for pattern_name, regex in patterns.items():
        compiled_regex = re.compile(regex, re.IGNORECASE)
        compiled_patterns[pattern_name] = compiled_regex
    return compiled_patterns
