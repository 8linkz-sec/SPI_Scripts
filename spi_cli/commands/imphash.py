"""TCA-0302: ImpHash Similarity"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("imphash", help="TCA-0302: ImpHash Similarity")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--imphash", help="ImpHash value to search")
    group.add_argument("--sample-hash", help="Sample hash to find its ImpHash similarity")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format ImpHash result as compact summary."""
    try:
        entries = data.get("rl", {}).get("imphash_index", {}).get("entries", [])
        count = len(entries)
        return f"similar_samples: {count}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    if args.imphash:
        result = client.get(
            f"/api/imphash_index/v1/query/{args.imphash}",
            params={"format": "json"},
        )
        save_result("imphash", args.imphash[:12], result, args.output,
                    raw=args.raw, summary_fn=format_summary)
    else:
        result = client.get(
            f"/api/imphash_index/v1/query/sample/{args.sample_hash}",
            params={"format": "json"},
        )
        save_result("imphash", args.sample_hash[:12], result, args.output,
                    raw=args.raw, summary_fn=format_summary)
