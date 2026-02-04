"""TCA-0406: IP Threat Intelligence"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("ip-report", help="TCA-0406: IP Threat Intelligence")
    p.add_argument("--ip", required=True, help="IP address to query")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format IP report result as compact summary."""
    try:
        rl = data.get("rl", {})
        report = rl.get("report", {}) or rl.get("ip_report", {})
        ip = rl.get("requested_ip") or report.get("ip", "?")
        classification = report.get("classification", "UNKNOWN")
        top_threats = report.get("top_threats", [])
        threat_count = len(top_threats)
        lines = [f"ip: {ip}", f"classification: {classification}", f"threats: {threat_count}"]
        return "\n".join(lines)
    except (KeyError, TypeError):
        return f"status: ERROR\ndata: {data}"


def execute(args, client):
    body = {"rl": {"query": {"ip": args.ip}}}

    result = client.post(
        "/api/networking/ip/report/v1/query/json",
        json_body=body,
        params={"format": "json"},
    )
    save_result("ip-report", args.ip, result, args.output, raw=args.raw, summary_fn=format_summary)
