"""TCA-0106: Dynamic Analysis Report"""
import logging

from spi_cli.hash_utils import detect_hash_type
from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("dynamic-report", help="TCA-0106: Dynamic Analysis Report")
    p.add_argument("--hash", required=True, help="SHA1 hash of file or URL")
    p.add_argument("--latest", action="store_true", help="Get latest report only")
    p.add_argument("--analysis-id", help="Specific analysis ID")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format dynamic analysis report as compact summary."""
    try:
        report = data["rl"]["report"]
        classification = report.get("classification", "?")
        risk_score = report.get("risk_score", "?")
        platforms = report.get("platforms", [])
        platform_str = ", ".join(platforms) if platforms else "?"
        return f"classification: {classification}\nrisk_score: {risk_score}\nplatform: {platform_str}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    hash_val = args.hash.strip()
    hash_type = detect_hash_type(hash_val)

    if args.latest:
        path = f"/api/dynamic/analysis/report/v1/query/{hash_type}/{hash_val}/latest"
    elif args.analysis_id:
        path = f"/api/dynamic/analysis/report/v1/query/{hash_type}/{hash_val}/{args.analysis_id}"
    else:
        path = f"/api/dynamic/analysis/report/v1/query/{hash_type}/{hash_val}"

    result = client.get(path, params={"format": "json"})
    save_result("dynamic-report", hash_val[:12], result, args.output,
                raw=args.raw, summary_fn=format_summary)
