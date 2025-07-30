# 🌐 Domain Checker MCP

An MCP (Model Context Protocol) server that helps AI assistants check domain availability and suggest creative domain names for your projects!

## ✨ Features

- **Check Domain Availability** - Verify if specific domains are available across multiple extensions
- **Smart Domain Suggestions** - Generate creative domain ideas based on your keywords
- **Multiple Extensions** - Check .com, .net, .org, .io, and more
- **Real-time Results** - Uses DNS lookup and API checks for accurate availability

## 🚀 Quick Start

### Installation

```bash
# Clone or download this repository
git clone https://github.com/yourusername/mcp-domain-checker.git
cd mcp-domain-checker

# Install dependencies
pip install mcp aiohttp
```

### Testing

Test the server locally with the MCP inspector:

```bash
npx @modelcontextprotocol/inspector python server.py
```

## 🤖 Usage with Claude Desktop

Add this to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "domain-checker": {
      "command": "python",
      "args": ["/full/path/to/mcp-domain-checker/server.py"]
    }
  }
}
```

Then restart Claude Desktop and try:

- "Check if myawesomeblog.com is available"
- "Help me find domains for my cooking recipe website"
- "Is johndoe available in .com, .net, and .io?"

## 🛠️ Available Tools

### `check_domain`
Check if specific domain names are available
- **Input**: Domain name and optional extensions array
- **Example**: `mysite.com` with extensions `[".com", ".net", ".org"]`

### `suggest_domains`  
Generate domain suggestions from keywords
- **Input**: Keywords/business description and optional extensions
- **Example**: `"cooking blog recipes"` → suggests `cookingblog.com`, `mycookingblog.net`, etc.

## 📦 Installation via PyPI

```bash
pip install mcp-domain-checker
```

Then use in your Claude config:
```json
{
  "mcpServers": {
    "domain-checker": {
      "command": "mcp-domain-checker"
    }
  }
}
```