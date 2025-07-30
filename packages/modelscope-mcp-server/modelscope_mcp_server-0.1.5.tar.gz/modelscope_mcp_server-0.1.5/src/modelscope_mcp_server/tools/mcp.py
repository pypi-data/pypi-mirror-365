"""ModelScope MCP Server MCP tools.

Provides tools for MCP-related operations in the ModelScope MCP Server, such as searching for MCP servers.
"""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..client import default_client
from ..settings import settings
from ..types import McpServer

logger = logging.get_logger(__name__)


def register_mcp_tools(mcp: FastMCP) -> None:
    """Register all MCP-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance

    """

    @mcp.tool(
        annotations={
            "title": "Search MCP Servers",
        }
    )
    async def search_mcp_servers(
        search: Annotated[
            str,
            Field(description="Search keyword for MCP servers"),
        ] = "",
        category: Annotated[
            (
                Literal[
                    "browser-automation",
                    "search",
                    "communication",
                    "customer-and-marketing",
                    "developer-tools",
                    "entertainment-and-media",
                    "file-systems",
                    "finance",
                    "knowledge-and-memory",
                    "location-services",
                    "art-and-culture",
                    "research-and-data",
                    "calendar-management",
                    "other",
                ]
                | None
            ),
            Field(description=("Filter by category")),
        ] = None,
        is_hosted: Annotated[
            bool | None,
            Field(description="Filter by hosted status"),
        ] = None,
        limit: Annotated[int, Field(description="Maximum number of servers to return", ge=1, le=100)] = 10,
    ) -> list[McpServer]:
        """Search for MCP servers on ModelScope."""
        url = f"{settings.main_domain}/openapi/v1/mcp/servers"

        # Build filter object
        filter_obj = {}
        if category is not None:
            filter_obj["category"] = category
        if is_hosted is not None:
            filter_obj["is_hosted"] = is_hosted

        request_data = {
            "filter": filter_obj,
            "page_number": 1,
            "page_size": limit,
            "search": search,
        }

        response = default_client.put(url, json_data=request_data)

        servers_data = response.get("data", {}).get("mcp_server_list", [])

        servers = []
        for server_data in servers_data:
            id = server_data.get("id", "")
            modelscope_url = f"{settings.main_domain}/mcp/servers/{id}"

            server = McpServer(
                id=id,
                modelscope_url=modelscope_url,
                name=server_data.get("name", ""),
                chinese_name=server_data.get("chinese_name", ""),
                description=server_data.get("description", ""),
                publisher=server_data.get("publisher", ""),
                tags=server_data.get("tags", []),
                view_count=server_data.get("view_count", 0),
            )
            servers.append(server)

        return servers
