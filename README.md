## Conventional Commits
We _slowly_ adopt [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) to our repositories.  
Goal is to have a consistent commit message format that can be used to 
  - _streamline cd/ci_ or simply
  - _help understand commits better_ for every party involved.  

The usage is not mandatory atm, but we encourage to use it. (maintainers will adjust the commit messages if necessary) 

------------
_Types_:  

Using below prefixes (eg. `fix: ...`) will automate the versioning and labelling of the pull requests.
  - `fix`: patches a bug in your codebase. This correlates with _**PATCH**_ in Semantic Versioning.
  - `feat`: introduces a new feature to the codebase. This correlates with _**MINOR**_ in Semantic Versioning.
  - BREAKING CHANGE: A commit that has a _footer_ `BREAKING CHANGE:`, or _appends a `!`_ after the type/scope, introduces a breaking API change. This correlates with _**MAJOR**_ in Semantic Versioning. A BREAKING CHANGE can be part of commits of any type.
    
    Example (usage of _!_ and _footer_):  
    ```
    chore!: drop support for Node 6

    BREAKING CHANGE: use JavaScript features not available in Node 6.
    ```
  Other _types_ that create a alpha release - if not breaking:
  - `build`: Changes that affect the build system or external dependencies.
  - `chore`: Changes which don’t change source code or tests e.g. changes to the build process, auxiliary tools, libraries.
  - `perf`: A code change that improves performance.
  - `refactor`: A code change that neither fixes a bug nor adds a feature.
  - `revert`: Revert something.

  _Types_ that don't get a release:
  - `ci`: Changes to CI configuration files and scripts.
  - `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
  - `test`: Adding missing tests or correcting existing tests.
  - `docs`: Documentation only changes.

---------------
  _Scopes_:  
  (context of the change; eg. `fix(parser): ...`)
  
  - `config`: Changes the configuration
  - `parser`: Changes to the intent parser code,
  - ...
  - `cli`: Changes/additions to the command line interfaces,
  - `gui`: Changes/additions to the graphical user interface,
  - `audio`: Changes to the audio handling,
  - `tts`: Changes to the text-to-speech handling,
  - `sst`: Changes to the speech-to-text handling,
  - `nlp`: Changes to the natural language processing,
  - `plugins`: Changes to the plugin system,
  - `localisation`: Changes to the localisation files,
  - `resources`: Changes to the resource files,
  - `release`: Everything related to the release process  
  
  This is an excerpt [list of predefined scopes](https://github.com/OpenVoiceOS/.github/blob/feat/shared_actions1/pccc.toml). This list is not exclusive, but the main system components.
  If you have to be more specific, feel free to use submodule names or more detailed scopes.

--------------
## Premises
  - The `main` branch is the stable branch.  
  - The `dev` branch is the development branch.  
  - The `testing` branch is a persistent branch for testing purposes.  
---------
  - Pushed or merged commits without a proper title/commit message (Conventional Commit spec) will get no release.  
  - Translations are supposed to be prefixed as `fix` or `feat` to get a stable release.  
  - General rule: PRs/commits are _dev only_, other branches will be protected.
  - PRs/commits that directly address issues with a **release** need a prefix/scope `fix(release):`/`release(<scope>):`. _Those_ will be part of the patch/minor/major release.
  - remember: `ci`/`style`/`test`/`docs` commits don't get a release.
  - The version of the `testing` branch is to be held steady.
  - A fix for later releases has to be commited as usual with `fix: ...`. Those PRs get a warning label "test ongoing". Usually it`s best to include them into the ongoing release/test.
  - All pending PRs get a daily check (00:00 UTC) and labeling is adjusted accordingly.
  - The PR title of release PRs that conclude the testing phase (_Proposals_) mustn't be edited
  - If those proposals need additional changes, the PR is to be closed until the changes are commited (to dev).
  - Release-tags: The tag resembles the semantic versioning (eg. `1.2.3`; no prefix!, alphas will be formatted appropriately)  

  TODO (per repo):
  - `setup.py`: setuptools cant cope with semver compliance: `x.x.x-alpha...` stays `x.x.xax` for now
  - add `main` branch protection rules

