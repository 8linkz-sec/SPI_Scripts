"""TCA-0103: Historic Multi-AV Scan Records (single + bulk)"""
import logging

from spi_cli.hash_utils import add_hash_arguments, parse_hashes, detect_hash_type
from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("av-scanners", help="TCA-0103: Historic Multi-AV Scan Records")
    add_hash_arguments(p)
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format AV scanner result as compact summary."""
    try:
        xref_list = data["rl"]["sample"]["xref"]
        xref = xref_list[0] if xref_list else {}
        scanner_count = xref.get("scanner_count", 0)
        scanner_match = xref.get("scanner_match", 0)
        results = xref.get("results", [])
        detections = [f"{r['scanner']}: {r['result']}" for r in results if r.get("result")][:3]
        det_str = ", ".join(detections) if detections else "none"
        return f"detections: {scanner_match}/{scanner_count}\ntop: {det_str}"
    except (KeyError, TypeError, IndexError):
        return f"result: {data}"


def execute(args, client):
    hashes = parse_hashes(args)

    if len(hashes) == 1:
        hash_val = hashes[0]
        hash_type = detect_hash_type(hash_val)
        result = client.get(
            f"/api/xref/v2/query/{hash_type}/{hash_val}",
            params={"format": "json"},
        )
        save_result("av-scanners", hash_val[:12], result, args.output,
                    raw=args.raw, summary_fn=format_summary)
    else:
        hash_type = detect_hash_type(hashes[0])
        body = {"rl": {"query": {"hash_type": hash_type, "hashes": hashes}}}
        result = client.post(
            "/api/xref/v2/bulk_query/json",
            json_body=body,
            params={"format": "json"},
        )
        save_result("av-scanners", "bulk", result, args.output,
                    raw=args.raw, summary_fn=format_summary)
