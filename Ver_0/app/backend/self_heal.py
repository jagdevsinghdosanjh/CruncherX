import os
import re

# Pattern that matches Edge sidebar injected metadata
EDGE_METADATA_PATTERN = re.compile(
    r"# User's Edge browser tabs metadata[\s\S]*?edge_all_open_tabs\s*=\s*\[.*?\]",
    re.MULTILINE
)

def clean_file(path: str):
    """Remove Edge metadata from a single file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # If no metadata found, skip
        if "edge_all_open_tabs" not in content:
            return False

        # Remove metadata block
        cleaned = re.sub(EDGE_METADATA_PATTERN, "", content)

        # Write cleaned file
        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"[SELF-HEAL] Cleaned metadata from: {path}")
        return True

    except Exception as e:
        print(f"[SELF-HEAL ERROR] Could not clean {path}: {e}")
        return False


def heal_project(root="app"):
    """Scan entire CruncherX project and remove Edge metadata."""
    healed_files = 0

    for subdir, _, files in os.walk(root):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(subdir, file)
                if clean_file(full_path):
                    healed_files += 1

    print(f"[SELF-HEAL] Completed. Files healed: {healed_files}")
    return healed_files