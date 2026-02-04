"""TCA-0408: Network Reputation User Override"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("net-override", help="TCA-0408: Network Reputation Override")
    p.add_argument("--location", required=True, help="Network location (URL, domain, or IP)")
    p.add_argument("--type", required=True, choices=["url", "domain", "ipv4"],
                   help="Type of network location")
    p.add_argument("--classification", required=True,
                   choices=["malicious", "suspicious", "known"],
                   help="Override classification")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format network override result as compact summary."""
    try:
        rl = data.get("rl", {})
        entries = rl.get("entries", [])
        if entries:
            entry = entries[0]
            location = entry.get("network_location", "?")
            classification = entry.get("classification", "?")
            return f"location: {location}\nclassification: {classification}\nstatus: OVERRIDE_APPLIED"
        return "status: NO_RESULTS"
    except (KeyError, TypeError):
        return f"status: ERROR\ndata: {data}"


def execute(args, client):
    body = {
        "rl": {
            "query": {
                "user_override": {
                    "override_network_locations": [{
                        "network_location": args.location,
                        "type": args.type,
                        "classification": args.classification,
                    }]
                }
            }
        }
    }

    result = client.post(
        "/api/networking/user_override/v1/query/json",
        json_body=body,
        params={"format": "json"},
    )
    save_result("net-override", args.location[:30], result, args.output, raw=args.raw, summary_fn=format_summary)
