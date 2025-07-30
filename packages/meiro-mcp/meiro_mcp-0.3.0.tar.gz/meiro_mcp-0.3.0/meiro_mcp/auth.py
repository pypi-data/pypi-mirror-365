import os
import functools
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timedelta

import requests
from fastmcp.exceptions import ToolError


_token_cache: dict = {"token": None, "generated_at": None}


@functools.lru_cache(maxsize=None)
def get_meiro_config() -> dict[str, str]:
    """Reads and validates Meiro CDP connection info from environment variables."""
    config = {}
    for var in ["MEIRO_DOMAIN", "MEIRO_USERNAME", "MEIRO_PASSWORD"]:
        if var not in os.environ:
            raise ToolError(f"Missing required environment variable: {var}")
        config[var.replace("MEIRO_", "").lower()] = os.environ[var]
    return config


def get_auth_token() -> str:
    """Authenticate with Meiro CDP and return a token."""
    if _token_cache["token"] and _token_cache["generated_at"]:
        if datetime.now() - _token_cache["generated_at"] < timedelta(hours=1):
            return _token_cache["token"]

    config = get_meiro_config()
    domain = config["domain"]
    username = config["username"]
    password = config["password"]

    parsed_domain = urlparse(domain)
    login_url = urlunparse(
        (parsed_domain.scheme, parsed_domain.netloc, "api/users/login", "", "", "")
    )

    response = requests.post(
        login_url,
        json={"email": username, "password": password},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    try:
        token = response.json()["token"]
        _token_cache["token"] = token
        _token_cache["generated_at"] = datetime.now()
        return token
    except (KeyError, requests.exceptions.JSONDecodeError) as e:
        raise ToolError(f"Failed to get token from response: {e}") 