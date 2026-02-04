"""TCA-0401: URI to Hash Search"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("uri-index", help="TCA-0401: URI to Hash Search")
    p.add_argument("--uri", required=True, help="URL, IP, domain, or email")
    p.add_argument("--classification", choices=["malicious", "suspicious", "known", "unknown"],
                   help="Filter by classification")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format URI index result as compact summary."""
    try:
        entries = data.get("rl", {}).get("uri_index", {}).get("sha1_list", [])
        count = len(entries)
        return f"associated_files: {count}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    import hashlib
    # URI index uses SHA1 of the URI
    uri_sha1 = hashlib.sha1(args.uri.encode()).hexdigest()
    params = {"format": "json"}
    if args.classification:
        params["classification"] = args.classification

    result = client.get(
        f"/api/uri_index/v1/query/{uri_sha1}",
        params=params,
    )
    save_result("uri-index", args.uri[:30], result, args.output,
                raw=args.raw, summary_fn=format_summary)
