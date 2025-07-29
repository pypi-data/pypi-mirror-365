"""STDIO MCP client implementation using FastMCP's StdioTransport."""

from typing import Any

import mcp.types
from fastmcp import Client
from fastmcp.client.messages import MessageHandler
from fastmcp.client.transports import StdioTransport

from ..models import MCPNotification, Prompt, Resource, ResourceTemplate, ServerInfo, Tool
from .base import MCPClient, MCPClientError


class NotificationBridge(MessageHandler):
    """Bridge FastMCP notifications to our notification system."""

    def __init__(self, client: "StdioMCPClient") -> None:
        """Initialize the notification bridge."""
        self.client = client

    async def on_notification(self, message: mcp.types.ServerNotification) -> None:
        """Handle all notifications from FastMCP and forward to our handlers."""
        if self.client._debug:
            print(f"[DEBUG] FastMCP notification received: {message.root}")

        # Convert FastMCP notification to our MCPNotification format
        # The actual notification data is in message.root
        params = getattr(message.root, "params", None)

        # Convert Pydantic params object to dict if needed
        if params is not None and hasattr(params, "model_dump"):
            params = params.model_dump()

        mcp_notification = MCPNotification(
            method=message.root.method,
            params=params,
        )

        # Call the base client's notification handler
        await self.client._handle_notification(mcp_notification)

    async def on_tool_list_changed(self, message: mcp.types.ToolListChangedNotification) -> None:
        """Handle tool list changed notifications."""
        if self.client._debug:
            print(f"[DEBUG] Tools list changed notification: {message}")

    async def on_resource_list_changed(self, message: mcp.types.ResourceListChangedNotification) -> None:
        """Handle resource list changed notifications."""
        if self.client._debug:
            print(f"[DEBUG] Resources list changed notification: {message}")

    async def on_prompt_list_changed(self, message: mcp.types.PromptListChangedNotification) -> None:
        """Handle prompt list changed notifications."""
        if self.client._debug:
            print(f"[DEBUG] Prompts list changed notification: {message}")

    async def on_logging_message(self, message: mcp.types.LoggingMessageNotification) -> None:
        """Handle logging message notifications."""
        if self.client._debug:
            print(f"[DEBUG] Logging message notification: {message}")


