#!/usr/bin/env python3
"""One-time H5 static-host provisioning for the current Hermes server.

This installer-only helper never runs in a learner conversation. It provisions a
narrow Nginx site on the same machine as Hermes and stores only the two runtime
variables the H5 publisher needs. If the host cannot safely self-provision, it
fails closed; the learning plugin then keeps teaching in chat instead of sending
an attachment or inventing a URL.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

PUBLIC_ROOT = Path("/var/www/feynman-h5")
NGINX_CONF = Path("/etc/nginx/conf.d/feynman-h5.conf")


def _public_ipv4() -> str:
    for endpoint in ("https://api.ipify.org", "https://ifconfig.me/ip"):
        try:
            with urllib.request.urlopen(endpoint, timeout=5) as response:
                value = response.read().decode("ascii", "ignore").strip()
            if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", value):
                return value
        except Exception:
            continue
    raise RuntimeError("public_ip_unavailable")


def _write_env(env_path: Path, base_url: str) -> None:
    existing = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    kept = [line for line in existing.splitlines() if not line.startswith("FEYNMAN_H5_PUBLIC_DIR=") and not line.startswith("FEYNMAN_H5_PUBLIC_BASE_URL=") and not line.startswith("FEYNMAN_H5_VERIFY_BASE_URL=")]
    kept.extend([
        f"FEYNMAN_H5_PUBLIC_DIR={PUBLIC_ROOT}",
        f"FEYNMAN_H5_PUBLIC_BASE_URL={base_url}",
        "FEYNMAN_H5_VERIFY_BASE_URL=http://127.0.0.1/feynman-h5",
    ])
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    home = Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes").expanduser()
    existing_base = os.environ.get("FEYNMAN_H5_PUBLIC_BASE_URL", "").strip().rstrip("/")
    existing_dir = os.environ.get("FEYNMAN_H5_PUBLIC_DIR", "").strip()
    if existing_base and existing_dir:
        print(f"ready {existing_base}")
        return 0
    if os.geteuid() != 0 or not shutil.which("nginx"):
        print("unavailable")
        return 2
    public_ip = _public_ipv4()
    base_url = f"http://{public_ip}/feynman-h5"
    conf = f'''server {{
    listen 80;
    server_name {public_ip} 127.0.0.1;
    location = /feynman-h5 {{ return 301 /feynman-h5/; }}
    location ^~ /feynman-h5/ {{
        alias {PUBLIC_ROOT}/;
        index index.html;
        autoindex off;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer" always;
        add_header Content-Security-Policy "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'none'" always;
    }}
}}
'''
    if args.dry_run:
        print(f"would-provision {base_url}")
        return 0
    PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)
    NGINX_CONF.write_text(conf, encoding="utf-8")
    try:
        subprocess.run(["nginx", "-t"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["systemctl", "reload", "nginx"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        NGINX_CONF.unlink(missing_ok=True)
        raise
    _write_env(home / ".env", base_url)
    print(f"ready {base_url}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("unavailable")
        raise SystemExit(2)
