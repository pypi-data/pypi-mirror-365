from typing import List, Dict, Any
from urllib.parse import urlparse, urlunparse, urlencode

import requests
from fastmcp.exceptions import ToolError

from meiro_mcp.auth import get_auth_token, get_meiro_config
from meiro_mcp.mcp_server import mcp


@mcp.tool()
async def list_events() -> List[Dict[str, Any]]:
    """
    List all available events from Meiro CDP.

    Each event dictionary will contain:
        - id: Event identifier
        - name: Human-readable event name
        - description: Optional description (defaults to "No description provided.")
        - examples: List of example payloads associated with the event

    Events that are hidden/disabled according to the backend flags are still
    returned because the upstream API does not expose explicit "disabled"
    flags; we rely on the default API filters (`show_hidden`, `cascade_is_hidden`)
    to decide which events to expose.

    Returns:
        A list of event dictionaries.
    """

    token = get_auth_token()
    config = get_meiro_config()
    domain = config["domain"]

    parsed_domain = urlparse(domain)

    limit = 100
    offset = 0
    all_events: List[Dict[str, Any]] = []

    while True:
        query_params = {
            "offset": offset,
            "limit": limit,
            "order_by": "name",
            "order_dir": "ASC",
            "show_hidden": 1,
            "cascade_is_hidden": 1,
            "load_full_structure": 1,
        }

        events_url = urlunparse(
            (
                parsed_domain.scheme,
                parsed_domain.netloc,
                "api/events",
                "",
                urlencode(query_params),
                "",
            )
        )

        headers = {
            "accept": "application/json",
            "X-Access-Token": token,
        }

        response = requests.get(events_url, headers=headers)
        response.raise_for_status()

        try:
            data = response.json()
            events = data.get("events", [])
        except (KeyError, requests.exceptions.JSONDecodeError) as e:
            raise ToolError(f"Failed to parse events from response: {e}")

        all_events.extend(events)

        if len(events) < limit:
            break
        offset += limit

    processed_events: List[Dict[str, Any]] = []
    for event in all_events:
        processed_events.append(
            {
                "id": event.get("id"),
                "name": event.get("name"),
                "description": event.get("description", "No description provided."),
                "examples": event.get("examples", []),
            }
        )

    return processed_events 