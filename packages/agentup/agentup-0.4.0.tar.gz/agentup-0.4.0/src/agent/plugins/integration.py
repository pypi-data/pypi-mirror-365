from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from agent.config.settings import Settings

import structlog
from a2a.types import Task

from agent.capabilities.manager import _capabilities

from .adapter import PluginAdapter, get_plugin_manager

logger = structlog.get_logger(__name__)


def integrate_plugins_with_capabilities(config: Union["Settings", None] = None) -> dict[str, list[str]]:
    """
    Integrate the plugin system with the existing capability registry.

    This function:
    1. Discovers and loads all plugins
    2. Registers only configured plugin capabilities as capability executors
    3. Makes them available through the existing get_capability_executor() mechanism

    Args:
        config: Optional configuration object. If not provided,
                will be loaded when needed.

    Returns:
        Dict mapping capability_id to required_scopes for enabled capabilities.
    """

    # Get the plugin manager and adapter
    plugin_manager = get_plugin_manager()

    # If config is not provided, we need to load it
    if config is None:
        from agent.config import Config

        config = Config

    adapter = PluginAdapter(config, plugin_manager)

    # Get configured plugins from the agent config
    try:
        configured_plugins = config.plugins
    except Exception as e:
        logger.warning(f"Could not load agent config, no plugins will be registered: {e}")
        configured_plugins = []

    registered_count = 0

    # Build a mapping of plugin names to their capabilities
    plugin_to_capabilities = {}
    for capability_id in adapter.list_available_capabilities():
        capability_info = adapter.get_capability_info(capability_id)
        if capability_info and "plugin_name" in capability_info:
            plugin_name = capability_info["plugin_name"]
            if plugin_name not in plugin_to_capabilities:
                plugin_to_capabilities[plugin_name] = []
            plugin_to_capabilities[plugin_name].append(capability_id)

    # Determine which capabilities to register based on new capability-based config
    capabilities_to_register = {}  # capability_id -> scope_requirements

    if not configured_plugins:
        logger.error("No plugin configuration found in agentup.yml - explicit configuration required")
        raise ValueError("Plugin configuration is required in agentup.yml.")
    else:
        for plugin_config in configured_plugins:
            plugin_id = plugin_config.plugin_id

            # Check if this uses the new capability-based structure
            if plugin_config.capabilities:
                if not plugin_config.capabilities:
                    logger.error(f"Plugin '{plugin_id}' has no capabilities defined in configuration")
                    logger.warning(
                        f"Plugin '{plugin_id}' must define capabilities in the configuration. "
                        f"Add 'capabilities' section with explicit scope requirements."
                    )
                    continue  # Skip this plugin and continue with the next one
                for capability_config in plugin_config.capabilities:
                    capability_id = capability_config.capability_id
                    required_scopes = capability_config.required_scopes or []
                    enabled = capability_config.enabled

                    if enabled:
                        # Store for registration but don't log until we verify plugin exists
                        capabilities_to_register[capability_id] = required_scopes
            else:
                logger.error(f"Plugin '{plugin_id}' uses legacy format - explicit capability configuration required")
                raise ValueError(
                    f"Plugin '{plugin_id}' must use explicit capability configuration format. "
                    f"Legacy format has been removed for security. "
                    f"Add 'capabilities' section with explicit scope requirements."
                )

    # Store the adapter globally so other components can access it
    _plugin_adapter[0] = adapter

    # Check for configured plugins/capabilities that weren't discovered
    discovered_capabilities = set(adapter.list_available_capabilities())
    for plugin_config in configured_plugins:
        plugin_id = plugin_config.plugin_id
        plugin_found = False

        # Check if any discovered capability belongs to this plugin
        for capability_id in discovered_capabilities:
            capability_info = adapter.get_capability_info(capability_id)
            if capability_info and capability_info.get("plugin_name") == plugin_id:
                plugin_found = True
                break

        if not plugin_found:
            logger.warning(
                f"Plugin '{plugin_id}' is configured in agentup.yml but was not discovered. "
                f"Check that the plugin is installed and properly registered."
            )

        # Also check individual capabilities
        if plugin_config.capabilities:
            for capability_config in plugin_config.capabilities:
                capability_id = capability_config.capability_id
                if capability_config.enabled and capability_id not in discovered_capabilities:
                    logger.warning(
                        f"Capability '{capability_id}' from plugin '{plugin_id}' is configured "
                        f"but not available. The plugin may not be installed or the capability "
                        f"may not exist."
                    )

    for capability_id, required_scopes in capabilities_to_register.items():
        # Skip if capability executor already exists (don't override existing executors)
        if capability_id in _capabilities:
            logger.debug(f"Capability '{capability_id}' already registered as executor, skipping plugin")
            continue

        if capability_id in discovered_capabilities:
            logger.debug(f"Registering capability '{capability_id}' with scopes: {required_scopes}")
        else:
            logger.debug(
                f"Skipping registration of missing capability '{capability_id}' with scopes: {required_scopes}"
            )
            continue

        try:
            from agent.capabilities.manager import register_plugin_capability

            plugin_config = {"capability_id": capability_id, "required_scopes": required_scopes}

            # Register using the framework's scope enforcement pattern
            register_plugin_capability(plugin_config)
            logger.debug(
                f"Registered plugin capability '{capability_id}' with framework scope enforcement: {required_scopes}"
            )
            registered_count += 1

        except Exception as e:
            logger.error(f"Failed to register plugin capability '{capability_id}' with scope enforcement: {e}")
            raise ValueError(
                f"Plugin capability '{capability_id}' requires proper scope enforcement configuration. "
                f"Legacy registration without scope enforcement has been removed for security."
            ) from e

    if registered_count == 0:
        logger.debug("No plugin capabilities registered in Agents config, integration complete")
    logger.info(
        f"Configuration loaded {registered_count} plugin capabilities (out of {len(adapter.list_available_capabilities())} discovered)"
    )

    # Return the enabled capabilities for use in AI function registration
    return capabilities_to_register


