import re

CHECKOUT_ACTION = "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10"
SETUP_ACTION = "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405"
CHECKOUT_BLOCK = "\n".join(("      - name: Check out repository", f"        uses: {CHECKOUT_ACTION} # v6.0.3", "        with:", "          persist-credentials: false"))

def top_level_key(line):
    if not line or line[0].isspace() or line.lstrip().startswith("#"): return None
    stripped=line.rstrip()
    if stripped.startswith(("'", '"')):
        quote=stripped[0]
        index=1
        value=[]
        while index < len(stripped):
            char=stripped[index]
            if quote=="'" and char=="'":
                if index+1 < len(stripped) and stripped[index+1]=="'":
                    value.append("'")
                    index+=2
                    continue
                rest=stripped[index+1:].lstrip()
                return "".join(value) if rest.startswith(":") else None
            if quote=='"' and char=='"':
                rest=stripped[index+1:].lstrip()
                return "".join(value) if rest.startswith(":") else None
            if quote=='"' and char=="\\":
                return "<unsupported-escaped-top-level-key>"
            value.append(char)
            index+=1
        return None
    match=re.match(r"^([^:#][^:]*?)\s*:",stripped)
    if not match: return None
    return match.group(1).strip()

def top_level_keys(workflow):
    return [key for key in (top_level_key(line) for line in workflow.splitlines()) if key is not None]

def top_level_mapping_entries(workflow, name):
    lines=workflow.splitlines()
    starts=[index for index,line in enumerate(lines) if top_level_key(line)==name]
    if len(starts)!=1: return None
    entries=[]
    for line in lines[starts[0]+1:]:
        if not line.strip() or line.lstrip().startswith("#"): continue
        if line and not line[0].isspace(): break
        entries.append(line)
    return entries

def validate(workflow):
    errors=[]
    production_install="python -m pip install --disable-pip-version-check --require-hashes -r requirements.lock"
    audit_install="python -m pip install --disable-pip-version-check pip-audit==2.10.0"
    actions=re.findall(r"^[ \t]*(?:-[ \t]*)?uses:[ \t]*(\S+)(?:[ \t]+#.*)?$",workflow,re.MULTILINE)
    if "  push:\n    branches:\n      - master" not in workflow: errors.append("validate pushes to master")
    if len(re.findall(r"^  pull_request:$",workflow,re.MULTILINE))!=1: errors.append("validate pull requests exactly once")
    if len(re.findall(r"^  workflow_dispatch:$",workflow,re.MULTILINE))!=1: errors.append("allow manual dispatch exactly once")
    keys=top_level_keys(workflow)
    if keys.count("<unsupported-escaped-top-level-key>"): errors.append("not use escaped quoted top-level workflow keys")
    if any(key.lower()=="permissions" and key!="permissions" for key in keys): errors.append("use the canonical lowercase permissions key")
    if keys.count("permissions")!=1: errors.append("declare workflow permissions exactly once")
    if top_level_mapping_entries(workflow,"permissions") != ["  contents: read"]: errors.append("use only read-only contents permission")
    if len(re.findall(r"^  cancel-in-progress: true$",workflow,re.MULTILINE))!=1: errors.append("cancel superseded runs exactly once")
    if len(re.findall(r"^    runs-on: ubuntu-24\.04$",workflow,re.MULTILINE))!=2: errors.append("use the fixed Ubuntu runner for both jobs")
    if len(re.findall(r"^    timeout-minutes: 5$",workflow,re.MULTILINE))!=2: errors.append("bound both jobs to five minutes")
    if len(re.findall(r"^      fail-fast: false$",workflow,re.MULTILINE))!=1: errors.append("run every supported Python matrix job")
    if len(re.findall(r'^        python-version: \["3\.10", "3\.12", "3\.14"\]$',workflow,re.MULTILINE))!=1: errors.append("test the exact supported Python matrix")
    if workflow.count(CHECKOUT_BLOCK)!=2: errors.append("use the exact credential-free checkout contract twice")
    if actions != [CHECKOUT_ACTION,SETUP_ACTION,CHECKOUT_ACTION,SETUP_ACTION]: errors.append("use only the reviewed checkout and setup-python actions")
    if workflow.count("persist-credentials:")!=2: errors.append("configure checkout credential persistence exactly twice")
    if len(re.findall(r"^          python-version: \$\{\{ matrix\.python-version \}\}$",workflow,re.MULTILINE))!=1: errors.append("select the matrix Python version exactly once")
    if len(re.findall(r"^          python-version: \"3\.12\"$",workflow,re.MULTILINE))!=1: errors.append("use Python 3.12 for dependency audit")
    if workflow.count(production_install)!=1: errors.append("install the hash-verified production lock exactly once")
    install_lines=[line.strip() for line in workflow.splitlines() if line.strip().startswith("python -m pip install ")]
    if install_lines != [production_install,audit_install]: errors.append("use only the reviewed production and audit installation commands")
    if workflow.count("/usr/bin/make check")!=1: errors.append("run the trusted system Make gate exactly once")
    if workflow.count("pip-audit==2.10.0")!=1 or workflow.count("pip-audit -r requirements.lock")!=1: errors.append("run the pinned resolved dependency audit exactly once")
    if "continue-on-error" in workflow: errors.append("not allow verification failures")
    return errors
