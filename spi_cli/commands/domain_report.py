"""TCA-0405: Domain Threat Intelligence"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("domain-report", help="TCA-0405: Domain Threat Intelligence")
    p.add_argument("--domain", required=True, help="Domain name to query")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format domain report result as compact summary."""
    try:
        rl = data.get("rl", {})
        report = rl.get("report", {}) or rl.get("domain_report", {})
        domain = rl.get("requested_domain") or report.get("domain", "?")
        classification = report.get("classification", "UNKNOWN")
        top_threats = report.get("top_threats", [])
        threat_count = len(top_threats)
        lines = [f"domain: {domain}", f"classification: {classification}", f"threats: {threat_count}"]
        return "\n".join(lines)
    except (KeyError, TypeError):
        return f"status: ERROR\ndata: {data}"


def execute(args, client):
    body = {"rl": {"query": {"domain": args.domain}}}

    result = client.post(
        "/api/networking/domain/report/v1/query/json",
        json_body=body,
        params={"format": "json"},
    )
    save_result("domain-report", args.domain[:30], result, args.output, raw=args.raw, summary_fn=format_summary)