class StdioMCPClient(MCPClient):
    """MCP client using FastMCP's StdioTransport.

    This implementation uses FastMCP's StdioTransport which provides
    robust subprocess management and process lifecycle handling.
    """

    def __init__(self, debug: bool = False, roots: list[str] | None = None) -> None:
        """Initialize STDIO client.

        Args:
            debug: Enable debug logging
            roots: List of root paths for filesystem servers
        """
        super().__init__(debug=debug, roots=roots)
        self._transport: StdioTransport | None = None
        self._client: Client | None = None
        self._command: str = ""
        self._args: list[str] = []

    async def connect(self, command: str, args: list[str] | None = None, env: dict[str, str] | None = None) -> None:
        """Connect to MCP server via STDIO.

        Args:
            command: Command to execute
            args: Command arguments
            env: Environment variables
        """
        if self._connected:
            raise MCPClientError("Already connected")

        self._command = command
        self._args = args or []

        # Prepare environment - FastMCP requires explicit env passing
        process_env = {}
        if env:
            process_env.update(env)

        # Create StdioTransport with FastMCP
        if self._debug:
            print(f"[DEBUG] Creating StdioTransport with command: {command}, args: {self._args}, env: {process_env}")

        try:
            self._transport = StdioTransport(command=command, args=self._args, env=process_env if process_env else None)

            # Create notification bridge to handle FastMCP notifications
            notification_bridge = NotificationBridge(self)

            # Create FastMCP client with transport and notification handler
            self._client = Client(self._transport, message_handler=notification_bridge)

            self._connected = True

            if self._debug:
                print(f"[DEBUG] Connected to STDIO process: {command} {' '.join(self._args)}")
        except Exception as e:
            # Handle EPIPE and other subprocess errors
            if "EPIPE" in str(e) or "Broken pipe" in str(e):
                raise MCPClientError(f"Subprocess communication failed (EPIPE): {e}")
            else:
                raise MCPClientError(f"Failed to create subprocess: {e}")

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        if not self._connected:
            return

        self._connected = False

        # Close client (this will handle transport cleanup)
        if self._client:
            try:
                await self._client.close()
                if self._debug:
                    print("[DEBUG] FastMCP client closed successfully")
            except Exception as e:
                if self._debug:
                    print(f"[DEBUG] Error closing client: {e}")
            finally:
                self._client = None

        # Ensure transport is cleaned up
        if self._transport:
            try:
                # If transport has a close method, call it
                if hasattr(self._transport, "close"):
                    await self._transport.close()
                if self._debug:
                    print("[DEBUG] Transport cleaned up")
            except Exception as e:
                if self._debug:
                    print(f"[DEBUG] Error cleaning up transport: {e}")
            finally:
                self._transport = None

        if self._debug:
            print("[DEBUG] Disconnected from STDIO process")

    async def _send_data(self, data: str) -> None:
        """Not used in this implementation - using FastMCP client methods instead."""
        raise NotImplementedError("Use FastMCP client methods instead")

    async def _receive_data(self) -> str | None:
        """Not used in this implementation - using FastMCP client methods instead."""
        raise NotImplementedError("Use FastMCP client methods instead")

    async def initialize(self) -> ServerInfo:
        """Initialize connection and get server info."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            # Use FastMCP's connection context
            async with self._client:
                # Ping server to verify connection
                await self._client.ping()

                # FastMCP doesn't expose separate methods for server info/capabilities
                # The capabilities are available through the transport after connection
                capabilities = {}
                if self._transport and hasattr(self._transport, "server_capabilities"):
                    server_capabilities = getattr(self._transport, "server_capabilities", None)
                    capabilities = server_capabilities or {}

                server_name = "STDIO MCP Server"
                server_version = "unknown"
                protocol_version = "2025-06-18"

                # Try to get server info from transport if available
                if self._transport and hasattr(self._transport, "server_info"):
                    server_info_dict = getattr(self._transport, "server_info", None) or {}
                    server_name = server_info_dict.get("name", server_name)
                    server_version = server_info_dict.get("version", server_version)

                # Convert to our ServerInfo model
                server_info_data = {
                    "protocol_version": protocol_version,
                    "capabilities": capabilities,
                    "name": server_name,
                    "version": server_version,
                }

                self._server_info = ServerInfo(**server_info_data)

                if self._debug:
                    print(f"[DEBUG] Initialized server: {self._server_info.name}")

                return self._server_info
        except Exception as e:
            # Handle EPIPE and other subprocess communication errors
            if "EPIPE" in str(e) or "Broken pipe" in str(e) or "errno: -32" in str(e):
                raise MCPClientError(f"Subprocess communication failed during initialization (EPIPE): {e}")
            else:
                raise MCPClientError(f"Failed to initialize: {e}")

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                tools_data = await self._client.list_tools()
                tools = []

                # FastMCP returns the raw tools list
                if isinstance(tools_data, list):
                    tools_list = tools_data
                else:
                    # Sometimes it might be wrapped in a result dict
                    tools_list = tools_data.get("tools", []) if isinstance(tools_data, dict) else []

                for tool_info in tools_list:
                    # Handle tool data (should be dict from JSON response)
                    if isinstance(tool_info, dict):
                        input_schema_data = tool_info.get("inputSchema", {})

                        if self._debug:
                            print(f"[DEBUG] Raw tool schema: {input_schema_data}")

                        # The server may have properties, don't override them
                        if "properties" not in input_schema_data:
                            input_schema_data["properties"] = {}

                        if self._debug:
                            print(f"[DEBUG] Final tool schema: {input_schema_data}")

                        # Convert dict to ToolParameter
                        from ..models.tool import ToolParameter

                        tool_parameter = ToolParameter(**input_schema_data)

                        tool = Tool(
                            name=tool_info["name"],
                            description=tool_info.get("description", ""),
                            inputSchema=tool_parameter,
                        )
                        tools.append(tool)
                    elif hasattr(tool_info, "name"):
                        # It's a Tool object - extract attributes
                        # FastMCP uses camelCase 'inputSchema' not snake_case 'input_schema'
                        input_schema_data = getattr(tool_info, "inputSchema", {})
                        if not input_schema_data or "properties" not in input_schema_data:
                            input_schema_data = (
                                {"properties": {}, **input_schema_data} if input_schema_data else {"properties": {}}
                            )

                        # Convert dict to ToolParameter
                        from ..models.tool import ToolParameter

                        tool_parameter = ToolParameter(**input_schema_data)

                        tool = Tool(
                            name=tool_info.name,
                            description=getattr(tool_info, "description", ""),
                            inputSchema=tool_parameter,
                        )
                        tools.append(tool)

                return tools
        except Exception as e:
            if self._debug:
                print(f"[DEBUG] Error listing tools: {e}")
            if "timeout" in str(e).lower() or "not supported" in str(e).lower() or "method not found" in str(e).lower():
                return []
            # Handle EPIPE and other subprocess communication errors
            if "EPIPE" in str(e) or "Broken pipe" in str(e) or "errno: -32" in str(e):
                raise MCPClientError(f"Subprocess communication failed during list_tools (EPIPE): {e}")
            raise MCPClientError(f"Failed to list tools: {e}")

    async def list_resources(self) -> list[Resource]:
        """List available resources."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                resources_data = await self._client.list_resources()
                resources = []
                for resource_info in resources_data:
                    # FastMCP may return Resource objects or dictionaries
                    if hasattr(resource_info, "uri"):
                        # It's a Resource object - extract attributes
                        # Convert AnyUrl to string if needed
                        uri_value = getattr(resource_info, "uri", "")
                        uri_value = str(uri_value)  # Always convert to string

                        resource = Resource(
                            uri=uri_value,
                            name=getattr(resource_info, "name", ""),
                            description=getattr(resource_info, "description", None),
                            mimeType=getattr(resource_info, "mimeType", None),  # Use camelCase
                        )
                    elif isinstance(resource_info, dict):
                        # It's a dictionary - use dict access
                        resource = Resource(
                            uri=resource_info["uri"],
                            name=resource_info.get("name", ""),
                            description=resource_info.get("description"),
                            mimeType=resource_info.get("mimeType"),  # Use camelCase
                        )
                    else:
                        # Skip invalid resource_info
                        continue
                    resources.append(resource)
                return resources
        except Exception as e:
            if self._debug:
                print(f"[DEBUG] Error listing resources: {e}")
            if "timeout" in str(e).lower() or "not supported" in str(e).lower() or "method not found" in str(e).lower():
                return []
            raise MCPClientError(f"Failed to list resources: {e}")

    async def list_resource_templates(self) -> list[ResourceTemplate]:
        """List available resource templates."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                templates_data = await self._client.list_resource_templates()
                templates = []
                for template_info in templates_data:
                    # FastMCP may return ResourceTemplate objects or dictionaries
                    if hasattr(template_info, "uriTemplate"):
                        # It's a ResourceTemplate object - extract attributes with camelCase
                        template = ResourceTemplate(
                            uriTemplate=getattr(template_info, "uriTemplate", ""),  # Use camelCase
                            name=getattr(template_info, "name", ""),
                            description=getattr(template_info, "description", None),
                            mimeType=getattr(template_info, "mimeType", None),  # Use camelCase
                        )
                    elif isinstance(template_info, dict):
                        # It's a dictionary - use dict access
                        template = ResourceTemplate(
                            uriTemplate=template_info["uriTemplate"],  # Use camelCase
                            name=template_info.get("name", ""),
                            description=template_info.get("description"),
                            mimeType=template_info.get("mimeType"),  # Use camelCase
                        )
                    else:
                        # Skip invalid template_info
                        continue
                    templates.append(template)
                return templates
        except Exception as e:
            if self._debug:
                print(f"[DEBUG] Error listing resource templates: {e}")
            if "timeout" in str(e).lower() or "not supported" in str(e).lower() or "method not found" in str(e).lower():
                return []
            raise MCPClientError(f"Failed to list resource templates: {e}")

    async def list_prompts(self) -> list[Prompt]:
        """List available prompts."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                prompts_data = await self._client.list_prompts()
                prompts = []
                for prompt_info in prompts_data:
                    # FastMCP may return Prompt objects or dictionaries
                    if hasattr(prompt_info, "name"):
                        # It's a Prompt object - extract attributes
                        arguments = []
                        prompt_arguments = getattr(prompt_info, "arguments", [])
                        if prompt_arguments:
                            for arg_info in prompt_arguments:
                                from ..models.prompt import PromptArgument

                                # Handle both object and dict arguments
                                if hasattr(arg_info, "name"):
                                    arg = PromptArgument(
                                        name=arg_info.name,
                                        description=getattr(arg_info, "description", None),
                                        required=getattr(arg_info, "required", False),
                                    )
                                else:
                                    arg = PromptArgument(
                                        name=arg_info["name"],
                                        description=arg_info.get("description"),
                                        required=arg_info.get("required", False),
                                    )
                                arguments.append(arg)

                        prompt = Prompt(
                            name=prompt_info.name,
                            description=getattr(prompt_info, "description", ""),
                            arguments=arguments,
                        )
                    elif isinstance(prompt_info, dict):
                        # It's a dictionary - use dict access
                        arguments = []
                        if prompt_info.get("arguments"):
                            for arg_info in prompt_info["arguments"]:
                                from ..models.prompt import PromptArgument

                                arg = PromptArgument(
                                    name=arg_info["name"],
                                    description=arg_info.get("description"),
                                    required=arg_info.get("required", False),
                                )
                                arguments.append(arg)

                        prompt = Prompt(
                            name=prompt_info["name"], description=prompt_info.get("description"), arguments=arguments
                        )
                    else:
                        # Skip invalid prompt_info
                        continue
                    prompts.append(prompt)
                return prompts
        except Exception as e:
            if self._debug:
                print(f"[DEBUG] Error listing prompts: {e}")
            if "timeout" in str(e).lower() or "not supported" in str(e).lower() or "method not found" in str(e).lower():
                return []
            raise MCPClientError(f"Failed to list prompts: {e}")

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool with arguments."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                result = await self._client.call_tool(name, arguments)
                return result
        except Exception as e:
            raise MCPClientError(f"Failed to call tool {name}: {e}")

    async def read_resource(self, uri: str) -> Any:
        """Read a resource by URI."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                result = await self._client.read_resource(uri)
                return result
        except Exception as e:
            raise MCPClientError(f"Failed to read resource {uri}: {e}")

    async def get_prompt(self, name: str, arguments: dict[str, Any]) -> Any:
        """Get a prompt with arguments."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                result = await self._client.get_prompt(name, arguments)
                return result
        except Exception as e:
            raise MCPClientError(f"Failed to get prompt {name}: {e}")
