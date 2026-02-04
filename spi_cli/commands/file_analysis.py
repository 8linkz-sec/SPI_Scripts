"""TCA-0104: File Analysis - Hash (single + bulk)"""
import logging

from spi_cli.hash_utils import add_hash_arguments, parse_hashes, detect_hash_type
from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("file-analysis", help="TCA-0104: File Analysis - Hash")
    add_hash_arguments(p)
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format file analysis result as compact summary."""
    try:
        sample = data["rl"]["sample"]
        sha256 = sample.get("sha256", "?")
        file_size = sample.get("sample_size", "?")
        # File type is nested in analysis entries
        entries = sample.get("analysis", {}).get("entries", [])
        file_type = "?"
        for entry in entries:
            tc = entry.get("tc_report", {})
            info = tc.get("info", {}).get("file", {})
            if info:
                ft = info.get("file_type", "")
                fs = info.get("file_subtype", "")
                file_type = f"{ft} {fs}".strip() if ft else "?"
                break
        return f"type: {file_type}\nsize: {file_size}\nhash: {sha256}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    hashes = parse_hashes(args)

    if len(hashes) == 1:
        hash_val = hashes[0]
        hash_type = detect_hash_type(hash_val)
        result = client.get(
            f"/api/databrowser/rldata/query/{hash_type}/{hash_val}",
            params={"format": "json"},
        )
        save_result("file-analysis", hash_val[:12], result, args.output,
                    raw=args.raw, summary_fn=format_summary)
    else:
        hash_type = detect_hash_type(hashes[0])
        body = {"rl": {"query": {"hash_type": hash_type, "hashes": hashes}}}
        result = client.post(
            "/api/databrowser/rldata/bulk_query/json",
            json_body=body,
            params={"format": "json"},
        )
        save_result("file-analysis", "bulk", result, args.output,
                    raw=args.raw, summary_fn=format_summary)
