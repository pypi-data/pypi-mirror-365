# Correction rules for common commands

def suggest_correction(cmd: str) -> str:
    """
    Suggests the correct command for a mistyped input using fuzzy matching.
    Args:
        cmd (str): The mistyped command string.
    Returns:
        str: The best matched command or '<no suggestion>'.
    """
    from .core import get_best_match
    return get_best_match(cmd.strip())
