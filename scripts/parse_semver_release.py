import pccc
import semver
from os import environ

"""
translates a conventional commit title/message into a semver version
"""

TITLE = environ.get("TITLE")
BODY = environ.get("BODY")
VERSION = environ.get("VERSION")

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
    
    

if VERSION:
    release = semver_from_version()
elif TITLE:
    release = semver_from_cc()
else:
    print("No semver release.")
    exit(0)

print(release)