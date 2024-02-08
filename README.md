## Workflows/Actions
**You can also find the implementation of the workflows in the [`skill-template-repo`](https://github.com/OpenVoiceOS/skill-template-repo)**

### Publish Alpha Release (example: `ovos-core`)
```yaml
name: Publish Alpha Build ...aX
on:
  push:
    branches:
      - dev
    paths-ignore:
      - 'ovos_core/version.py'
      - 'test/**'
      - 'examples/**'
      - '.github/**'
      - '.gitignore'
      - 'LICENSE'
      - 'CHANGELOG.md'
      - 'MANIFEST.in'
      - 'readme.md'
      - 'scripts/**'
  workflow_dispatch:

jobs:
  build_and_publish:
    uses: openvoiceos/.github/.github/workflows/publish_alpha_release.yml@main
    secrets: inherit
    with:
      branch: dev                               # Branch to use, default: branch that triggered the action
      version_file: ovos_core/version.py        # File location of the version file, default: version.py
      python_version: "3.8"                     # Python version (quoted) to use, default: 3.8
      locale_folder: ovos_core/locale           # use if there are localisation files the location of the base folder, default: locale
      update_intentfile: test/test_intents.yaml # use if there are changes to resource files, the test file to update. (ONLY USED IN SKILLS)
      changelog_file: CHANGELOG.md              # use if the changlog file has a special name, default: CHANGELOG.md
```
## Propose and Publish Stable (Build,Minor,Major) Release
Strategy: 2-staged  
*Proposal (prepares bump and pull requests to testing/stable)*  
This creates a pull request to the appropriate branch.  
On merge, the (shared) publish action is triggered. (no extra repo workflow needed)
```yaml
name: Propose Stable Build
on:
  workflow_dispatch:
    inputs:
      release_type:
        type: choice
        options:
          - "patch"
          - "minor"
          - "major"

jobs:
  build_and_publish:
    uses: openvoiceos/.github/.github/workflows/propose_semver_release.yml@main
    with:
      branch: dev                               # Branch to use, default: branch that triggered the action
      python_version: "3.10"                    # Python version (quoted) to use, default: 3.8
      version_file: ovos_core/version.py        # File location of the version file, default: version.py
      release_type: ${{inputs.release_type}}    # build, minor, major
      changelog_file: ChAnGeLoG.md              # if the changlog file has a special name, default: CHANGELOG.md
```
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
```yaml
name: License testing
on:
  <trigger strategy>

jobs:
  license_tests:
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
    needs: unit_tests
    uses: openvoiceos/.github/.github/workflows/pytest_file_or_dir.yml@main
    with:
      ...
      append_coverage: true                     # Whether to append coverage to the previous job, default: false
                                                # the artifact will be downloaded, appended and uploaded again
    ...
  and_another_test_that_needs_coverage:
    needs: [ unit_tests, next_test_that_needs_coverage ]
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
## Skill Installation Tests
```yaml
name: Skill Installation Tests
on:
  <trigger strategy>

jobs:
  skill_installation_tests:
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
## Skill Resource Tests
Tests the resources of a skill (e.g dialogs, vocabs, regex or intent resources) for completeness and workability.
```yaml
name: Skill Ressource Tests
on:
  <trigger strategy>

jobs:
  skill_resource_tests:
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
## Notify Matrix on Pull Request
```yaml
name: Notify Matrix Chat

# only trigger on pull request closed events
on:
  pull_request:
    types: [ closed ]

jobs:
  notify_pr_matrix:
    # this job will only run if the PR has been merged
    if: github.event.pull_request.merged == true
    secrets: inherit
    uses: openvoiceos/.github/.github/workflows/notify_pr_matrix.yml@main
    with:
      pr_id: ${{ github.event.number }}
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