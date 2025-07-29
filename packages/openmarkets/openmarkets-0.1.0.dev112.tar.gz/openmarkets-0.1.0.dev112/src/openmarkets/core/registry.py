import importlib
import inspect
import logging
import pkgutil

logger = logging.getLogger(__name__)


class ToolRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        # Potentially initialize other attributes here if needed

    def register_all_tools(self, mcp_instance, tools_package_name="openmarkets.tools"):
        """
        Dynamically discovers and registers all tools from the specified package.

        Args:
            mcp_instance: The FastMCP instance to register tools with.
            tools_package_name: The full package name where tool modules are located (e.g., "openmarkets.tools").
        """
        try:
            tools_package = importlib.import_module(tools_package_name)
        except ImportError:
            logger.error(f"Could not import tools package: {tools_package_name}")
            return

        if not hasattr(tools_package, "__path__"):
            logger.error(f"Tools package {tools_package_name} does not have __path__, cannot discover modules.")
            return

        package_path = tools_package.__path__

        for _, module_name, _ in pkgutil.walk_packages(package_path, prefix=tools_package.__name__ + "."):
            if module_name.endswith(".__init__"):
                continue
            try:
                module = importlib.import_module(module_name)
                logger.info(f"Successfully imported module: {module_name}")

                # Register all public functions in the module as tools
                try:
                    self.register_module_tools(module, mcp_instance)
                    logger.info(f"Successfully registered tools from {module_name}")
                except Exception as e:
                    logger.error(f"Error registering tools from {module_name}: {e}")

            except ImportError as e:
                logger.error(f"Failed to import module {module_name}: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred while processing module {module_name}: {e}")

    def register_module_tools(self, module, mcp):
        """Register all public functions in a module as tools with the MCP server."""
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("_") or name.startswith("register_"):
                continue
            try:
                mcp.tool()(func)
            except Exception as e:
                logger.error(f"Error registering function '{name}' from module '{module.__name__}': {e}")
                raise e
