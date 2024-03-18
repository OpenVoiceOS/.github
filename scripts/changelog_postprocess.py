from os import environ
from os.path import join, dirname
import sys
import subprocess
import json
import re

CONTEXT = environ.get("CLIFF_CHANGELOG_CONTEXT")
PULL_LINK_PATTERN = r' \(\[#\d+\]\(https:\/\/github\.com\/.+?\/pull\/\d+\)\)'
CLIFF_IGNORE_FILE = join(environ.get("REPO_BASEDIR", ""), ".cliffignore")
CHANGELOG_ITEMS = environ.get("GIT_CLIFF_CHANGELOG_ITEMS", "full")


def escape_control_characters(s):
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda c: "\\u{0:04x}".format(ord(c.group())), s)

def strip_pull_request_links(text):
    return re.sub(PULL_LINK_PATTERN, '', text).strip()

def in_git_repo(file_path):
    try:
        subprocess.check_output(['git', '-C', dirname(file_path), 'rev-parse'])
        return True
    except subprocess.CalledProcessError:
        return False

def valid_json(s):
    try:
        json.loads(escape_control_characters(s))
        return True
    except json.JSONDecodeError:
        return False
    
if not valid_json(CONTEXT):
    raise Exception("You need to provide a valid changelog context (json)")
if not in_git_repo(CLIFF_IGNORE_FILE):
    raise Exception("You have to run this script in a git repository or provide a proper `REPO_BASEDIR` environment variable.")
else:
    # empty the file
    with open(CLIFF_IGNORE_FILE, 'w') as f:
        f.write("")
if not CHANGELOG_ITEMS in ["full", "latest", "current", "unreleased"]:
    raise ValueError("GIT_CLIFF_CHANGELOG_ITEMS must be one of 'latest', 'current', 'unreleased'")


escaped_json_string = escape_control_characters(CONTEXT)
changelog_context = json.loads(escaped_json_string)
last_message = None

for entry in changelog_context:
    last_commit = None
    for commit in entry.get('commits', []):

        message = commit['message']
        if not (last_commit and re.search(PULL_LINK_PATTERN, message)):
            last_commit = commit
            continue
        
        stripped_message = strip_pull_request_links(message)
        if stripped_message == last_commit['message'] and \
                commit.get('scope') == last_commit.get('scope'):
            # add to ignored commits (as the merge commit will be part of the changelog)
            with open(CLIFF_IGNORE_FILE, 'a') as f:
                f.write(f"{last_commit['id']}\n")
        last_message = message

if not open(CLIFF_IGNORE_FILE, 'r').read():
    print("No commits to ignore. No need to postprocess.")
    exit(0)

command = ["git", "cliff"]

if CHANGELOG_ITEMS == "unreleased":
    command.append("--unreleased")
elif CHANGELOG_ITEMS == "latest":
    command.append("--latest")
elif CHANGELOG_ITEMS == "current":
    command.append("--current")


process = subprocess.Popen(command, env=environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# interact with the subprocess's standard output and error streams
stdout, stderr = process.communicate()

# print the subprocess's standard output and error streams
print(stdout.decode())
print(stderr.decode(), file=sys.stderr)
