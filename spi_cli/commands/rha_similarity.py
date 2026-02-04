"""TCA-0301: RHA Functional Similarity"""
import logging

from spi_cli.output import save_result

logger = logging.getLogger(__name__)


def register(subparsers):
    p = subparsers.add_parser("rha-similarity", help="TCA-0301: RHA Functional Similarity")
    p.add_argument("--hash", required=True, help="SHA1 hash")
    p.add_argument("--type", default="pe01", choices=["pe01", "pe02", "elf01", "macho01"],
                   help="RHA1 type: pe01 (25%% PE), pe02 (50%% PE), elf01, macho01")
    p.add_argument("--extended", action="store_true", help="Extended metadata")
    p.add_argument("--classification", choices=["malicious", "suspicious", "known", "unknown"],
                   help="Filter by classification")
    p.add_argument("--raw", action="store_true", help="Output full JSON instead of summary")
    p.add_argument("-o", "--output", help="Output file path")


def format_summary(data):
    """Format RHA similarity result as compact summary."""
    try:
        entries = data.get("rl", {}).get("group_by_rha1", {}).get("entries", [])
        count = len(entries)
        return f"similar_samples: {count}"
    except (KeyError, TypeError):
        return f"result: {data}"


def execute(args, client):
    hash_val = args.hash.strip()
    params = {"format": "json"}
    if args.extended:
        params["extended"] = "true"
    if args.classification:
        params["classification"] = args.classification

    # First page (no next_page_sha1)
    result = client.get(
        f"/api/group_by_rha1/v1/query/{args.type}/{hash_val}",
        params=params,
    )
    save_result("rha-similarity", hash_val[:12], result, args.output,
                raw=args.raw, summary_fn=format_summary)
