# Setting Up shadcn MCP Server for Claude Code

The UI Designer agent requires the shadcn MCP server to function properly. Follow these steps to set it up:

## Installation

### Method 1: Using npx (Recommended)

```bash
npx @ymadd/shadcn-ui
```

### Method 2: Manual Installation

```bash
# Clone the shadcn MCP server
git clone https://github.com/Jpisnice/shadcn-ui-mcp-server.git
cd shadcn-ui-mcp-server

# Install dependencies
npm install

# Build the server
npm run build
```

## Configuration

Add the shadcn MCP server to your Claude Desktop configuration:

### macOS Configuration
Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows Configuration
Edit: `%APPDATA%\Claude\claude_desktop_config.json`

### Configuration Content

```json
{
  "mcpServers": {
    "shadcn-ui": {
      "command": "node",
      "args": [
        "/path/to/shadcn-ui-mcp-server/dist/index.js"
      ],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

## Alternative: Using the NPM Package

```json
{
  "mcpServers": {
    "shadcn-ui": {
      "command": "npx",
      "args": [
        "-y",
        "@ymadd/shadcn-ui"
      ]
    }
  }
}
```

## Verify Installation

After configuration, restart Claude Desktop and test:

```bash
# In Claude Code, test the MCP server
--shadcn list_components
```

You should see a list of available shadcn/ui components.

## Available Commands

Once installed, the UI Designer agent can use these commands:

### List All Components
```bash
--shadcn list_components
```

### Get Component Source Code
```bash
--shadcn get_component button
--shadcn get_component card
--shadcn get_component form
```

### Get Component Demo/Examples
```bash
--shadcn get_demo button
--shadcn get_demo dialog
```

### Get Complex UI Blocks
```bash
--shadcn get_block dashboard-01
--shadcn get_block authentication-01
```

## Troubleshooting

### MCP Server Not Found
1. Verify the path in claude_desktop_config.json is correct
2. Ensure Node.js is installed and in PATH
3. Restart Claude Desktop after configuration changes

### Permission Errors
```bash
# Fix permissions on macOS/Linux
chmod +x /path/to/shadcn-ui-mcp-server/dist/index.js
```

### Connection Issues
1. Check if any firewall is blocking local connections
2. Verify the MCP server process is running
3. Check Claude Desktop logs for error messages

## Integration with UI Designer Agent

The UI Designer agent automatically uses the shadcn MCP server for:
- Component discovery and selection
- Fetching component source code
- Getting usage examples and best practices
- Accessing pre-built UI blocks

## Best Practices

1. **Always use MCP commands** for shadcn components rather than manually copying code
2. **Check for updates** regularly as shadcn/ui is actively maintained
3. **Use TypeScript** components for better type safety
4. **Follow the design system** specified in @design.md

## Additional Resources

- [shadcn/ui Documentation](https://ui.shadcn.com)
- [MCP Protocol Specification](https://mcpservers.org/docs)
- [Claude Code MCP Integration](https://docs.anthropic.com/claude-code/mcp)

---

*Note: The shadcn MCP server provides access to v4 components optimized for React 19 and Tailwind CSS v4.*