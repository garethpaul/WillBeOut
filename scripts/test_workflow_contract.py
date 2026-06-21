#!/usr/bin/env python3
from pathlib import Path
from workflow_contract import CHECKOUT_ACTION, SETUP_ACTION, validate
ROOT=Path(__file__).resolve().parents[1]
BASELINE=(ROOT/'.github/workflows/check.yml').read_text(encoding='utf-8')
def mutate(description,target,replacement):
    result=BASELINE.replace(target,replacement,1)
    if result==BASELINE: raise AssertionError(f'{description} mutation did not alter workflow')
    return result
def reject(description,workflow):
    if not validate(workflow): raise AssertionError(f'{description} mutation was accepted')
errors=validate(BASELINE)
if errors: raise AssertionError(f'baseline workflow invalid: {errors}')
mutations={
'contradictory credentials':mutate('contradictory credentials','persist-credentials: false','persist-credentials: false\n          persist-credentials: true'),
'relocated credentials':mutate('relocated credentials','        with:\n          persist-credentials: false\n','').replace('permissions:','persist-credentials: false\n\npermissions:',1),
'floating checkout':mutate('floating checkout',CHECKOUT_ACTION,'actions/checkout@v6'),
'floating setup':mutate('floating setup',SETUP_ACTION,'actions/setup-python@v6'),
'extra action':mutate('extra action','      - name: Set up Python','      - uses: example/unreviewed@v1\n      - name: Set up Python'),
'write permission':mutate('write permission','contents: read','contents: read\n  issues: write'),
'quoted write permission':mutate('quoted write permission','contents: read','contents: read\n  "issues": write'),
'comment-resumed write permission':mutate('comment-resumed write permission','contents: read','contents: read\n# YAML comments do not end the mapping\n  issues: write'),
'duplicate permissions':mutate('duplicate permissions','permissions:\n  contents: read\n','permissions:\n  contents: read\npermissions:\n  issues: write\n'),
'double-quoted duplicate permissions':mutate('double-quoted duplicate permissions','permissions:\n  contents: read\n','permissions:\n  contents: read\n"permissions":\n  issues: write\n'),
'single-quoted duplicate permissions':mutate('single-quoted duplicate permissions','permissions:\n  contents: read\n',"permissions:\n  contents: read\n'permissions':\n  issues: write\n"),
'commented duplicate permissions':mutate('commented duplicate permissions','permissions:\n  contents: read\n','permissions:\n  contents: read\n# top-level comments do not end the mapping\n"permissions":\n  issues: write\n'),
'explicit duplicate permissions':mutate('explicit duplicate permissions','permissions:\n  contents: read\n','permissions:\n  contents: read\n? permissions\n:\n  issues: write\n'),
'flow-style duplicate permissions':mutate('flow-style duplicate permissions','permissions:\n  contents: read\n','permissions:\n  contents: read\n{permissions: {issues: write}}\n'),
'aliased duplicate permissions':mutate('aliased duplicate permissions','permissions:\n  contents: read\n','permissions:\n  contents: read\npermission-name: &permission-name permissions\n*permission-name:\n  issues: write\n'),
'case-variant permissions':mutate('case-variant permissions','permissions:\n  contents: read\n','permissions:\n  contents: read\nPermissions:\n  issues: write\n'),
'missing push':mutate('missing push','  push:\n    branches:\n      - master\n',''),
'missing pull request':mutate('missing pull request','  pull_request:\n',''),
'missing manual dispatch':mutate('missing manual dispatch','  workflow_dispatch:\n',''),
'missing runner':mutate('missing runner','    runs-on: ubuntu-24.04\n',''),
'unbounded job':mutate('unbounded job','    timeout-minutes: 5\n',''),
'fail-fast matrix':mutate('fail-fast matrix','      fail-fast: false','      fail-fast: true'),
'reduced matrix':mutate('reduced matrix','["3.10", "3.12", "3.14"]','["3.12"]'),
'continued failure':mutate('continued failure','    strategy:','    continue-on-error: true\n    strategy:'),
'wrong Python selector':mutate('wrong Python selector','python-version: ${{ matrix.python-version }}','python-version: "3.12"'),
'missing hash enforcement':mutate('missing hash enforcement',' --require-hashes',''),
'direct manifest install':mutate('direct manifest install','-r requirements.lock','-r requirements.txt'),
'floating dependency install':mutate('floating dependency install','python -m pip install --disable-pip-version-check --require-hashes -r requirements.lock','python -m pip install tornado'),
'extra unhashed install':mutate('extra unhashed install','          /usr/bin/make check','          python -m pip install -r requirements.txt\n          /usr/bin/make check'),
'removed dependency audit':mutate('removed dependency audit','          pip-audit -r requirements.lock\n',''),
'weakened gate':mutate('weakened gate','          /usr/bin/make check','          /usr/bin/make lint'),
}
for description,workflow in mutations.items(): reject(description,workflow)
print(f'workflow contract tests passed ({len(mutations)} mutations rejected).')
