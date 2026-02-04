"""TCA-0402: URI Statistics"""
import hashlib
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("uri-stats", help="TCA-0402: URI Statistics")
    p.add_argument("--uri", required=True, help="URL, IP, domain, or email")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format URI statistics as compact summary."""
    try:
        stats = data.get("rl", {}).get("uri_state", {}).get("counters", {})
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        known = stats.get("known", 0)
        return f"malicious: {malicious}\nsuspicious: {suspicious}\nknown: {known}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    # The API expects SHA1 of the URI
    uri_sha1 = hashlib.sha1(args.uri.encode("utf-8")).hexdigest()
    logger.debug("URI SHA1: %s (from %s)", uri_sha1, args.uri)

    result = client.get(
        f"/api/uri/statistics/uri_state/sha1/{uri_sha1}",
        params={"format": "json"},
    )
    save_result("uri-stats", args.uri[:30], result, args.output,
                raw=args.raw, summary_fn=format_summary)
