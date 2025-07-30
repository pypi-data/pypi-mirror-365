from meiro_mcp.mcp_server import mcp
from meiro_mcp.tools import customer, segment, attribute, event, funnel


def main():
    mcp.run(transport="stdio")