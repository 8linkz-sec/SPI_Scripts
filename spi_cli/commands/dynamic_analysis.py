"""TCA-0207: Dynamic Analysis (submit for sandbox detonation)"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("dynamic-analysis", help="TCA-0207: Submit file/URL for dynamic analysis")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--hash", help="SHA1 hash of file to detonate")
    group.add_argument("--url", help="URL to detonate")
    p.add_argument("--platform", default="windows10", choices=["windows7", "windows10"],
                   help="Sandbox platform (default: windows10)")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format dynamic analysis result as compact summary."""
    try:
        rl = data.get("rl", {})
        status = rl.get("status", "submitted")
        analysis_id = rl.get("analysis_id", "?")
        return f"status: {status}\nanalysis_id: {analysis_id}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    if args.hash:
        body = {"rl": {"sha1": args.hash.strip(), "platform": args.platform}}
        identifier = args.hash[:12]
    else:
        body = {"rl": {"url": args.url, "platform": args.platform}}
        identifier = "url"

    result = client.post(
        "/api/dynamic/analysis/analyze/v1/query/json",
        json_body=body,
        params={"format": "json"},
    )
    save_result("dynamic-analysis", identifier, result, args.output,
                raw=args.raw, summary_fn=format_summary)