------------
## Workflows/Actions
**You can also find the implementation of the workflows in the [`skill-template-repo`](https://github.com/OpenVoiceOS/skill-template-repo)**

## Release Handling (alpha/patch/minor/major versions)
_Alpha releases are directly published without going through a test phase_

Strategy: 3-staged  
  - _Manually_ propose a testing start or _automatically_ with setting "Conventional Commits"
  - _Manually_ conclude testing phase, propose a stable release (PR)
  - _Automatically_ publishing a stable release (on merge)

**Start release mechanism**  

```yaml
name: Start release mechanism
on:
  workflow_dispatch:
    inputs:
      release_type:
        type: choice
        options:
          - "alpha"
          - "patch"
          - "minor"
          - "major"
  # Make SURE that sqashed PRs do have the PRs title as commit message !!!!!!!!
  push:
    branches:
      - dev
    paths-ignore:
      - 'ovos_testpkg/version.py'
      - 'test/**'
      - 'examples/**'
      - '.github/**'
      - '.gitignore'
      - 'CHANGELOG.md'
      - 'MANIFEST.in'
      - 'scripts/**'

jobs:
  start_semver_release_mechanism:
    if: github.actor != 'EggmanBot'
    uses: openvoiceos/.github/.github/workflows/release_semver_start.yml@feat/shared_actions1
    with:
      branch: dev                                                  # Branch to use, default: branch that triggered the action
      action_branch: feat/shared_actions1                          # Shared action branch to use, default: main
      python_version: "3.10"                                       # the python version to use
      version_file: "ovos_testpkg/version.py"                      # the file containing the version number
      locale_folder: ovos_testpkg/locale                           # the location of the base localisation folder
      update_intentfile: test/unittests/test_intent.yaml           # the intent file resources gets tested against
      release_type: ${{ inputs.release_type || null }}             # if manually triggered, set a release type
      subject: ${{  github.event.head_commit.message || null }}    # on push, the commit message is used as release subject
```
**Conclude testing phase**  

_After the testing phase, a PR is opened to propose the stable release_  
```yaml
name: Conclude testing phase
on:
  workflow_dispatch:

jobs:
  pull_to_master:
    uses: openvoiceos/.github/.github/workflows/release_semver_pull_master.yml@feat/shared_actions1
    secrets: inherit
    with:
      action_branch: shared_actions1              # Shared action branch to use, default: main
      python_version: "3.10"                      # the python version to use
```
**Publishing stable release**  

```yaml
name: Publish Stable Release

on:
  pull_request:
    types: [ closed ]
    branches:
      - master

jobs:
  publish_stable_release:
    if: >
      github.event.pull_request.merged == true &&
      github.actor != 'EggmanBot' &&
      (contains(github.event.pull_request.title, 'patch release stable') ||
      contains(github.event.pull_request.title, 'minor release stable') ||
      contains(github.event.pull_request.title, 'major release stable'))
    uses: openvoiceos/.github/.github/workflows/release_semver_publish.yml@feat/shared_actions1
    secrets: inherit
    with:
      action_branch: feat/shared_actions1
      python_version: "3.10"
      subject: ${{ github.event.pull_request.title }}
```  
-----------------

## Propose translatios
Introduce a new language localisation by proposing a translation via pull request. (creating new branch staging/translation_xx-xx)
```yaml
name: Propose Translations
on:
  workflow_dispatch:
    inputs:                                       # multiple ways to set this up
      translation:                                # predefined list of languages*
        type: choice
        options:
          - "de-de"
          ...
          - "zh-cn"
      # or
      translations:                               # wait for dispatcher input for a langcode (xx-xx)
        type: string
        required: true

jobs:
  propose_translation:
    uses: openvoiceos/.github/.github/workflows/propose_translation.yml@main
    secrets: inherit
    with:
      branch: dev                               # Branch to use, default: branch that triggered the action
      python_version: "3.8"
      language: ${{ inputs.translation }}
      locale_folder: ovos_core/locale/          # the location of the base localisation folder, default: locale
      reviewers: "jarbasai,emphasize"           # comma separated list of reviewers, default: emphasize
```
* [available languages with deepl](https://support.deepl.com/hc/en-us/articles/360019925219-Languages-included-in-DeepL-Pro)

## License testing
Tests validity of licenses of all packages (explicit and transitive).
(Note:)
```yaml
name: License testing
on:
  <trigger strategy>

jobs:
  license_tests:
    if: github.actor != 'EggmanBot'
    uses: openvoiceos/.github/.github/workflows/license_tests.yml@main
    with:
      runner: ubuntu-latest                     # Runner to use, default: ubuntu-latest
      branch: dev                               # Branch to use, default: branch that triggered the action
      system_deps: "somepkg"                    # System dependencies (whitespace delimited) to install
      pip_packages: "random-pkg"                # Python packages (whitespace delimited) to install
      python_version: "3.8"                     # Python version (quoted) to use, default: 3.8
      install_extras: test                      # Optional extras to install the python package with
      packages-exclude: '^(fann2|tqdm|bs4).*'   # Custom regex to exclude packages from the license check
                                                # default: '^(precise-runner|fann2|tqdm|bs4|nvidia|bitstruct).*'
      licenses-exclude: ^(BSD-3).*$'            # Custom regex to exclude licenses from the license check
                                                # default: '^(Mozilla|NeonAI License v1.0).*$'
```
## Build testing
Tests the build of the python package.
```yaml
name: Build testing
on:
  <trigger strategy>

jobs:
  build_tests:
    if: github.actor != 'EggmanBot'
    uses: openvoiceos/.github/.github/workflows/python_build_tests.yml@main
    with:
      runner: ubuntu-latest                     # Runner to use, default: ubuntu-latest
      branch: dev                               # Branch to use, default: branch that triggered the action
      system_deps: "libfann-dev libfann2"       # System dependencies (whitespace delimited) to install
      pip_packages: "pytest pytest-cov"         # Additional python packages (whitespace delimited) to install
                                                # commonly installed: `build wheel`
      python_matrix: '["3.8", "3.9", "3.10"]'   # Python version matrix to use, default: '["3.8", "3.9", "3.10", "3.11"]'
      test_manifest: true                       # if to test with MANIFEST.in, default: false
      manifest_ignored: "test/** qt5/**"        # Files to ignore in MANIFEST.in, default: "test/**"
      test_relative_paths: false                # if to test with relative paths, default: true
      test_pipaudit: true                       # if to test with pip-audit, default: false
      pipaudit_ignored: ""                      # Vulnerabilities to ignore in pip-audit,
                                                # default: "GHSA-r9hx-vwmv-q579 PYSEC-2022-43012"
```
## Unit Tests (file or directory)
```yaml
name: Unit Tests
on:
  <trigger strategy>

jobs:
  unit_tests:
    if: github.actor != 'EggmanBot'
    uses: openvoiceos/.github/.github/workflows/pytest_file_or_dir.yml@main
    with:
      runner: ubuntu-latest
      branch: dev                               # Branch to use, default: branch that triggered the action
      action_branch: custom/branch              # Shared action branch to use, default: main
      timeout_minutes: 15                       # Timeout in minutes for the job, default: 15
      system_deps: "libfann-dev libfann2"       # (*) Additional system dependencies to install before running the license check
      python_matrix: '["3.8", "3.9", "3.10"]'   # Python version matrix to use, default: '["3.8", "3.9", "3.10", "3.11"]'
      pip_packages: "pytest pytest-cov"         # (**) Additional python packages (whitespace delimited) to install
      pip_install_dirs: |                       # Additional directories to install python packages from
        relpath/to/package1
        relpath/to/package2
      install_extras: lgpl,mycroft              # Comma-separated extras to install the python package with
      test_location: test/unittests             # Test file (or directory) to run, default: test/unittests
      is_skill: true                            # Whether this is an ovos skill, default: false
      codecov: true                             # Whether to record the test code coverage, default: true
                                                # below (append/upload_coverage) can be omitted if codecov is false

      upload_coverage: true                     # Whether to upload the coverage to codecov server, default: false
                                                # should upload only if there are no following jobs that need coverage
  
  # showcase with multiple jobs that should add to the coverage test
  next_test_that_needs_coverage:
    if: github.actor != 'EggmanBot'
    needs: unit_tests
    uses: openvoiceos/.github/.github/workflows/pytest_file_or_dir.yml@main
    with:
      ...
      append_coverage: true                     # Whether to append coverage to the previous job, default: false
                                                # the artifact will be downloaded, appended and uploaded again
    ...
  and_another_test_that_needs_coverage:
    needs: [ unit_tests, next_test_that_needs_coverage ]
    if: github.actor != 'EggmanBot'
    uses: openvoiceos/.github/.github/workflows/pytest_file_or_dir.yml@main
    with:
      ...
      append_coverage: true
      upload_coverage: true                     # Whether to upload the coverage to codecov server
    ...
```
(*) [Common system dependencies](https://github.com/OpenVoiceOS/.github/requirements/sys_deb_common_deps.txt)  
(**) Common python dependencies: [skill](https://github.com/OpenVoiceOS/.github/requirements/pip_skill_tests.txt) / [other](https://github.com/OpenVoiceOS/.github/requirements/pip_tests.txt) 
## Skills
### Skill Installation Tests
```yaml
name: Skill Installation Tests
on:
  <trigger strategy>

jobs:
  skill_installation_tests:
    if: github.actor != 'EggmanBot'
    uses: openvoiceos/.github/.github/workflows/skill_test_installation.yml@main
    with:
      runner: ubuntu-latest
      branch: dev                               # Branch to use, default: branch that triggered the action
      action_branch: custom/branch              # Shared action branch to use, default: main
      system_deps: "libfann-dev libfann2"       # (*) Additional system dependencies (whitespace delimited) to install
      python_matrix: '["3.8", "3.9", "3.10"]'   # Python version matrix to use, default: '["3.8", "3.9", "3.10", "3.11"]'
      pip_packages: "pytest pytest-cov"         # (**) Additional python packages (whitespace delimited) to install'
      skill_id: "ovos-skill-x.openvoiceos"      # Skill id of the testskill, required
      skill_location: "skill"                   # Skill location relative to the root (can usually be omitted, used if the skill is not located in the base folder)
```
(*) [Common system dependencies](https://github.com/OpenVoiceOS/.github/requirements/sys_deb_common_deps.txt)  
(**) [Common python dependencies](https://github.com/OpenVoiceOS/.github/requirements/pip_skill_tests.txt)  
### Skill Resource Tests
Tests the resources of a skill (e.g dialogs, vocabs, regex or intent resources) for completeness and workability.
```yaml
name: Skill Ressource Tests
on:
  <trigger strategy>

jobs:
  skill_resource_tests:
    if: github.actor != 'EggmanBot'
    uses: openvoiceos/.github/.github/workflows/skill_test_resources.yml@main
    with:
      runner: ubuntu-latest                     # Runner to use, default: ubuntu-latest
      timeout: 15                               # Timeout for the test, default: 15
      branch: dev                               # Branch to use, default: branch that triggered the action
      action_branch: custom/branch              # Shared action branch to use, default: main
      system_deps: "libfann-dev libfann2"       # (*) Additional system dependencies (whitespace delimited) to install
      python_matrix: '["3.8", "3.9", "3.10"]'   # Python version matrix to use, default: '["3.8", "3.9", "3.10", "3.11"]'
      pip_packages: "pytest pytest-cov"         # (**) Additional python packages (whitespace delimited) to install
      intent_testfile: test/test_intents.yaml   # Intent test file to test against, required
      test_padatious: true                      # if to test against padatious, default: false
      test_padacioso: true                      # if to test against padacioso, default: true
```
(*) [Common system dependencies](https://github.com/OpenVoiceOS/.github/requirements/sys_deb_common_deps.txt)  
(**) [Common python dependencies](https://github.com/OpenVoiceOS/.github/requirements/pip_skill_tests.txt)  
## Notifications
### Notify Matrix on Pull Request
```yaml
name: Notify Matrix Chat

on:
  pull_request:
    types: [ closed ]

jobs:
  notify_pr_matrix:
    if: github.event.pull_request.merged == true
    secrets: inherit
    uses: openvoiceos/.github/.github/workflows/notify_pr_matrix.yml@main
    with:
      pr_id: ${{ github.event.number }}
      subject: ${{ github.event.pull_request.title }}
```
-------------

![OpenVoiceOS](https://openvoiceos.com/wp-content/uploads/2020/10/loading400.png)
# OpenVoiceOS
A community powered Linux distribution, purpose-built with buildroot to showcase the power of Open Source Voice AI for a range of devices.

## About
OpenVoiceOS is a minimalistic linux OS bringing the open source voice assistant Mycroft A.I. to embbeded, low-spec headless and/or small (touch)screen devices.

## Get Involved

At this moment development is in very early stages and focussed on the Raspberry Pi 3B & 4. As soon as an initial first workable version is created, other hardware might be added.

* [Discussion Board](https://github.com/OpenVoiceOS/OpenVoiceOS/discussions)
* [Forum thread @ Mycroft A.I.](https://community.mycroft.ai/t/openvoiceos-a-bare-minimal-production-type-of-os-based-on-buildroot/4708)
* [Matrix Chat rooms](https://matrix.to/#/!XFpdtmgyCoPDxOMPpH:matrix.org?via=matrix.org)

Visit [openvoiceos.org](https://openvoiceos.org) to learn more!