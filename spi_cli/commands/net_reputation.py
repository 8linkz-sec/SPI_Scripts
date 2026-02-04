"""TCA-0407: Network Reputation"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("net-reputation", help="TCA-0407: Network Reputation")
    p.add_argument("--network-location", required=True,
                   help="URL, domain, or IP address to query")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format network reputation result as compact summary."""
    try:
        rl = data.get("rl", {})
        entries = rl.get("entries", {})
        # entries.item could be dict (single) or list (multiple)
        items = entries.get("item", [])
        if not isinstance(items, list):
            items = [items] if items else []
        if items:
            entry = items[0]
            location = entry.get("requested_network_location", "?")
            classification = entry.get("classification", "UNKNOWN")
            threat_level = entry.get("threat_level", "?")
            return f"location: {location}\nclassification: {classification}\nthreat_level: {threat_level}"
        return "status: NO_RESULTS"
    except (KeyError, TypeError):
        return f"status: ERROR\ndata: {data}"


def execute(args, client):
    body = {"rl": {"query": {"network_locations": [{"network_location": args.network_location}]}}}

    result = client.post(
        "/api/networking/reputation/v1/query/json",
        json_body=body,
        params={"format": "json"},
    )
    save_result("net-reputation", args.network_location[:30], result, args.output, raw=args.raw, summary_fn=format_summary)
