"""TCA-9999: Customer Usage"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("usage", help="TCA-9999: Customer Usage")
    p.add_argument("--type", default="daily", choices=["daily", "monthly"],
                   help="Usage type (default: daily)")
    p.add_argument("--company", action="store_true", help="Show company-wide usage")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format usage result as compact summary."""
    try:
        rl = data.get("rl", {})
        date = rl.get("date", "?")
        usage_report = rl.get("usage_report", [])
        total = sum(item.get("number_of_queries", 0) for item in usage_report)
        lines = [f"date: {date}", f"total_queries: {total}"]
        for item in usage_report[:5]:
            product = item.get("product", "?")
            queries = item.get("number_of_queries", 0)
            lines.append(f"  {product}: {queries}")
        return "\n".join(lines)
    except (KeyError, TypeError):
        return f"status: ERROR\ndata: {data}"


def execute(args, client):
    if args.company:
        path = f"/api/customer_usage/v1/usage/company/{args.type}"
    else:
        path = f"/api/customer_usage/v1/usage/{args.type}"

    result = client.get(path, params={"format": "json"})
    save_result("usage", args.type, result, args.output, raw=args.raw, summary_fn=format_summary)
