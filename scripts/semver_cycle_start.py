from os import getenv
import re

from github import Github
import semver

"""
Get the first, last, latest or next release versions of the release cycle 
for the current release type. (patch, minor, major)

    enviroment Variable `RELEASE`:
    if unset, the first release of that release type in the current cycle will be returned.

    If set to `last`, the last release of that release type in the current cycle will be returned.
    eg. last minor version of 0.10.7-a2 -> 0.10.0
        last patch version of 0.10.1 -> 0.10.1
        last patch version of 0.10.0a2 -> 0.10.0 (!)

    If set to `latest`, returns the latest version released.

    If set to `next` the next release of the upcoming release type will be returned.
    eg. next minor version of 0.10.7-a2 -> 0.11.0
        next alpha version of 0.10.7 -> 0.10.8a1
        next alpha version of 0.10.7a2 -> 0.10.7a3
"""

ALPHA_MARKER = getenv("ALPHA_MARKER", "a") 

GITHUB_REPOSITORY = getenv("GITHUB_REPOSITORY")
RELEASE_TYPE = getenv("RELEASE_TYPE", "").lower().strip()
RELEASE = getenv("RELEASE", "").lower().strip()

# validate environment variables
if RELEASE and RELEASE not in ["last", "next", "latest"]:
    raise ValueError("Invalid value for `RELEASE` environment variable. "
                     "Expected one of `last`, `next`, `latest`.")

if RELEASE_TYPE and RELEASE_TYPE not in ["patch", "minor", "major", "alpha"]:
    raise ValueError("Invalid value for `RELEASE_TYPE` environment variable. "
                     "Expected one of `patch`, `minor`, `major`, `alpha`.")

requirements = {
    "GITHUB_REPOSITORY": GITHUB_REPOSITORY
}
if RELEASE != "latest":
    requirements.update({"RELEASE_TYPE", RELEASE_TYPE})

missing_req = [name for name, value in requirements.items() if value is None]
if missing_req:
    raise ValueError("Missing required environment variable(s) "
                     f"{str(missing_req)}")

# get the repo
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
    elif RELEASE_TYPE in ["alpha", ""]:
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

# get the release history
releases = repo.get_releases()

for id, release in enumerate(releases):
    version = get_semver(release.tag_name)
    if id == 0:
        latest_version = version
        if RELEASE == "next":
            next_version = bump_version(latest_version)
            break
        elif RELEASE == "latest":
            start_cycle_id = 0
            break
        continue

    if not version:
        continue
    elif in_cycle(version) and RELEASE_TYPE in ["patch", "minor", "major"]:
        start_cycle_id = id

version = None
if latest_version is None:
    version = "0.0.0"
    if RELEASE == "next":
        version = bump_version(semver.Version.parse(version))
elif RELEASE == "next":
    version = next_version
elif not RELEASE == "last" and start_cycle_id > 0:
    start_cycle_id -= 1

print(version or releases[start_cycle_id].tag_name)
