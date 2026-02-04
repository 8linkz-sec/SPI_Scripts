"""TCA-0202: File Upload"""
import hashlib
import logging
import os
import sys

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("upload", help="TCA-0202: Upload a file for analysis")
    p.add_argument("--file", required=True, help="Path to file to upload")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format upload result as compact summary."""
    status = data.get("status", "?")
    sha1 = data.get("sha1", "?")
    return f"status: {status}\nsha1: {sha1}"


def execute(args, client):
    file_path = args.file
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Compute SHA1 for the upload endpoint
    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha1.update(chunk)
    sha1_hex = sha1.hexdigest()
    logger.debug("File SHA1: %s", sha1_hex)

    with open(file_path, "rb") as f:
        url = f"{client.host}/api/spex/upload/{sha1_hex}"
        logger.debug("POST %s", url)
        resp = client.session.post(
            url,
            data=f,
            headers={"Content-Type": "application/octet-stream"},
        )
        resp.raise_for_status()

    result = {"sha1": sha1_hex, "status": "uploaded", "http_status": resp.status_code}
    try:
        result["response"] = resp.json()
    except Exception:
        result["response_text"] = resp.text

    save_result("upload", sha1_hex[:12], result, args.output,
                raw=args.raw, summary_fn=format_summary)
