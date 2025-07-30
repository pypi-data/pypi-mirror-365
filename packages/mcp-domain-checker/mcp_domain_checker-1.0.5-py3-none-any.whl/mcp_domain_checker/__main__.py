#!/usr/bin/env python3

import asyncio
import json
import sys
from typing import List, Optional, Any, Dict
import aiohttp
import socket
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl
import mcp.types as types

server = Server("mcp-domain-checker")

async def check_dns(domain: str) -> bool:
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, socket.getaddrinfo, domain, None)
        return False
    except socket.gaierror:
        return True
    except:
        return None

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    return [
        Tool(
            name="check_domain",
            description="Check if specific domain names are available for registration",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "The domain name to check (without http:// or www). Example: myawesomesite or myawesomesite.com"
                    },
                    "extensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional array of extensions to check. Defaults to common ones like .com, .net, .org",
                        "default": [".com", ".net", ".org", ".io"]
                    }
                },
                "required": ["domain"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "check_domain":
        return await check_domains(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def check_domains(args: Dict[str, Any]) -> List[TextContent]:
    domain = args.get("domain", "")
    extensions = args.get("extensions", [".com", ".net", ".org", ".io"])
    
    domain = domain.replace("http://", "").replace("https://", "").replace("www.", "")
    if "/" in domain:
        domain = domain.split("/")[0]
    
    if "." in domain:
        base = domain.split(".")[0]
    else:
        base = domain
    
    results = []
    
    # Check each extension
    for ext in extensions:
        full_domain = f"{base}{ext}"
        
        available = await check_dns(full_domain)
        
        if available is None:
            status = "Error checking"
        elif available:
            status = "Available"
        else:
            status = "Taken"
        
        results.append({
            "domain": full_domain,
            "available": available,
            "status": status
        })
    
    # Count available ones
    available_count = sum(1 for r in results if r.get("available") == True)
    
    # Build response
    if available_count > 0:
        summary = f"Found {available_count} available domain(s)"
    else:
        summary = "All domains appear to be taken"
    
    response = {
        "summary": summary,
        "results": results
    }
    
    # If nothing available, suggest some alternatives
    if available_count == 0:
        alts = []
        prefixes = ["get", "my", "try"]
        suffixes = ["app", "site", "hub"]
        
        # Just check a few quick alternatives with .com
        for prefix in prefixes[:2]:
            alt = f"{prefix}{base}.com"
            if await check_dns(alt):
                alts.append({"domain": alt, "status": "Available"})
        
        for suffix in suffixes[:2]:
            alt = f"{base}{suffix}.com"
            if await check_dns(alt):
                alts.append({"domain": alt, "status": "Available"})
        
        if alts:
            response["alternatives"] = alts
    
    return [TextContent(type="text", text=json.dumps(response, indent=2))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-domain-checker",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())