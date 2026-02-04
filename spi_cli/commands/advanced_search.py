"""TCA-0320: Advanced Search"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("search", help="TCA-0320: Advanced Search")
    p.add_argument("--query", required=True, help="Search expression")
    p.add_argument("--limit", type=int, default=100, help="Results per page (default: 100)")
    p.add_argument("--page", help="Next page hash for pagination")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format search result as compact summary."""
    try:
        rl = data.get("rl", {})
        web_api = rl.get("web_search_api", {})
        total = web_api.get("total_count", "?")
        sample_count = web_api.get("sample_count", "?")
        entries = web_api.get("entries", {})
        # entries could be dict with 'item' key or list
        items = entries.get("item", []) if isinstance(entries, dict) else entries
        if not isinstance(items, list):
            items = [items] if items else []
        return f"total: {total}\nsamples: {sample_count}\nreturned: {len(items)}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    body = {"query": args.query, "page_size": args.limit}
    if args.page:
        body["next_page_hash"] = args.page

    # Client handles XML response automatically
    result = client.post("/api/search/v1/query", json_body=body)

    save_result("search", "query", result, args.output,
                raw=args.raw, summary_fn=format_summary)
