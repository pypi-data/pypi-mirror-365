import os
import shutil
import subprocess
import time
import requests
import json
from pathlib import Path
from mm.validator import validate_meta, validate_meta_consistency

TEMPLATE_DIR = Path(__file__).parent.parent / "template"


def init_project(name: str):
    dest = Path(name)
    if dest.exists():
        raise FileExistsError(f"Project directory '{name}' already exists.")

    shutil.copytree(TEMPLATE_DIR, dest)
    print(f"✅ Project '{name}' created at {dest.resolve()}")


def validate_project():
    meta_path = Path("mms/meta.json")
    validate_meta(meta_path)
    print("✅ meta.json validated.")


def push_project():
    validate_project()

    print("🚀 Starting mms service via run/start.py ...")
    process = subprocess.Popen(["python", "run/start.py"])

    time.sleep(3)
    try:
        resp = requests.get("http://localhost:8000/meta", timeout=5)
        resp.raise_for_status()
        remote_meta = resp.json()

        with open("mms/meta.json") as f:
            local_meta = json.load(f)

        validate_meta_consistency(local_meta, remote_meta)
        print("✅ /meta response matches mms/meta.json")

    except Exception as e:
        print("❌ Error verifying /meta endpoint:", e)
    finally:
        process.terminate()
