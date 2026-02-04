import logging
import re
import sys

logger = logging.getLogger(__name__)


def detect_hash_type(hash_value):
    """Detect hash type (md5, sha1, sha256) from length."""
    h = hash_value.strip().lower()
    if re.fullmatch(r"[0-9a-f]{32}", h):
        return "md5"
    elif re.fullmatch(r"[0-9a-f]{40}", h):
        return "sha1"
    elif re.fullmatch(r"[0-9a-f]{64}", h):
        return "sha256"
    else:
        return None


def parse_hashes(args):
    """Parse hashes from --hash (single or comma-separated) and/or --hash-file.

    Returns a list of hash strings. Exits on error.
    """
    hashes = []

    if hasattr(args, "hash") and args.hash:
        for h in args.hash.split(","):
            h = h.strip()
            if h:
                hashes.append(h)

    if hasattr(args, "hash_file") and args.hash_file:
        logger.debug("Reading hashes from file: %s", args.hash_file)
        try:
            with open(args.hash_file, "r") as f:
                for line in f:
                    h = line.strip()
                    if h and not h.startswith("#"):
                        hashes.append(h)
        except FileNotFoundError:
            print(f"Error: Hash file not found: {args.hash_file}", file=sys.stderr)
            sys.exit(1)

    if not hashes:
        print("Error: No hashes provided. Use --hash or --hash-file.", file=sys.stderr)
        sys.exit(1)

    logger.debug("Parsed %d hash(es)", len(hashes))
    return hashes


def add_hash_arguments(parser):
    """Add --hash and --hash-file arguments to a subparser."""
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--hash", help="Single hash or comma-separated list of hashes")
    group.add_argument("--hash-file", help="Text file with one hash per line")
