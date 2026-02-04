import argparse
import logging
import sys

from spi_cli.config import load_config
from spi_cli.client import SPIClient
from spi_cli.commands import (
    file_reputation,
    av_scanners,
    file_analysis,
    dynamic_report,
    file_download,
    file_upload,
    reanalyze,
    dynamic_analysis,
    rha_similarity,
    imphash,
    advanced_search,
    uri_index,
    uri_stats,
    url_report,
    analyze_url,
    domain_report,
    ip_report,
    net_reputation,
    net_override,
    usage,
)

# All command modules in registration order
COMMAND_MODULES = [
    file_reputation,
    av_scanners,
    file_analysis,
    dynamic_report,
    file_download,
    file_upload,
    reanalyze,
    dynamic_analysis,
    rha_similarity,
    imphash,
    advanced_search,
    uri_index,
    uri_stats,
    url_report,
    analyze_url,
    domain_report,
    ip_report,
    net_reputation,
    net_override,
    usage,
]

# Subcommand name -> module mapping
COMMAND_MAP = {
    "reputation": file_reputation,
    "av-scanners": av_scanners,
    "file-analysis": file_analysis,
    "dynamic-report": dynamic_report,
    "download": file_download,
    "upload": file_upload,
    "reanalyze": reanalyze,
    "dynamic-analysis": dynamic_analysis,
    "rha-similarity": rha_similarity,
    "imphash": imphash,
    "search": advanced_search,
    "uri-index": uri_index,
    "uri-stats": uri_stats,
    "url-report": url_report,
    "analyze-url": analyze_url,
    "domain-report": domain_report,
    "ip-report": ip_report,
    "net-reputation": net_reputation,
    "net-override": net_override,
    "usage": usage,
}


def main():
    parser = argparse.ArgumentParser(
        prog="spi",
        description="ReversingLabs Spectra Intelligence CLI Tool",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", help="Path to config.ini (default: config.ini in project root)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register all commands
    for module in COMMAND_MODULES:
        module.register(subparsers)

    args = parser.parse_args()

    # Setup logging
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    else:
        logging.basicConfig(level=logging.WARNING, format=log_format)

    logger = logging.getLogger("spi_cli")

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load config and create client
    cfg = load_config(args.config)
    client = SPIClient(cfg["host"], cfg["username"], cfg["password"])
    logger.debug("Client initialized for %s", cfg["host"])

    # Execute the command
    module = COMMAND_MAP.get(args.command)
    if not module:
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        sys.exit(1)

    try:
        module.execute(args, client)
    except Exception as e:
        logger.debug("Exception details:", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
