import subprocess
import time
from typing import Any

from autofmt.services.logger import log_error, log_success

last_formatted = {}


def run_formatters(filepath: str, config: dict[str, Any]) -> None:
    cooldown = config.get("cooldown_seconds", 1.0)
    now = time.time()
    if filepath in last_formatted and (now - last_formatted[filepath]) < cooldown:
        return

    time.sleep(0.5)  # Wait for file save to complete
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", filepath],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(f"\nSyntax error logsx:\n  {filepath}\n  {result.stdout.strip()}")

        if "ruff" in config["formatters"]:
            # Run fuff and capture the output
            result = subprocess.run(
                ["ruff", "check", "--fix", filepath],
                check=True,
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(f"\nRuff logs:\n  {filepath}\n  {result.stdout.strip()}")
        if "black" in config["formatters"]:
            # Run black and capture the output
            result = subprocess.run(
                ["black", filepath],
                check=True,
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(f"\nBlack logs:\n  {filepath}\n  {result.stdout.strip()}")
        last_formatted[filepath] = now
        log_success(f"\nFormatted path:\n  {filepath}")
    except subprocess.CalledProcessError:
        log_error(f"\nSyntax error logs:\n  {filepath}\n  skipping formatting.")
