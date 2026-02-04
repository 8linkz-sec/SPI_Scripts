import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def save_result(command, identifier, data, output_path=None, raw=False, summary_fn=None):
    """Save API result to a JSON file and print to terminal.

    Args:
        command: The subcommand name (e.g. 'reputation')
        identifier: Short identifier for the query (e.g. hash prefix, 'bulk', domain)
        data: The data to serialize (dict, list, or Response-like with .json())
        output_path: Optional explicit output path. If None, auto-generates in output/
        raw: If True, print full JSON. If False, use summary_fn for compact output.
        summary_fn: Function that takes data and returns a compact string summary.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if output_path:
        path = output_path
    else:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)

        safe_id = str(identifier).replace("/", "_").replace(":", "_")[:50]
        filename = f"{command}_{safe_id}_{timestamp}.json"
        path = os.path.join(output_dir, filename)

    # Handle SDK Response objects that have .json() or .text
    if hasattr(data, "json"):
        try:
            data = data.json()
        except Exception:
            data = {"raw": data.text if hasattr(data, "text") else str(data)}
    elif hasattr(data, "text") and not isinstance(data, (dict, list)):
        try:
            data = json.loads(data.text)
        except (json.JSONDecodeError, AttributeError):
            data = {"raw": str(data)}

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    # Print result to terminal
    if raw or summary_fn is None:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        print(summary_fn(data))

    # Log file path only in debug mode
    logger.debug("Result saved to: %s (%d bytes)", path, os.path.getsize(path))

    return path
