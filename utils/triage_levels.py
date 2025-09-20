TRIAGE_LEVELS = {
    1: "Immediately life‑threatening",
    2: "Imminently life‑threatening",
    3: "Potentially life‑threatening",
    4: "Potentially serious",
    5: "Less urgent"
}

# Create reverse mapping for string to int conversion
TRIAGE_LEVELS_REVERSE = {v: k for k, v in TRIAGE_LEVELS.items()}

def get_triage_description(level: int) -> str:
    if level not in TRIAGE_LEVELS:
        print(f"Invalid triage level: {level}. Setting to 5.")
        level = 5
    return TRIAGE_LEVELS[level]

def get_triage_level(description: str) -> int:
    if description not in TRIAGE_LEVELS_REVERSE:
        print(f"Invalid triage description: {description}. Setting to 5.")
        return 5
    return TRIAGE_LEVELS_REVERSE[description]

# Example usage:
if __name__ == "__main__":
    # Integer to string
    print(get_triage_description(1))  # Output: Immediately life‑threatening
    # String to integer
    print(get_triage_level("Less urgent"))  # Output: 5
