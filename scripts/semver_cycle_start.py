from os import getenv
import re

from github import Github
import semver

"""
Get the first, last or next release versions of the release cycle 
for the current release type. (patch, minor, major)

    If `LAST_RELEASE` is set, the last release of that release type will be returned.
    eg. last minor version of 0.10.7-a2 -> 0.10.0

    If `NEXT_RELEASE` is set, the next release of the upcoming release type will be returned.
    eg. next minor version of 0.10.7-a2 -> 0.11.0
        next alpha version of 0.10.7 -> 0.10.8a1
        next alpha version of 0.10.7a2 -> 0.10.7a3
    
"""

ALPHA_MARKER = getenv("ALPHA_MARKER", "a") 

GITHUB_REPOSITORY = getenv("GITHUB_REPOSITORY")
RELEASE_TYPE = getenv("RELEASE_TYPE")
LAST_RELEASE = bool(getenv("LAST_RELEASE"))
NEXT_RELEASE = bool(getenv("NEXT_RELEASE"))

if any(req is None for req in [GITHUB_REPOSITORY, RELEASE_TYPE]):
    raise ValueError("Missing required environment variable(s) "
                     "`GITHUB_REPOSITORY` and `RELEASE_TYPE`)")

repo = Github(getenv("GH_PAT")).get_repo(GITHUB_REPOSITORY)
latest_version = None
start_cycle_id = 0

def get_semver(tag: str) -> semver.Version:
    # hack for v prefix
    tag = tag.lstrip("v").lstrip("V")

    # hack for alpha releases
    if re.match(r"[0-9]+\.[0-9]+\.[0-9]+a[0-9]+", tag):
        tag = re.sub(r"([0-9]+)(a[0-9]+)", r"\1-\2", tag)

    if not semver.Version.is_valid(tag):
        return None
    return semver.Version.parse(tag)


def bump_version(v: semver.Version) -> semver.Version:
    if RELEASE_TYPE == "patch":
        return v.bump_patch()
    elif RELEASE_TYPE == "minor":
        return v.bump_minor()
    elif RELEASE_TYPE == "major":
        return v.bump_major()
    elif RELEASE_TYPE == "alpha":
        if not v.prerelease:
            v = v.bump_patch()
        return to_pypi_format(v.bump_prerelease(ALPHA_MARKER))


def to_pypi_format(v: semver.Version) -> str:
    return f"{v.major}.{v.minor}.{v.patch}{v.prerelease.replace('.', '') if v.prerelease else ''}"


def in_cycle(v: semver.Version) -> bool:
    if RELEASE_TYPE == "patch":
        return v.patch == latest_version.patch and not \
                (v.minor < latest_version.minor) and not \
                (v.major < latest_version.major)
    elif RELEASE_TYPE == "minor":
        return v.minor == latest_version.minor and not \
                (v.major < latest_version.major)
    elif RELEASE_TYPE == "major":
        return v.major == latest_version.major


releases = repo.get_releases()

for id, release in enumerate(releases):
    version = get_semver(release.tag_name)
    if id == 0:
        latest_version = version
        if NEXT_RELEASE:
            next_version = bump_version(latest_version)
            break
        continue

    if not version:
        continue
    elif in_cycle(version) and RELEASE_TYPE in ["patch", "minor", "major"]:
        start_cycle_id = id

version = None
if latest_version is None:
    version = "0.0.0"
    if NEXT_RELEASE:
        version = bump_version(semver.Version.parse(version))
elif NEXT_RELEASE:
    version = next_version
elif not LAST_RELEASE and start_cycle_id > 0:
    start_cycle_id -= 1

print(version or releases[start_cycle_id].tag_name)
