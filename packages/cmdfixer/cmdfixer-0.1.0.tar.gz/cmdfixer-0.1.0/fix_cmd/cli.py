import sys
from .rules import suggest_correction

def main() -> None:
    """
    Entry point for the fix-cmd CLI tool.
    Accepts a mistyped command and prints the best suggestion.
    """
    if len(sys.argv) < 2:
        print("Usage: fix-cmd <mistyped_command>")
        sys.exit(1)
    mistyped_command = " ".join(sys.argv[1:])
    suggestion = suggest_correction(mistyped_command)
    print(f"You entered: {mistyped_command}")
    print(f"Suggested command: {suggestion}")

if __name__ == "__main__":
    main()
