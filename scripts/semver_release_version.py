from os import getenv
from os.path import isfile
import re

from github import Github
import semver
import argparse

"""
Get the first, last, latest or next release versions of the release cycle 
for the current release type. (patch, minor, major)

Args
    --alpha_marker: str        # marker for alpha releases, default is 'a'
    --repo: str                # the repository to get the releases from
    --type: str                # the release type to get the version for
    --output_file: str         # writes an ovos version file to the specified path

Flags
    --last                     # get the last release of that release type in the current cycle
    --next                     # get the next release of the upcoming release type
    --latest                   # get the latest version released
    none of above              # get the first release of that release type in the current cycle
"""

parser = argparse.ArgumentParser()

parser.add_argument("--alpha_marker", default="a")
parser.add_argument("--repo", required=True)
parser.add_argument("--type", choices=["patch", "minor", "major", "alpha", "prerelease"])
parser.add_argument("--output_file")

release_group = parser.add_mutually_exclusive_group()
release_group.add_argument("--last", action='store_true')
release_group.add_argument("--next", action='store_true')
release_group.add_argument("--latest", action='store_true')

args = parser.parse_args()


RELEASE_TYPE = args.type
# old habits
if RELEASE_TYPE == "alpha" or RELEASE_TYPE is None:
    RELEASE_TYPE = "prerelease"

if not args.latest and not RELEASE_TYPE:
    raise ValueError("Missing release type. Please set the `--type` argument")

if args.output_file and not isfile(args.output_file):
    raise ValueError(f"Output file does not exist: {args.output_file}")

# get the repo
repo = Github(getenv("GH_PAT")).get_repo(args.repo)
latest_version = None
release_id = None

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
    return to_pypi_format(v.next_version(RELEASE_TYPE, args.alpha_marker))


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
if not releases:
    semv = semver.Version.parse("0.0.0")
    if args.next:
        semv = semv.next_version(RELEASE_TYPE, args.alpha_marker)
elif not args.next and not args.latest:
    for id, release in enumerate(releases):
        version = get_semver(release.tag_name)
        if version and in_cycle(version) and RELEASE_TYPE in ["patch", "minor", "major"]:
            release_id = id
elif args.next:
    latest_version = get_semver(releases[0].tag_name)
    semv = latest_version.next_version(RELEASE_TYPE, args.alpha_marker)
elif args.latest:
    semv = get_semver(releases[0].tag_name)
    release_id = 0

if not args.last and release_id:
    release_id -= 1

if release_id is not None:
    semv = get_semver(releases[release_id].tag_name)

if args.output_file:
    version_block = f"""
# START_VERSION_BLOCK
VERSION_MAJOR = {semv.major}
VERSION_MINOR = {semv.minor}
VERSION_BUILD = {semv.patch}
VERSION_ALPHA = {semv.prerelease.replace(args.alpha_marker, '').replace(".", "") if semv.prerelease else 0}
# END_VERSION_BLOCK
"""
    with open(args.output_file, "w") as f:
        f.write(version_block)

if release_id is not None:
    print(releases[release_id].tag_name)
else:
    print(to_pypi_format(semv))
