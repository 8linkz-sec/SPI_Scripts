"""TCA-0201: File Download"""
import logging
import os

from spi_cli.hash_utils import detect_hash_type

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("download", help="TCA-0201: Download a sample")
    p.add_argument("--hash", required=True, help="Hash of file to download")
    p.add_argument("-o", "--output", required=True, help="Output file path for the binary")


def execute(args, client):
    hash_val = args.hash.strip()
    hash_type = detect_hash_type(hash_val)

    resp = client.get_raw(f"/api/spex/download/v2/query/{hash_type}/{hash_val}")

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    size = os.path.getsize(args.output)
    logger.debug("Downloaded %d bytes to %s", size, args.output)
    print(f"status: downloaded\nfile: {args.output}\nsize: {size}")
