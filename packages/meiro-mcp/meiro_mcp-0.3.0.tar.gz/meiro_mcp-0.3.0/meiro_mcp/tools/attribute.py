from typing import Any, Dict, List
import json
import re
from urllib.parse import urlparse, urlunparse

import requests
from fastmcp.exceptions import ToolError

from meiro_mcp.auth import get_auth_token, get_meiro_config
from meiro_mcp.mcp_server import mcp


@mcp.tool()
async def list_attributes() -> List[Dict[str, Any]]:
    """
    Get all available attributes from Meiro CDP.

    For compound attributes, sub-attributes are parsed and included in the
    response. Disabled or hidden attributes are filtered out so that the
    returned list only contains attributes that can be safely used by other
    tools.

    Returns:
        A list of dictionaries, one per attribute. Example structure::

            [
                {
                    "id": "my_attribute_id",
                    "name": "My Attribute",
                    "data_type": "string"
                },
                {
                    "id": "compound_attr_id",
                    "name": "Compound Attribute",
                    "data_type": "compound([ [\"field_id\", \"Field name\", \"string\"] ])",
                    "sub_attributes": [
                        {"id": "field_id", "name": "Field name", "type": "string"}
                    ]
                }
            ]
    """
    token = get_auth_token()
    config = get_meiro_config()
    domain = config["domain"]

    parsed_domain = urlparse(domain)
    attributes_url = urlunparse(
        (
            parsed_domain.scheme,
            parsed_domain.netloc,
            "api/attributes",
            "",
            "offset=0&limit=500",
            "",
        )
    )

    headers = {
        "accept": "application/json",
        "X-Access-Token": token,
    }

    response = requests.get(attributes_url, headers=headers)
    response.raise_for_status()
    try:
        full_response = response.json()
        attributes = full_response.get("attributes", [])
    except (KeyError, requests.exceptions.JSONDecodeError) as e:
        raise ToolError(f"Failed to parse attributes from response: {e}")

    processed_attributes: List[Dict[str, Any]] = []

    for attr in attributes:
        # Skip disabled or hidden attributes
        if attr.get("is_disabled", 0) != 0 or attr.get("is_hidden", 0) != 0:
            continue

        attr_id = attr.get("id")
        attr_name = attr.get("name")
        data_type = attr.get("data_type")

        attribute_data: Dict[str, Any] = {
            "id": attr_id,
            "name": attr_name,
            "data_type": data_type,
        }

        # If the attribute is compound, parse its sub-attributes
        if data_type and data_type.startswith("compound("):
            match = re.match(r"compound\((.*)\)", data_type)
            if match:
                compound_str = match.group(1).strip()
                # Ensure the inner string is a valid JSON array representation
                if not compound_str.startswith("["):
                    compound_str = "[" + compound_str
                if not compound_str.endswith("]"):
                    compound_str = compound_str + "]"

                try:
                    sub_attrs_raw = json.loads(compound_str)
                    sub_attributes: List[Dict[str, str]] = []
                    for sub in sub_attrs_raw:
                        # Expecting [id, name, type] triples
                        if len(sub) == 3:
                            sub_id, sub_name, sub_type = sub
                            sub_attributes.append(
                                {"id": sub_id, "name": sub_name, "type": sub_type}
                            )
                    if sub_attributes:
                        attribute_data["sub_attributes"] = sub_attributes
                except Exception:
                    # Any parsing error should not break the entire tool – simply
                    # skip sub-attribute extraction for this attribute.
                    pass

        processed_attributes.append(attribute_data)

    return processed_attributes 