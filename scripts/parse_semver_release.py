import re
from os import environ

import pccc
import semver

"""
translates a conventional commit title/message into a semver version
"""


def get_version():
    # note: this is a PEP 440 compliant version, so alpha versions come in "1.0.0a1"
    version = environ.get("VERSION", "")
    match = re.match(r"(\d+\.\d+\.\d+)([aA-zZ].*)", )
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    else:
        return version


def semver_from_cc():
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load()
    ccr.raw = f"{TITLE}\n{BODY}"
    ccr.clean()
    try:
        ccr.parse()
    # no spec compliant format
    except Exception:
        print("No semver release.")
        exit(0)

    if ccr.breaking.get("flag") or ccr.breaking.get("token"):
        return "major"
    elif ccr.header.get("type") == "feat":
        return "minor"
    elif ccr.header.get("type") == "fix":
        return "patch"
    else:
        return "alpha"

def semver_from_version():
    try:
        version = semver.VersionInfo.parse(VERSION)
    except ValueError:
        print("No semver release.")
        exit(0)
    
    if version.prerelease:
        return "alpha"
    elif version.patch != 0:
        return "patch"
    elif version.minor != 0:
        return "minor"
    elif version.major != 0:
        return "major"
    
TITLE = environ.get("TITLE")
BODY = environ.get("BODY")
VERSION = get_version()

if VERSION:
    release = semver_from_version()
elif TITLE:
    release = semver_from_cc()
else:
    print("No semver release.")
    exit(0)

print(release)