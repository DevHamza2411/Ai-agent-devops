from pathlib import Path

# Define standard log levels globally
LOG_LEVELS = ["INFO", "WARNING", "ERROR"]

def read_file(path: str) -> str:
    """Reads and returns the content of a file given its path string."""
    # Convert string path to Path object and resolve it to handle any WSL links
    return Path(path).resolve().read_text(encoding="utf-8")

def count_log_levels(log_content: str) -> dict:
    """
    Counts the occurrences of INFO, WARNING, and ERROR from a raw log string text.
    """
    # Initialize counts dictionary
    counts = {level: 0 for level in LOG_LEVELS}
    
    # Split text content into lines and remove empty lines or whitespace strings
    lines = [line.strip() for line in log_content.split('\n') if line.strip()]
    
    # Check each line for matching log levels
    for line in lines:
        for level in LOG_LEVELS:
            if level in line:
                counts[level] += 1
                
    return counts

#print(count_log_levels(Levels))