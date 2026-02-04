"""TCA-0404: Analyze URL"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("analyze-url", help="TCA-0404: Submit URL for analysis")
    p.add_argument("--url", required=True, help="URL to submit for analysis")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format URL analysis result as compact summary."""
    try:
        rl = data.get("rl", {})
        analysis = rl.get("analysis", {}) or rl.get("url_analysis", {})
        url = rl.get("requested_url", "?")
        status = analysis.get("status", "SUBMITTED")
        return f"url: {url}\nstatus: {status}"
    except (KeyError, TypeError):
        return f"status: ERROR\ndata: {data}"


def execute(args, client):
    body = {"rl": {"query": {"url": args.url}}}

    result = client.post(
        "/api/networking/url/v1/analyze/query/json",
        json_body=body,
        params={"format": "json"},
    )
    save_result("analyze-url", "url", result, args.output, raw=args.raw, summary_fn=format_summary)
