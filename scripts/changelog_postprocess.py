from os import environ
from os.path import join, dirname, isfile
import sys
import subprocess
import json
import re
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--context", "-c", help="Path to the changelog context file")
parser.add_argument("--items", "-i", choices=["latest", "current", "unreleased", "first unreleased"], default="full")
args = parser.parse_args()


PULL_LINK_PATTERN = r' \(\[#\d+\]\(https:\/\/github\.com\/.+?\/pull\/\d+\)\)'
CLIFF_IGNORE_FILE = join(environ.get("REPO_BASEDIR", ""), ".cliffignore")
GIT_CLIFF_OUTPUT = environ.get("GIT_CLIFF_OUTPUT")
if GIT_CLIFF_OUTPUT:
    del environ["GIT_CLIFF_OUTPUT"]
GIT_CLIFF_PREPEND = environ.get("GIT_CLIFF_PREPEND")
if GIT_CLIFF_PREPEND:
    del environ["GIT_CLIFF_PREPEND"]


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


def run_cliff(get_context = False):
    command = ["git", "cliff"]
    mute = False

    if args.items == "unreleased":
        command.append("--unreleased")
    elif args.items == "latest":
        command.append("--latest")
    elif args.items == "current":
        command.append("--current")

    if get_context:
        command.append("--context")
        mute = True
    elif GIT_CLIFF_OUTPUT:
        command.append("--output")
        command.append(GIT_CLIFF_OUTPUT)
    elif GIT_CLIFF_PREPEND:
        command.append("--prepend")
        command.append(GIT_CLIFF_PREPEND)

    process = subprocess.Popen(command, env=environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # interact with the subprocess's standard output and error streams
    stdout, stderr = process.communicate()

    # print the subprocess's standard output and error streams
    if not mute:
        print(stdout.decode())
        print(stderr.decode(), file=sys.stderr)

    return stdout.decode().strip()

if not args.context or not isfile(args.context):
    CONTEXT = run_cliff(get_context=True)
else:
    with open(args.context, 'r') as f:
        CONTEXT = f.read()

if not valid_json(CONTEXT):
    raise Exception("You need to provide a valid changelog context (json)")
if not in_git_repo(CLIFF_IGNORE_FILE):
    raise Exception("You have to run this script in a git repository or provide a proper `REPO_BASEDIR` environment variable.")
else:
    # empty the file
    with open(CLIFF_IGNORE_FILE, 'w') as f:
        f.write("")

escaped_json_string = escape_control_characters(CONTEXT)
changelog_context = json.loads(escaped_json_string)

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
        last_commit = commit


run_cliff()

# delete the ignore file
subprocess.run(["rm", CLIFF_IGNORE_FILE])
