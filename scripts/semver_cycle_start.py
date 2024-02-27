from os import getenv
import re

from github import Github
import semver

"""
Get the first release of the release cycle for the current release type. (patch, minor, major)
If `LAST_RELEASE` is set, the last release of that release type will be returned.
eg. last minor version of 0.10.7-a2 -> 0.10.0
"""

GITHUB_REPOSITORY = getenv("GITHUB_REPOSITORY")
RELEASE_TYPE = getenv("RELEASE_TYPE")
LAST_RELEASE = bool(getenv("LAST_RELEASE"))

if any(req is None for req in [GITHUB_REPOSITORY, RELEASE_TYPE]):
    raise ValueError("Missing required environment variable(s)")

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
if not releases:
    print("0.0.0")
    exit(0)

for id, release in enumerate(releases):
    version = get_semver(release.tag_name)
    if id == 0:
        latest_version = version
        continue

    if not version:
        continue
    elif in_cycle(version) and RELEASE_TYPE in ["patch", "minor", "major"]:
        start_cycle_id = id

if latest_version is None:
    print("0.0.0")
    exit(0)
elif not LAST_RELEASE and start_cycle_id > 0:
    start_cycle_id -= 1

print(releases[start_cycle_id].tag_name)
