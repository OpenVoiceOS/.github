import os
from os.path import join, dirname, isfile
import json
from typing import List

from github import Github, PullRequest
import pccc

TOKEN = os.getenv('GH_PAT') or os.getenv('GITHUB_TOKEN')
REPOSITORY = os.getenv('GITHUB_REPOSITORY')
PR_LABELS: dict = json.loads(os.getenv('PR_LABELS', '{}'))
PR_NUMBER = os.getenv('PR_NUMBER')
ERROR_ON_MISSING_CC = os.getenv('MISSING_CC_ERROR', 'true').lower() == 'true'
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

def check_for_labels(pull_request: PullRequest) -> List[str]:
    global cc_missing
    
    ccr = pccc.ConventionalCommitRunner()
    ccr.options.load()
    ccr.raw = f"{pull_request.title}\n{pull_request.body}"
    ccr.clean()
    labels = set()
    try:
        ccr.parse()
    # no spec compliant format
    except Exception:
        labels.add(PR_LABELS.get("need_cc", "cc missing"))
        cc_missing = True
    else:
        if ccr.breaking.get("flag") or ccr.breaking.get("token"):
            labels.add(PR_LABELS.get("breaking", "breaking change"))
        if ccr.header.get("scope") in PR_LABELS:
            labels.add(PR_LABELS.get(ccr.header["scope"]))
        if ccr.header.get("type") in PR_LABELS:
            labels.add(PR_LABELS.get(ccr.header["type"]))
        if ongoing_test:
            labels.add("do not merge")
        
    return list(labels)


git = Github(TOKEN).get_repo(REPOSITORY)
open_pulls = git.get_pulls(state='open')
cc_missing = False


for pr in open_pulls:
    if PR_NUMBER and pr.number != int(PR_NUMBER):
        continue
    labels = check_for_labels(pr)
    pr.set_labels(*labels)

# nuke status check
if (cc_missing and ERROR_ON_MISSING_CC) or ongoing_test:
    raise Exception(f"CC missing: {cc_missing}, ongoing test phase: {ongoing_test}")
