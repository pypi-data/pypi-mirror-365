"""Main MCP server entry point for spec-driven development tool."""

import asyncio
import logging
from typing import Any

import structlog
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import ServerConfig, setup_logging
from .tools.content_tools import ContentAccessTools
from .tools.workflow_tools import WorkflowManagementTools
from .tools.validation_tools import ValidationTools

# Setup structured logging
config = ServerConfig.from_env()
setup_logging(config.log_level, config.log_format, config.log_file)
logger = structlog.get_logger(__name__)

# Initialize MCP server
server: Server = Server("mcp-spec-driven-development")

# Initialize tool handlers
content_tools = ContentAccessTools()
workflow_tools = WorkflowManagementTools()
validation_tools = ValidationTools()


@server.list_tools()  # type: ignore
async def handle_list_tools() -> list[Tool]:
    """List available MCP tools for spec-driven development."""
    logger.debug("Listing available tools")
    tools = []
    
    # Add content access tools
    tools.extend(content_tools.get_tool_definitions())
    
    # Add workflow management tools
    tools.extend(workflow_tools.get_tool_definitions())
    
    # Add validation tools
    tools.extend(validation_tools.get_tool_definitions())
    
    logger.info("Listed tools", tool_count=len(tools))
    return tools


@server.call_tool()  # type: ignore
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[TextContent]:
    """Handle MCP tool calls."""
    if arguments is None:
        arguments = {}

    logger.debug("Handling tool call", tool_name=name, arguments=arguments)

    try:
        # Route to appropriate tool handler
        content_tool_names = {
            "get_template", "get_methodology_guide", 
            "list_available_content", "get_examples_and_case_studies"
        }
        
        workflow_tool_names = {
            "create_workflow", "get_workflow_status", "transition_phase",
            "navigate_backward", "check_transition_requirements", "get_approval_guidance"
        }
        
        validation_tool_names = {
            "validate_document", "get_validation_checklist", 
            "explain_validation_error", "validate_requirement_traceability"
        }
        
        if name in content_tool_names:
            result = await content_tools.handle_tool_call(name, arguments)
        elif name in workflow_tool_names:
            result = await workflow_tools.handle_tool_call(name, arguments)
        elif name in validation_tool_names:
            result = await validation_tools.handle_tool_call(name, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        logger.info("Tool call completed", tool_name=name, success=True)
        return result

    except Exception as e:
        logger.error("Tool call failed", tool_name=name, error=str(e), exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def async_main() -> None:
    """Async main entry point for the MCP server."""
    logger.info("Starting MCP server", server_name=config.name, version=config.version)
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=config.name,
                    server_version=config.version,
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error("Server failed to start", error=str(e), exc_info=True)
        raise


def main() -> None:
    """Synchronous entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
