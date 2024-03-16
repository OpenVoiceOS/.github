import os
from os.path import join, dirname, isfile
import json
from typing import List, Optional

from github import Github, PullRequest
import pccc

TOKEN = os.getenv('GH_PAT') or os.getenv('GITHUB_TOKEN')
REPOSITORY = os.getenv('GITHUB_REPOSITORY')
PR_LABELS: dict = json.loads(os.getenv('PR_LABELS', '{}'))
SINGLE_PR = os.getenv('PR_NUMBER')
ERROR_ON_FAILURE = os.getenv('ERROR_ON_FAILURE', 'false').lower() == 'true'
if not PR_LABELS:
    PR_LABELS = json.loads(open(join(dirname(dirname(__file__)), "pr_labels.json")).read())

test_phase_cache = os.getenv('TEST_PHASE_CACHE', '')
if not isfile(test_phase_cache):
    ongoing_test = False
    if test_phase_cache:
        print("The file specified in TEST_PHASE_FILE does not exist.")
else:
    with open(test_phase_cache, 'r') as f:
        ongoing_test = f.read().strip() == "testing"


def cc_type(desc: str) -> str:
    ccr = parse_cc(desc)
    if ccr:
        if ccr.breaking.get("flag") or ccr.breaking.get("token"):
            return "breaking"
        return ccr.header.get("type")

    return "unknown"


def cc_scope(desc: str) -> str:
    ccr = parse_cc(desc)
    if ccr:
        return ccr.header.get("scope")

    return "unknown"


def parse_cc(desc: str) -> Optional[pccc.ConventionalCommitRunner]:
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load()
    ccr.raw = desc
    ccr.clean()
    try:
        ccr.parse()
        return ccr
    # no spec compliant format
    except Exception:
        return None


def check_cc_labels(desc: str) -> List[str]:

    labels = set()
    _type = cc_type(desc)
    _scope = cc_scope(desc)
    if _type == "unknown":
        return [PR_LABELS.get("need_cc", "CC missing")]
    if _type == "breaking":
        labels.add(PR_LABELS.get("breaking", "breaking change"))
    if _scope in PR_LABELS:
        labels.add(PR_LABELS.get(_scope))
    if _type in PR_LABELS:
        labels.add(PR_LABELS.get(_type))
    if ongoing_test and not any(t == "release" for t in [_type, _scope]):
        labels.add("ongoing test")
        
    return list(labels)


git = Github(TOKEN).get_repo(REPOSITORY)
open_pulls = git.get_pulls(state='open')
cc_missing = False


for pr in open_pulls:
    if SINGLE_PR and pr.number != int(SINGLE_PR):
        continue
    pr_description = f"{pr.title}\n{pr.body}"
    labels = check_cc_labels(pr_description)
    pr.set_labels(*labels)

    # clear the test flag if the PR adresses a release. Ie. gets added to the test
    if SINGLE_PR:
        if cc_type(pr_description) == "release":
            ongoing_test = False
        elif cc_type(pr_description) == "unknown":
            cc_missing = True

# nuke status check (if requested)
if (cc_missing or ongoing_test) and ERROR_ON_FAILURE:
    raise Exception(f"CC missing: {cc_missing}, ongoing test phase: {ongoing_test}")
