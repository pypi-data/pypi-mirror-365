from typing import Optional, Dict, Any
from urllib.parse import urlparse, urlunparse, urlencode
import json
import socketio

import requests
from fastmcp.exceptions import ToolError

from meiro_mcp.auth import get_auth_token, get_meiro_config
from meiro_mcp.mcp_server import mcp


@mcp.tool()
async def list_segments() -> list[dict]:
    """
    List all segments from Meiro CDP and return as a list of dictionaries.

    Returns:
        A list of dictionaries, where each dictionary represents a segment with its details.
    """
    token = get_auth_token()
    config = get_meiro_config()
    domain = config["domain"]
    parsed_domain = urlparse(domain)

    all_segments = []
    limit = 100
    offset = 0

    while True:
        query_params = {
            "offset": offset,
            "limit": limit,
            "order_by": "created",
            "order_dir": "DESC",
            "name_filter": "",
            "load_full_structure": 0,
            "show_my": 1,
            "show_shared_with_me": 1,
            "show_foreign": 1,
        }

        segments_url = urlunparse(
            (
                parsed_domain.scheme,
                parsed_domain.netloc,
                "api/segments",
                "",
                urlencode(query_params),
                "",
            )
        )
        headers = {
            "accept": "application/json",
            "X-Access-Token": token,
        }

        response = requests.get(segments_url, headers=headers)
        response.raise_for_status()

        try:
            data = response.json()
            segments = data.get("segments", [])
            all_segments.extend(segments)
            if len(segments) < limit:
                break
            offset += limit
        except (KeyError, requests.exceptions.JSONDecodeError) as e:
            raise ToolError(f"Failed to parse segments from response: {e}")

    processed_segments = []
    for seg in all_segments:
        seg_id = seg.get("id")
        seg_url = (
            urlunparse(
                (
                    parsed_domain.scheme,
                    parsed_domain.netloc,
                    f"segments/custom/{seg_id}",
                    "",
                    "",
                    "",
                )
            )
            if seg_id
            else None
        )

        processed_segment = {
            "id": seg_id,
            "name": seg.get("name"),
            "customers_count": seg.get("customers_count"),
            "settings": seg.get("settings"),
            "url": seg_url,
        }
        processed_segments.append(processed_segment)

    return processed_segments


