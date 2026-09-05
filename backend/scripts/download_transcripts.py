"""Download a transcript archive into data/transcripts. Usage: python scripts/download_transcripts.py URL"""
import sys
from pathlib import Path
import httpx

url = sys.argv[1] if len(sys.argv) > 1 else ""
if not url:
    raise SystemExit("Pass the raw archive URL from the assignment transcript repository")
target = Path(__file__).parents[2] / "data" / "transcripts" / "archive.zip"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(httpx.get(url, timeout=60).content)
print(f"Downloaded {target}")