# Store the adapter instance
_plugin_adapter: list[PluginAdapter | None] = [None]


def get_plugin_adapter() -> PluginAdapter | None:
    return _plugin_adapter[0]


def create_plugin_capability_wrapper(plugin_executor: Callable) -> Callable[[Task], str]:
    """
    Wrap a plugin capability executor to be compatible with the existing executor signature.

    This converts between the plugin's CapabilityContext and the simple Task parameter.
    """

    async def wrapped_executor(task: Task) -> str:
        # The adapter already handles this conversion
        return await plugin_executor(task)

    return wrapped_executor


def list_all_capabilities() -> list[str]:
    """
    List all available capabilities from both executors and plugins.
    """
    # Get capabilities from existing executors
    executor_capabilities = list(_capabilities.keys())

    # Get capabilities from plugins if integrated
    plugin_capabilities = []
    adapter = get_plugin_adapter()
    if adapter:
        plugin_capabilities = adapter.list_available_capabilities()

    # Combine and deduplicate
    all_capabilities = list(set(executor_capabilities + plugin_capabilities))
    return sorted(all_capabilities)


def get_capability_info(capability_id: str) -> dict[str, Any]:
    """
    Get information about a capability from either executors or plugins.
    """
    # Check if it's a plugin capability
    adapter = get_plugin_adapter()
    if adapter:
        info = adapter.get_capability_info(capability_id)
        if info:
            return info

    # Fallback to basic executor info
    if capability_id in _capabilities:
        executor = _capabilities[capability_id]
        return {
            "capability_id": capability_id,
            "name": capability_id.replace("_", " ").title(),
            "description": executor.__doc__ or "No description available",
            "source": "executor",
        }

    return {}


def enable_plugin_system() -> None:
    """
    Enable the plugin system and integrate it with existing capability executors.

    This should be called during agent startup.
    """
    try:
        enabled_capabilities = integrate_plugins_with_capabilities()

        # Integrate plugins with the function registry for AI function calling
        try:
            from agent.core.dispatcher import get_function_registry

            # Get the global function registry
            function_registry = get_function_registry()

            # Get the plugin adapter that was created during capability integration
            adapter = get_plugin_adapter()

            if adapter:
                # Integrate the plugin adapter with the function registry
                # Pass the enabled capabilities to ensure only enabled AI functions are registered
                adapter.integrate_with_function_registry(function_registry, enabled_capabilities)
                logger.info("Plugin adapter integrated with function registry for AI function calling")
            else:
                logger.warning("No plugin adapter available for function registry integration")

        except Exception as e:
            logger.error(f"Failed to integrate plugins with function registry: {e}")
            # Continue without AI function integration

        # Make multi-modal helper available to plugins
        try:
            # Store in global space for plugins to access
            import sys

            from agent.utils.multimodal import MultiModalHelper

            if "agentup.multimodal" not in sys.modules:
                import types

                module = types.ModuleType("agentup.multimodal")
                module.MultiModalHelper = MultiModalHelper
                sys.modules["agentup.multimodal"] = module
                logger.debug("Multi-modal helper made available to plugins")
        except Exception as e:
            logger.warning(f"Could not make multi-modal helper available to plugins: {e}")

        logger.debug("Plugin system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to enable plugin system: {e}", exc_info=True)
        # Don't crash the agent if plugins fail to load
        pass
