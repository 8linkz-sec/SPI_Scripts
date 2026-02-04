"""TCA-0403: URL Threat Intelligence"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("url-report", help="TCA-0403: URL Threat Intelligence")
    p.add_argument("--url", required=True, help="URL to query")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format URL report as compact summary."""
    try:
        rl = data.get("rl", {})
        url = rl.get("requested_url", "?")
        analysis = rl.get("analysis", {})
        history = analysis.get("analysis_history", {})
        items = history.get("item", [])
        if not isinstance(items, list):
            items = [items] if items else []
        count = len(items)
        latest = items[0] if items else {}
        status = latest.get("availability_status", "?")
        return f"url: {url}\nstatus: {status}\nanalyses: {count}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    body = {"rl": {"query": {"url": args.url}}}

    result = client.post(
        "/api/networking/url/v1/report/query/json",
        json_body=body,
        params={"format": "json"},
    )
    save_result("url-report", args.url[:30], result, args.output,
                raw=args.raw, summary_fn=format_summary)
