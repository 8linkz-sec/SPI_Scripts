"""TCA-0205: Re-Analyze File (single + bulk)"""
import logging

from spi_cli.hash_utils import add_hash_arguments, parse_hashes, detect_hash_type
from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("reanalyze", help="TCA-0205: Re-Analyze File")
    add_hash_arguments(p)
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format reanalyze result as compact summary."""
    try:
        rl = data.get("rl", {})
        message = rl.get("message") or rl.get("status", "triggered")
        return f"status: {message}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    hashes = parse_hashes(args)

    if len(hashes) == 1:
        hash_val = hashes[0]
        hash_type = detect_hash_type(hash_val)
        result = client.get(
            f"/api/rescan/v1/query/{hash_type}/{hash_val}",
            params={"format": "json"},
        )
        save_result("reanalyze", hash_val[:12], result, args.output,
                    raw=args.raw, summary_fn=format_summary)
    else:
        hash_type = detect_hash_type(hashes[0])
        body = {"rl": {"query": {"hash_type": hash_type, "hashes": hashes}}}
        result = client.post(
            "/api/rescan/v1/bulk_query/json",
            json_body=body,
            params={"format": "json"},
        )
        save_result("reanalyze", "bulk", result, args.output,
                    raw=args.raw, summary_fn=format_summary)