@mcp.tool()
async def create_segment(name: str, settings: Optional[dict] = None) -> dict:
    """
    Create a new segment in Meiro CDP.
    Documentation on the Segment creation DSL:

    **Segment Definition DSL (STRICT):**
        - To select all customers:
        {}

        - Single attribute condition (for scalar or compound attributes):
        {
            "attribute_id": "scalar_attribute_id",
            "condition": {
                "operation": "equals",
                "value": "meiro"
            },
            "negation": false
        }
        {
            "attribute_id": "compound_attribute_id",
            "condition": {
                "sub_attribute_id": "age",
                "operation": "equals",
                "value": "meiro"
            },
            "negation": false
        }

        - Attribute operation (multiple conditions for a single attribute):
        {
            "attribute_id": "age",
            "operation": "or",
            "operands": [
                {
                    "condition": {
                        "operation": "equals",
                        "value": 25
                    }
                },
                {
                    "operation": "and",
                    "operands": [
                        {
                            "condition": {
                                "operation": "lower",
                                "value": 10
                            }
                        },
                        {
                            "condition": {
                                "operation": "greater",
                                "value": 30
                            }
                        }
                    ]
                }
            ],
            "negation": false
        }

        - Segment operation (combine attribute conditions, attribute operations, or other segment operations):
        {
            "operation": "and",
            "operands": [
                {
                    "attribute_id": "subscription",
                    "condition": {
                        "sub_attribute_id": "enabled",
                        "operation": "is_true"
                    }
                },
                {
                    "attribute_id": "age",
                    "operation": "and",
                    "operands": [
                        {
                            "condition": {
                                "operation": "lower",
                                "value": 30
                            }
                        },
                        {
                            "condition": {
                                "operation": "greater",
                                "value": 20
                            }
                        }
                    ]
                }
            ],
            "negation": false
        }

        {
            "operands": [
                {
                    "negation": false,
                    "condition": {
                        "value": "6 hours ago",
                        "operation": "date_greater_than",
                        "sub_attribute_id": "date"
                    },
                    "attribute_id": "me_products_viewed_comp"
                },
                {
                    "operands": [
                        {
                            "negation": false,
                            "condition": {
                                "value": "now - 6 hours",
                                "operation": "date_lower_than"
                            },
                            "attribute_id": "me_transaction_datetime_last"
                        },
                        {
                            "negation": false,
                            "condition": {
                                "operation": "is_not_set"
                            },
                            "attribute_id": "me_transaction_datetime_last"
                        }
                    ],
                    "operation": "or"
                },
                {
                    "negation": false,
                    "condition": {
                        "value": 1,
                        "operation": "number_equals"
                    },
                    "attribute_id": "ab_num_mailkit_email_all"
                }
            ],
            "operation": "and"
        }
        ---
        **IMPORTANT RULES WHEN CREATING SEGMENTS:**
        - If you want to return all customers, interpret this as "All customers in the system without any filtering"
        - Use ONLY the attribute IDs from the list_attributes tool.
        - NEVER invent or guess attribute IDs or structure.
        - Use the correct structure for each type of segment/condition as shown above.
        - While you need to use this structured format for creating segments, NEVER show the raw JSON to users
        - Always interpret the JSON into human-readable descriptions when presenting to users
        ---
        **Allowed Operations and Data Types:**
        [
            {"operation": "equals", "data_types": ["int", "float", "string", "bool", "date", "datetime"]},
            {"operation": "not_equal", "data_types": ["int", "float", "string", "bool", "date", "datetime"]},
            {"operation": "contains", "data_types": ["string"]},
            {"operation": "not_contain", "data_types": ["string"]},
            {"operation": "in", "data_types": ["int", "float", "string", "bool", "date", "datetime"]},
            {"operation": "not_in", "data_types": ["int", "float", "string", "bool", "date", "datetime"]},
            {"operation": "contains_any_of", "data_types": ["string"]},
            {"operation": "not_contain_any_of", "data_types": ["string"]},
            {"operation": "number_equals", "data_types": ["int", "float"]},
            {"operation": "number_not_equal", "data_types": ["int", "float"]},
            {"operation": "number_lower_than", "data_types": ["int", "float"]},
            {"operation": "number_greater_than", "data_types": ["int", "float"]},
            {"operation": "number_between", "data_types": ["int", "float"]},
            {"operation": "number_in", "data_types": ["int", "float"]},
            {"operation": "number_not_in", "data_types": ["int", "float"]},
            {"operation": "date_equals", "data_types": ["date", "datetime"]},
            {"operation": "date_lower_than", "data_types": ["date", "datetime"]},
            {"operation": "date_between", "data_types": ["date", "datetime"]},
            {"operation": "date_matches_current_day", "data_types": ["date", "datetime"]},
            {"operation": "date_matches_current_month", "data_types": ["date", "datetime"]},
            {"operation": "date_matches_current_year", "data_types": ["date", "datetime"]},
            {"operation": "is_true", "data_types": ["bool"]},
            {"operation": "is_false", "data_types": ["bool"]},
            {"operation": "is_set", "data_types": ["int", "float", "string", "bool", "date", "datetime", "compound"]},
            {"operation": "is_not_set", "data_types": ["int", "float", "string", "bool", "date", "datetime", "compound"]}
        ]

    Args:
        name: Name of the segment
        settings: Dictionary of segment settings describing the segment conditions

    Returns:
        Dict containing:
        - id: Segment ID
        - name: Segment name
        - url: URL of the segment
    """
    token = get_auth_token()
    config = get_meiro_config()
    domain = config["domain"]
    parsed_domain = urlparse(domain)
    segment_url = urlunparse(
        (
            parsed_domain.scheme,
            parsed_domain.netloc,
            "api/segments",
            "",
            "",
            "",
        )
    )
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Access-Token": token,
    }

    conditions = {}
    if settings:
        conditions = settings

    data = {"name": name, "settings": {"conditions_operation": conditions}}

    try:
        response = requests.post(segment_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        segment_data = result.get("segment", {})
        segment_id = segment_data.get("id")
        segment_name = segment_data.get("name")
        new_segment_url = urlunparse(
            (
                parsed_domain.scheme,
                parsed_domain.netloc,
                f"segments/custom/{segment_id}",
                "",
                "",
                "",
            )
        )
        return {"id": segment_id, "name": segment_name, "url": new_segment_url}
    except requests.exceptions.HTTPError as e:
        try:
            error_details = e.response.json()
            message = error_details.get("message", e.response.text)
            raise ToolError(f"Failed to create segment: {message}")
        except json.JSONDecodeError:
            message = e.response.text
            raise ToolError(f"Failed to create segment: {message}")
    except Exception as e:
        raise ToolError(f"Failed to create segment: {str(e)}")


@mcp.tool()
async def get_segment_details(segment_id: int) -> dict:
    """
    Get details for a specific segment from Meiro CDP, including its customer count,
    conditions, and live insights, and return as a dictionary.

    Returns:
        A dictionary containing segment details: name, URL, customer count, description, conditions, and insights.
    """
    token = get_auth_token()
    config = get_meiro_config()
    domain = config["domain"]
    parsed_domain = urlparse(domain)

    headers = {"accept": "application/json", "X-Access-Token": token}

    try:
        # Fetch segment details
        segment_url = urlunparse(
            (
                parsed_domain.scheme,
                parsed_domain.netloc,
                f"api/segments/{segment_id}",
                "",
                "",
                "",
            )
        )
        response = requests.get(segment_url, headers=headers)
        response.raise_for_status()
        # Attempt to parse the JSON body. In some edge-cases (e.g. the segment does not
        # exist or the user does not have permission) the CDP API may legitimately
        # return `null` (which becomes `None` in Python) or another non-object JSON
        # value. Guard against these scenarios so we raise a clear ToolError instead
        # of bubbling up an AttributeError.
        try:
            data = response.json()
        except json.JSONDecodeError as decode_err:
            raise ToolError(
                f"Failed to parse response for segment ID {segment_id}: {str(decode_err)}"
            )

        # The happy-path is a JSON object at the top level. If the API returns
        # `null`/`None`, a list, or any other type, provide a helpful error.
        if not isinstance(data, dict):
            raise ToolError(
                f"Unexpected response format when fetching segment ID {segment_id}: "
                f"expected JSON object but got {type(data).__name__}"
            )

        segment_data = data.get("segment", {})

        if not segment_data:
            raise ToolError(f"No details found for segment ID: {segment_id}")

        ui_base_url = urlunparse(
            (parsed_domain.scheme, parsed_domain.netloc, "", "", "", "")
        )

        result = {
            "id": segment_data.get("id"),
            "name": segment_data.get("name", "N/A"),
            "description": segment_data.get("description", "No description provided."),
            "customers_count": segment_data.get("customers_count"),
            "url": f"{ui_base_url}/segments/custom/{segment_data.get('id')}",
            # The API may return "settings": null. Use an empty dict instead so
            # the following nested lookup doesn’t raise an AttributeError.
            "conditions": (segment_data.get("settings") or {}).get(
                "conditions_operation", {}
            ),
            "aggregations_and_insights": {},
        }

        # WebSocket part for aggregations/insights
        ws_full_url = f"wss://{parsed_domain.netloc}"
        sio = socketio.Client(logger=False, engineio_logger=False)
        segment_aggregations_data = []
        segment_customer_count_data = None

        @sio.on("segment_aggregations_response")
        def on_message(data: Dict[str, Any]):
            nonlocal segment_aggregations_data
            if data.get("segment_id") == segment_id:
                segment_aggregations_data.append(data)

        @sio.on("segment_counts_response")
        def on_segment_counts(data: Dict[str, Any]):
            nonlocal segment_customer_count_data
            if (
                data.get("segment_id") == segment_id
                and data.get("count_type") == "segment_results_count"
            ):
                segment_customer_count_data = data.get("count")

        ws_fetch_status_message = ""
        try:
            sio.connect(
                ws_full_url,
                socketio_path="wsapi/socket.io",
                transports=["websocket"],
                headers={"Cookie": f"access_token={token}"},
                wait_timeout=10,
            )
            sio.emit("segment_aggregations", data={"segment_id": segment_id})
            sio.emit(
                "segment_counts",
                data={"segment_id": segment_id, "count_type": "segment_results_count"},
            )
            sio.sleep(3)
        except Exception as e:
            ws_fetch_status_message = (
                f"WebSocket connection failed or timed out: {str(e)}"
            )
        finally:
            if sio.connected:
                sio.disconnect()

        if ws_fetch_status_message:
            result["aggregations_and_insights"]["status"] = ws_fetch_status_message

        if segment_aggregations_data:
            result["aggregations_and_insights"]["insights"] = segment_aggregations_data

        if segment_customer_count_data is not None:
            result["live_customer_count"] = segment_customer_count_data

        return result

    except requests.exceptions.HTTPError as http_err:
        try:
            error_detail = http_err.response.json()
        except json.JSONDecodeError:
            error_detail = {
                "detail": http_err.response.text
                if http_err.response.text
                else str(http_err)
            }
        raise ToolError(f"Failed to get segment details: {error_detail.get('detail')}")
    except Exception as e:
        raise ToolError(f"Failed to get segment details for ID {segment_id}: {str(e)}") 