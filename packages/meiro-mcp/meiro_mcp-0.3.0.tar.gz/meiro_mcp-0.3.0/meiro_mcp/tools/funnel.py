# NOTE: Removed `from __future__ import annotations` to avoid deferred string
# evaluation issues in type hints when FastMCP/Pydantic inspects the function
# signatures. Replaced legacy typing generics (List, Dict) with builtin
# generics (list, dict) that are always available at runtime.

import datetime as _dt
import json
from typing import Any, Optional
from urllib.parse import urlparse, urlunparse, urlencode

import socketio
import requests
from fastmcp.exceptions import ToolError

from meiro_mcp.auth import get_auth_token, get_meiro_config
from meiro_mcp.mcp_server import mcp


@mcp.tool()
async def list_funnels() -> list[dict[str, Any]]:
    """
    List all funnels grouped by their funnel groups in Meiro CDP.

    Each returned item represents a funnel group and contains:
        - id: Funnel group ID
        - name: Funnel group name
        - funnels: A list of funnel definitions within the group where each
          funnel dictionary contains:
            * id – Funnel ID
            * name – Funnel name
            * description – Funnel description or a fallback value
            * steps – Ordered list of step dictionaries (title + attribute_id)

    Notes
    -----
    * Disabled / deleted funnel groups are skipped.
    * Only charts whose type is "FUNNEL" are included when iterating through
      charts of a funnel group.
    """

    token = get_auth_token()
    config = get_meiro_config()
    domain = config["domain"]
    parsed_domain = urlparse(domain)

    # First fetch the list of funnel groups
    funnel_groups_url = urlunparse(
        (parsed_domain.scheme, parsed_domain.netloc, "api/funnel_groups", "", "", "")
    )
    headers = {"accept": "application/json", "X-Access-Token": token}

    try:
        response = requests.get(funnel_groups_url, headers=headers)
        response.raise_for_status()
        funnel_groups_data = response.json()
        funnel_groups = funnel_groups_data.get("funnel_groups", [])
    except (requests.exceptions.HTTPError, requests.exceptions.JSONDecodeError) as e:
        raise ToolError(f"Failed to fetch funnel groups: {e}")

    results: list[dict[str, Any]] = []

    for group in funnel_groups:
        if group.get("deleted") or group.get("disabled"):
            continue

        group_id = group.get("id")
        group_name = group.get("name")

        group_entry: dict[str, Any] = {"id": group_id, "name": group_name, "funnels": []}

        # Fetch funnels inside the group
        funnels_url = urlunparse(
            (
                parsed_domain.scheme,
                parsed_domain.netloc,
                f"api/funnel_groups/{group_id}/funnels",
                "",
                "",
                "",
            )
        )
        try:
            response = requests.get(funnels_url, headers=headers)
            response.raise_for_status()
            funnels_data = response.json()
            funnels = funnels_data.get("charts", [])
        except (requests.exceptions.HTTPError, requests.exceptions.JSONDecodeError) as e:
            group_entry["error"] = f"Could not retrieve funnels for this group: {e}"
            results.append(group_entry)
            continue

        for funnel in funnels:
            if funnel.get("type") != "FUNNEL":
                continue

            chart_attributes = funnel.get("definition", {}).get("chart_attributes", [])
            steps: list[dict[str, str]] = []
            for attr in chart_attributes:
                attr_id = attr.get("attribute_id")
                title = attr.get("data_dimension_title")
                if attr_id and title:
                    steps.append({"title": title, "attribute_id": attr_id})

            group_entry["funnels"].append(
                {
                    "id": funnel.get("id"),
                    "name": funnel.get("name"),
                    "description": funnel.get("description") or "No description provided.",
                    "steps": steps,
                }
            )

        results.append(group_entry)

    return results


@mcp.tool()
async def get_funnel_group_data(
    funnel_group_id: str,
    start_date: str,
    end_date: str,
    segment_id: Optional[str] = None,
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Retrieve funnel counts for a specific funnel group over a date range.

    The data is fetched via the Meiro CDP WebSocket endpoint (`funnels_counts`).

    Parameters
    ----------
    funnel_group_id : str
        The ID of the funnel group.
    start_date : str
        Date range start in *YYYY-MM-DD* format (UTC).
    end_date : str
        Date range end in *YYYY-MM-DD* format (UTC).
    segment_id : str | None, optional
        If provided, the counts will be filtered by the given segment.

    Returns
    -------
    list[dict]
        A list of dictionaries, as provided by the *funnels_counts_response*
        message. If no data is available an empty list will be returned. In case
        of an error a dictionary with a single key `error` is returned.
    """

    # Validate date format
    try:
        _dt.datetime.strptime(start_date, "%Y-%m-%d")
        _dt.datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Please use 'YYYY-MM-DD'."}

    token = get_auth_token()
    config = get_meiro_config()
    domain = config["domain"]
    parsed_domain = urlparse(domain)

    ws_domain = parsed_domain.netloc
    ws_url = f"wss://{ws_domain}"

    all_funnel_data: list[dict[str, Any]] = []
    ws_status_msg = ""

    sio = socketio.Client(logger=False, engineio_logger=False)

    @sio.on("funnels_counts_response")
    def on_funnel_data(data: dict[str, Any]):  # noqa: D401
        """Handle funnel counts response and collect data."""
        all_funnel_data.append(data)

    try:
        # Establish WebSocket connection
        sio.connect(
            ws_url,
            socketio_path="wsapi/socket.io",
            transports=["websocket"],
            headers={"Cookie": f"access_token={token}"},
            wait_timeout=10,
        )

        # Emit request for data
        payload = {
            "funnel_group_id": funnel_group_id,
            "date_range": {
                "start": f"{start_date}T00:00:00Z",
                "end": f"{end_date}T00:00:00Z",
            },
            "segment_id": segment_id,
        }
        sio.emit("funnels_counts", data=payload)

        # Wait for responses (in seconds)
        sio.sleep(5)

        if not all_funnel_data:
            ws_status_msg = "No funnel data received via WebSocket in the allocated time."
    except socketio.exceptions.ConnectionError as e:
        ws_status_msg = f"WebSocket connection failed: {e}"
    except Exception as e:  # noqa: BLE001
        ws_status_msg = f"WebSocket error: {e}"
    finally:
        if sio.connected:
            sio.disconnect()

    if ws_status_msg and not all_funnel_data:
        return {"error": ws_status_msg}

    return all_funnel_data 