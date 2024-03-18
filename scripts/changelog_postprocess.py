from os import environ
from os.path import join, dirname
import subprocess
import json
import re

#CONTEXT = environ.get("CLIFF_CHANGELOG_CONTEXT")
CONTEXT = '[{"version":"0.3.40a3","commits":[{"id":"e08c27d1c5dd61ddcd4fc28c50b1c756b68dd691","message":"bump","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"tts","links":[],"author":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710769697},"committer":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710769697},"conventional":true,"merge_commit":false,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"a99aab5ab0aac932035d784a204bf7c9fc58fa6a","message":"bump ([#198](https://github.com/<REPO>/pull/198))","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"tts","links":[],"author":{"name":"Swen Gross","email":"25036977+emphasize@users.noreply.github.com","timestamp":1710769744},"committer":{"name":"GitHub","email":"noreply@github.com","timestamp":1710769744},"conventional":true,"merge_commit":true,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"6d9e906d98700a3cd85483ed062a1a3bebb212e7","message":"bump","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"stt","links":[],"author":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710770502},"committer":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710770502},"conventional":true,"merge_commit":false,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"eda66264a83ef35d4df23f10026cc0257187ece5","message":"bump ([#199](https://github.com/<REPO>/pull/199))","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"stt","links":[],"author":{"name":"Swen Gross","email":"25036977+emphasize@users.noreply.github.com","timestamp":1710770515},"committer":{"name":"GitHub","email":"noreply@github.com","timestamp":1710770515},"conventional":true,"merge_commit":true,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"def1f9ee70493cdc9cf929981c95e4dbcab3249b","message":"bump","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"stt","links":[],"author":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710771913},"committer":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710771913},"conventional":true,"merge_commit":false,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"3d884ec8542bd005364e39ec748831e9186f3c0b","message":"bump ([#200](https://github.com/<REPO>/pull/200))","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"stt","links":[],"author":{"name":"Swen Gross","email":"25036977+emphasize@users.noreply.github.com","timestamp":1710771970},"committer":{"name":"GitHub","email":"noreply@github.com","timestamp":1710771970},"conventional":true,"merge_commit":true,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"2cfad089d4bee39fef7f9d324ffdb7cb4642f583","message":"bump","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"nlp","links":[],"author":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710772746},"committer":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710772746},"conventional":true,"merge_commit":false,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"5ad5da3faae949761edb42c31d189dc7dfe816bb","message":"bump ([#201](https://github.com/<REPO>/pull/201))","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"nlp","links":[],"author":{"name":"Swen Gross","email":"25036977+emphasize@users.noreply.github.com","timestamp":1710772790},"committer":{"name":"GitHub","email":"noreply@github.com","timestamp":1710772790},"conventional":true,"merge_commit":true,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"fa626505a36ef89e74582b370df82c9c2d3dbaf2","message":"bump","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"tts","links":[],"author":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710774510},"committer":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710774510},"conventional":true,"merge_commit":false,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"55147702f7980338cd976d67a2b39e5d07673943","message":"bump ([#202](https://github.com/<REPO>/pull/202))","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"tts","links":[],"author":{"name":"Swen Gross","email":"25036977+emphasize@users.noreply.github.com","timestamp":1710774531},"committer":{"name":"GitHub","email":"noreply@github.com","timestamp":1710774531},"conventional":true,"merge_commit":true,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"5300b035186ff3c9fdd9d668d0334c79074d33e5","message":"bump","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"stt","links":[],"author":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710774960},"committer":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710774960},"conventional":true,"merge_commit":false,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"6fb2ae48ca55dcf2b39733af612be8d12092447d","message":"bump ([#203](https://github.com/<REPO>/pull/203))","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"stt","links":[],"author":{"name":"Swen Gross","email":"25036977+emphasize@users.noreply.github.com","timestamp":1710774986},"committer":{"name":"GitHub","email":"noreply@github.com","timestamp":1710774986},"conventional":true,"merge_commit":true,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"602c9e970a3f01887e6856bc1b4d1797ebda3cc2","message":"bump","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":null,"links":[],"author":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710775850},"committer":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710775850},"conventional":true,"merge_commit":false,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"2fadd7b14552ced76f9065f94af4eb46085fa0b1","message":"bump ([#204](https://github.com/<REPO>/pull/204))","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":null,"links":[],"author":{"name":"Swen Gross","email":"25036977+emphasize@users.noreply.github.com","timestamp":1710775870},"committer":{"name":"GitHub","email":"noreply@github.com","timestamp":1710775870},"conventional":true,"merge_commit":true,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"e9a225a5e9a70c58daa4ff7f3ec2e7e29c7219ed","message":"bump","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"tts","links":[],"author":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710776421},"committer":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710776421},"conventional":true,"merge_commit":false,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"a47647e286cbd76cf8670ffb7e6fde5b152e0e05","message":"bump ([#205](https://github.com/<REPO>/pull/205))","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"tts","links":[],"author":{"name":"Swen Gross","email":"25036977+emphasize@users.noreply.github.com","timestamp":1710776448},"committer":{"name":"GitHub","email":"noreply@github.com","timestamp":1710776448},"conventional":true,"merge_commit":true,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"1b04cc8a3c8feba12f0c06dee23beeed826ebb03","message":"bump","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"stt","links":[],"author":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710776662},"committer":{"name":"emphasize","email":"swen_g@t-online.de","timestamp":1710776662},"conventional":true,"merge_commit":false,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}},{"id":"3cc132a8bf01d571e430ab85a01875ada9cb523c","message":"bump ([#206](https://github.com/<REPO>/pull/206))","body":null,"footers":[],"group":"<!-- 1 -->🐛 Bug Fixes","breaking_description":null,"breaking":false,"scope":"stt","links":[],"author":{"name":"Swen Gross","email":"25036977+emphasize@users.noreply.github.com","timestamp":1710776695},"committer":{"name":"GitHub","email":"noreply@github.com","timestamp":1710776695},"conventional":true,"merge_commit":true,"github":{"username":null,"pr_title":null,"pr_number":null,"pr_labels":[],"is_first_time":false}}],"commit_id":"3cc132a8bf01d571e430ab85a01875ada9cb523c","timestamp":1710791950,"previous":{"version":"0.3.40a2","commits":[],"commit_id":"2fcf56b470755c63d417c3c905fac274bdfe4203","timestamp":1710714924,"previous":null,"github":{"contributors":[]}},"github":{"contributors":[]}}]'
PULL_LINK_PATTERN = r' \(\[#\d+\]\(https://github\.com/.+?/pull/\d+\)\)'
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
    
if CONTEXT is None:
    print("You need to provide a changlog context (json)")
    exit(1)
if not in_git_repo(CLIFF_IGNORE_FILE):
    print("you have to run this script in a git repository or provide a proper `REPO_BASEDIR` environment variable.")
    exit(1)
else:
    # empty the file
    with open(CLIFF_IGNORE_FILE, 'w') as f:
        f.write("")
if not CHANGELOG_ITEMS in ["full", "latest", "current", "unreleased"]:
    raise ValueError("GIT_CLIFF_CHANGELOG_ITEMS must be one of 'latest', 'current', 'unreleased'")

escaped_json_string = escape_control_characters(CONTEXT)
changelog_context = json.loads(escaped_json_string)
last_message = None

# write the commits to be ignored in the postprocessing step
for entry in changelog_context:
    message = entry['message']
    if not(last_message and re.match(PULL_LINK_PATTERN)):
        continue
    
    # the merge_commit flag is not safe to use by itself
    # double check
    stripped_message = strip_pull_request_links(message)
    if message.get('merge_commit', False) or stripped_message == last_message:
        with open(CLIFF_IGNORE_FILE, 'a') as f:
            f.write(f"{message["id"]}\n")


            


    











