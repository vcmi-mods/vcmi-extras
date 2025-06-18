#!/usr/bin/env python3

import re
import sys
from pathlib import Path
from pprint import pprint

# VCMI supports JSON with comments, but not JSON5
import jstyleson

validation_failed = False


def parse_version(ver):
    """Parse a version string into a tuple of integers for comparison."""
    return tuple(int(part) for part in re.findall(r'\d+', ver))

def validate_version_field(json_data):
    """Validate that the JSON data contains a 'version' field."""
    if "version" not in json_data:
        raise ValueError("Missing 'version' field")
    return

def validate_changelog_field(json_data):
    """Validate that the JSON data contains a 'changelog' field."""
    if "changelog" not in json_data or not isinstance(json_data["changelog"], dict):
        raise ValueError("Does not have a valid 'changelog' field")
    return

def validate_mod_ver(json_data):
    """Validate the 'version' field against the 'changelog' field."""
    if "changelog" in json_data and isinstance(json_data["changelog"], dict):
        changelog_versions = list(json_data["changelog"].keys())
        highest_changelog_version = max(changelog_versions, key=parse_version)
        mod_version = json_data["version"]
        if parse_version(mod_version) < parse_version(highest_changelog_version):
            raise ValueError(
                f"Version mismatch: 'version' is {mod_version}, but changelog contains higher version {highest_changelog_version}"
            )
        if parse_version(mod_version) > parse_version(highest_changelog_version) and mod_version not in changelog_versions:
            raise ValueError(
                f"Version {mod_version} is newer than any version documented in changelog"
            )
    return

for path in sorted(Path(".").glob("**/*.json"), key=lambda path: str(path).lower()):
    path_str = str(path)
    if path_str.startswith("."):
        continue

    try:
        with open(path_str, "r") as file:
            dictH = jstyleson.load(file)
            if path.name == "mod.json":
                validate_version_field(dictH)
                # Check for changelog field only in /mod.json
                if path.name == path_str:
                    validate_changelog_field(dictH)
                validate_mod_ver(dictH)
            print(f"✅ {path_str}")
    except Exception as exc:
        print(f"❌ {path_str}: {exc}")
        validation_failed = True

if validation_failed:
    sys.exit(1)

