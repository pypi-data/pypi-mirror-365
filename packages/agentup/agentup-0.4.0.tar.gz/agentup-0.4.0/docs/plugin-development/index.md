# AgentUp Plugin System

The AgentUp plugin system is for extending AI agent capabilities and provides a clean,
type-safe, and extensible way to create, distribute, and manage agent skills.

## What Are Plugins?

Plugins are independent Python packages that extend your agent's capabilities. Unlike traditional handlers, plugins:

- **Are fully independent** - can be developed, tested, and distributed separately
- **Support hot-reloading** - develop and test without restarting your agent
- **Are type-safe** - full type hints and validation throughout
- **Follow standards** - use Python entry points and standard packaging
- **Include testing** - comprehensive testing framework included
- **Support AI functions** - seamless LLM function calling integration

## Quick Start

### 1. Create Your First Plugin

Plugins can be created anywhere - you don't need to be inside an agent project:

```bash
# Create a new plugin with interactive prompts (run from any directory)
agentup plugin create

# Or specify details directly
agentup plugin create weather-plugin --template ai

# This creates a new directory with your plugin
cd weather-plugin/
```

### 2. Develop and Test

```bash
# Install your plugin in development mode
pip install -e .

# Your plugin is now available to any AgentUp agent on your system!
```

### 3. Use in Your Agent

Plugins are discovered automatically through two methods:

**a) Development Mode** (Recommended for plugin development)
```bash
# Navigate to your plugin directory
cd /path/to/weather-plugin

# Install in development mode
pip install -e .

# Now available to all agents - changes take effect immediately
agentup agent serve
```

**b) Production Mode** (For published packages)
```bash
# Install from PyPI or other sources
pip install agentup-weather-plugin

# Plugin automatically available to all agents
agentup agent serve
```

## Plugin Types

### Basic Plugins
Perfect for simple text processing and straightforward tasks.

### Advanced Plugins  
Include state management, external API integration, and middleware.

### AI Plugins
Provide LLM-callable functions for agent interactions.

## Documentation Sections

1. **[Getting Started](getting-started.md)** - Create your first plugin in 5 minutes
2. **[Plugin Development](development.md)** - Comprehensive development guide
3. **[AI Function Integration](ai-functions.md)** - Build LLM-callable functions
4. **[Scopes and Security](scopes-and-security.md)** - Plugin security and access control
5. **[System Prompts](plugin-system-prompts.md)** - Customize AI behavior with capability-specific system prompts
6. **[Testing Plugins](testing.md)** - Test your plugins thoroughly
7. **[CLI Reference](cli-reference.md)** - Complete CLI command documentation

## Why Use Plugins?

**For Developers:**
- Focus on your skill logic, not infrastructure
- Rich development tools and templates
- Comprehensive testing framework
- Hot-reload during development

**For Users:**
- Easy installation: `agentup plugin install weather-plugin`
- Automatic discovery and loading
- Rich plugin ecosystem
- Seamless integration with existing agents

**For Teams:**
- Independent development cycles
- Clear interfaces and contracts
- Version management and dependencies
- Professional distribution workflow

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your Plugin   │    │  AgentUp Core    │    │   LLM Service   │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Skill Logic │◄┼────┼►│ Plugin Mgr   │◄┼────┼►│ Function    │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ │ Calling     │ │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ └─────────────┘ │
│ │AI Functions │◄┼────┼►│ Function Reg │ │    │                 │
│ └─────────────┘ │    │ └──────────────┘ │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

The plugin system provides clean interfaces between your code and the agent infrastructure,
making plugin development straightforward and maintainable, and best of all,
sharable with the community.

## Next Steps

Ready to build your first plugin? Start with our [Getting Started Guide](getting-started.md)
and have a working plugin in just 5 minutes!