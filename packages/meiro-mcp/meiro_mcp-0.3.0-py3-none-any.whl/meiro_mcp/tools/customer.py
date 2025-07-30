from urllib.parse import urlparse, urlunparse

import requests
from fastmcp.exceptions import ToolError

from meiro_mcp.auth import get_auth_token, get_meiro_config
from meiro_mcp.mcp_server import mcp


@mcp.tool()
async def search_customers(search_text: str) -> list[dict]:
    """Search for customers in Meiro CDP."""
    token = get_auth_token()
    config = get_meiro_config()
    domain = config["domain"]
    parsed_domain = urlparse(domain)
    search_url = urlunparse(
        (
            parsed_domain.scheme,
            parsed_domain.netloc,
            "api/customers/fulltext_search",
            "",
            f"search_text={search_text}",
            "",
        )
    )
    headers = {
        "Content-Type": "application/json",
        "X-Access-Token": token,
    }
    response = requests.get(search_url, headers=headers)
    response.raise_for_status()
    try:
        return response.json()["customers"]
    except (KeyError, requests.exceptions.JSONDecodeError) as e:
        raise ToolError(f"Failed to parse customers from response: {e}")


@mcp.tool()
async def get_customer_attributes(customer_entity_id: str) -> dict:
    """
    Get all attributes for a specific customer from Meiro CDP.

    Args:
        customer_entity_id: The unique identifier for the customer (e.g. '12345').
    Returns:
        A dictionary of customer attributes, grouped by attribute ID.
    """
    token = get_auth_token()
    config = get_meiro_config()
    domain = config["domain"]
    parsed_domain = urlparse(domain)
    attributes_url = urlunparse(
        (
            parsed_domain.scheme,
            parsed_domain.netloc,
            f"api/customers/{customer_entity_id}/attributes",
            "",
            "load_full_structure=0&attribute_values_max_count=100",
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
        data = response.json()
        customer_attributes = data.get("customer_attributes", [])

        attributes_grouped = {}
        for attr in customer_attributes:
            attr_id = attr.get("attribute_id")
            value = attr.get("value")
            if attr_id not in attributes_grouped:
                attributes_grouped[attr_id] = []
            attributes_grouped[attr_id].append(value)

        return attributes_grouped
    except (KeyError, requests.exceptions.JSONDecodeError) as e:
        raise ToolError(f"Failed to parse customer attributes from response: {e}") 