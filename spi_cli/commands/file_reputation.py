"""TCA-0101: File Reputation (single + bulk)"""
import logging

from spi_cli.hash_utils import add_hash_arguments, parse_hashes, detect_hash_type
from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("reputation", help="TCA-0101: File Reputation")
    add_hash_arguments(p)
    p.add_argument("--extended", action="store_true", help="Include extended metadata")
    p.add_argument("--show-hashes", action="store_true", help="Include all hash types in response")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format reputation result as compact summary."""
    try:
        mp = data["rl"]["malware_presence"]
        status = mp.get("status", "UNKNOWN")
        query = mp.get("query_hash", {})
        hash_val = query.get("sha256") or query.get("sha1") or query.get("md5") or "?"
        return f"status: {status}\nhash: {hash_val}"
    except (KeyError, TypeError):
        return f"status: ERROR\ndata: {data}"


def execute(args, client):
    hashes = parse_hashes(args)

    if len(hashes) == 1:
        hash_val = hashes[0]
        hash_type = detect_hash_type(hash_val)
        logger.debug("Single query: %s (%s)", hash_val, hash_type)

        params = {"format": "json"}
        if args.extended:
            params["extended"] = "true"
        if args.show_hashes:
            params["show_hashes"] = "true"

        result = client.get(
            f"/api/databrowser/malware_presence/query/{hash_type}/{hash_val}",
            params=params,
        )
        save_result("reputation", hash_val[:12], result, args.output,
                    raw=args.raw, summary_fn=format_summary)
    else:
        # Bulk query via POST
        hash_type = detect_hash_type(hashes[0])
        logger.debug("Bulk query: %d hashes (%s)", len(hashes), hash_type)

        body = {"rl": {"query": {"hash_type": hash_type, "hashes": hashes}}}
        params = {"format": "json"}
        if args.extended:
            params["extended"] = "true"
        if args.show_hashes:
            params["show_hashes"] = "true"

        result = client.post(
            "/api/databrowser/malware_presence/bulk_query/json",
            json_body=body,
            params=params,
        )
        save_result("reputation", "bulk", result, args.output,
                    raw=args.raw, summary_fn=format_summary)
