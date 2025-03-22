"""Utilities."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from collections.abc import Sequence


DEFAULT_MODEL_ENCODING = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 4000


def get_total_tokens_from_string(string: str, model: str = DEFAULT_MODEL_ENCODING) -> int:
    """Get total amount of tokens from string using the specified encoding."""
    import tokonomics

    return tokonomics.count_tokens(string, model=model)


def get_max_items_from_list(
    data: Sequence[dict], max_tokens: int = DEFAULT_MAX_TOKENS
) -> list[dict[str, str]]:
    """Get max items from list of items based on defined max tokens."""
    result = []
    current_tokens = 0
    for item in data:
        item_str = json.dumps(item)
        new_total_tokens = current_tokens + get_total_tokens_from_string(item_str)
        if new_total_tokens > max_tokens:
            break
        result.append(item)
        current_tokens = new_total_tokens
    return result


def save_results_to_file(results: dict):
    """Save results to a file with timestamp in filename.

    Args:
        results: Processed results to save
    """
    import datetime

    import anyenv
    import upath

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = upath.UPath(f"search_results_{timestamp}.json")

    try:
        with filename.open("w", encoding="utf-8") as file:
            text = anyenv.dump_json(results, indent=True)
            file.write(text)
        logger.info("Results saved to %r", filename)
    except OSError as e:
        error_msg = f"Failed to save results to file: {e}"
        logger.exception(error_msg)
