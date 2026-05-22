#!/usr/bin/env python3
"""
Validates governance resources against the Nomos server.
Reads resources/topics.yaml, service-accounts.yaml, rbac.yaml
and calls the Nomos REST API for each entry.

Exit code 0 = all valid
Exit code 1 = one or more violations found
"""
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

SERVER = os.environ.get("NOMOS_SERVER", "http://localhost:8080").rstrip("/")
RESOURCES = Path(__file__).parent.parent / "resources"

errors = []
checked = 0


def call(endpoint: str, payload: dict) -> dict:
    url = f"{SERVER}{endpoint}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def check(label: str, result: dict) -> None:
    global checked
    checked += 1
    if result.get("valid"):
        print(f"  ✅  {label}")
    else:
        print(f"  ❌  {label}")
        for err in result.get("errors", []):
            print(f"       → {err}")
        errors.append(label)


# Topics
topics_file = RESOURCES / "topics.yaml"
if topics_file.exists():
    print("\n── Topics ──────────────────────────────")
    data = yaml.safe_load(topics_file.read_text())
    for name in data.get("topics", []):
        name = name.split("#")[0].strip()
        if name:
            check(name, call("/validate/topic", {"name": name}))

# Service accounts
sa_file = RESOURCES / "service-accounts.yaml"
if sa_file.exists():
    print("\n── Service Accounts ────────────────────")
    data = yaml.safe_load(sa_file.read_text())
    for name in data.get("service_accounts", []):
        name = name.split("#")[0].strip()
        if name:
            check(name, call("/validate/sa", {"name": name}))

# RBAC
rbac_file = RESOURCES / "rbac.yaml"
if rbac_file.exists():
    print("\n── RBAC Bindings ───────────────────────")
    data = yaml.safe_load(rbac_file.read_text())
    for entry in data.get("rbac", []):
        role = entry["role"]
        rtype = entry["resource_type"]
        rname = entry["resource_name"]
        label = f"{role} / {rtype} / {rname}"
        check(label, call("/validate/rbac", {
            "role_name": role,
            "resource_type": rtype,
            "resource_name": rname,
        }))

# Summary
print(f"\n── Result ──────────────────────────────")
print(f"   checked: {checked}  |  failed: {len(errors)}")

if errors:
    print("\nFailed resources:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("All resources passed governance checks.")
