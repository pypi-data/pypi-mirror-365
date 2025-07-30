#!/usr/bin/env python3

import asyncio
import json
import sys
from typing import List, Optional, Any, Dict
import aiohttp
import socket
import re
from urllib.parse import urlparse

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl
import mcp.types as types

server = Server("mcp-domain-checker")

async def check_domain_dns(domain: str) -> bool:
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, socket.getaddrinfo, domain, None)
        return False
    except socket.gaierror:
        return True
    except Exception:
        return None

async def check_domain_api(session: aiohttp.ClientSession, domain: str) -> Optional[bool]:
    try:
        async with session.get(f"https://dns.google/resolve?name={domain}&type=A") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("Status", 0) != 0
    except Exception:
        pass
    return None

async def generate_alternatives(base_domain: str) -> List[str]:
    alternatives = []
    
    prefixes = ["get", "my", "the", "try", "go", "use"]
    suffixes = ["app", "site", "hub", "pro", "now", "today", "official"]
    
    for prefix in prefixes:
        alternatives.append(f"{prefix}{base_domain}")
    
    for suffix in suffixes:
        alternatives.append(f"{base_domain}{suffix}")
    
    if len(base_domain) > 4:
        alternatives.append(base_domain[:4])
        alternatives.append(base_domain[:6])
    
    alternatives.append(f"{base_domain}2024")
    alternatives.append(f"{base_domain}2025")
    
    return alternatives[:10]

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
        ),
        Tool(
            name="suggest_domains",
            description="Generate available domain name suggestions based on keywords or business description",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "Keywords or business description to generate domain suggestions from. Example: 'cooking blog recipes'"
                    },
                    "extensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional array of extensions to check. Defaults to .com, .net, .org",
                        "default": [".com", ".net", ".org"]
                    }
                },
                "required": ["keywords"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "check_domain":
        return await check_domain_availability(arguments)
    elif name == "suggest_domains":
        return await suggest_domains(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def check_domain_availability(arguments: Dict[str, Any]) -> List[TextContent]:
    domain = arguments.get("domain", "")
    extensions = arguments.get("extensions", [".com", ".net", ".org", ".io"])
    
    domain = domain.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0]
    
    domain_pattern = r'([a-zA-Z0-9\-]+\.[a-zA-Z]{2,})|([a-zA-Z0-9\-]+)(?=\s|$)'
    matches = re.findall(domain_pattern, domain.lower())
    
    if matches:
        for match in matches:
            if match[0]:
                domain = match[0]
                break
            elif match[1] and len(match[1]) > 2:
                domain = match[1]
                break
    
    domain = re.sub(r'\b(i|want|wanna|make|a|website|called|named|for|my|the|and|or|site|blog)\b', '', domain)
    domain = re.sub(r'\s+', '', domain)
    domain = domain.strip()
    
    if "." in domain:
        base_domain = domain.split(".")[0]
    else:
        base_domain = domain
    
    results = []
    unavailable_domains = []
    
    async with aiohttp.ClientSession() as session:
        for ext in extensions:
            if "." in domain and not domain.endswith(ext):
                full_domain = domain
            else:
                full_domain = f"{base_domain}{ext}"
            
            try:
                is_available = await check_domain_api(session, full_domain)
                if is_available is None:
                    is_available = await check_domain_dns(full_domain)
                
                if is_available is None:
                    status = "Could not check 🤷‍♂️"
                elif is_available:
                    status = "Available! 🎉"
                else:
                    status = "Taken 😞"
                    unavailable_domains.append(full_domain)
                
                results.append({
                    "domain": full_domain,
                    "available": is_available,
                    "status": status
                })
                
            except Exception as e:
                results.append({
                    "domain": full_domain,
                    "available": None,
                    "status": "Error checking 🤷‍♂️",
                    "error": str(e)
                })
    
    available_count = len([r for r in results if r.get("available")])
    
    response_data = {
        "summary": f"Found {available_count} available domains!" if available_count > 0 else "All checked domains appear to be taken.",
        "results": results
    }
    
    if unavailable_domains:
        alternatives = await generate_alternatives(base_domain)
        alternative_results = []
        
        async with aiohttp.ClientSession() as session:
            for alt in alternatives:
                for ext in [".com", ".net", ".org"][:2]:
                    alt_domain = f"{alt}{ext}"
                    try:
                        is_available = await check_domain_api(session, alt_domain)
                        if is_available is None:
                            is_available = await check_domain_dns(alt_domain)
                        
                        if is_available:
                            alternative_results.append({
                                "domain": alt_domain,
                                "available": True,
                                "status": "Available Alternative! ✨"
                            })
                            
                        if len(alternative_results) >= 5:
                            break
                    except Exception:
                        continue
                if len(alternative_results) >= 5:
                    break
        
        if alternative_results:
            response_data["alternatives"] = {
                "message": "Here are some available alternatives:",
                "suggestions": alternative_results
            }
        else:
            response_data["alternatives"] = {
                "message": "No alternatives found. Try different keywords or extensions."
            }
    
    return [TextContent(type="text", text=json.dumps(response_data, indent=2))]

async def suggest_domains(arguments: Dict[str, Any]) -> List[TextContent]:
    keywords = arguments.get("keywords", "")
    extensions = arguments.get("extensions", [".com", ".net", ".org"])
    
    words = keywords.lower().split()
    suggestions = []
    
    if len(words) >= 1:
        base_suggestions = [
            "".join(words),
            "-".join(words),
            f"get{''.join(words)}",
            f"my{''.join(words)}",
            f"the{''.join(words)}",
            f"{''.join(words)}hub",
            f"{''.join(words)}app",
            f"{''.join(words)}site",
            f"{''.join(words)}pro",
        ]
        
        if len(words) >= 2:
            base_suggestions.extend([
                "".join(words[:2]),
                "-".join(words[:2]),
                f"{words[0]}{words[-1]}"
            ])
        
        suggestions = base_suggestions
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for suggestion in suggestions[:8]:
            for ext in extensions[:3]:
                domain = f"{suggestion}{ext}"
                
                try:
                    is_available = await check_domain_api(session, domain)
                    if is_available is None:
                        is_available = await check_domain_dns(domain)
                    
                    if is_available:
                        results.append({
                            "domain": domain,
                            "available": True,
                            "status": "Available! 🎉",
                            "suggestion": True
                        })
                except Exception:
                    continue
    
    response_data = {
        "keywords": keywords,
        "availableSuggestions": results,
        "totalFound": len(results),
        "tip": "🎯 Here are available domain suggestions based on your keywords!" if results else "💡 Try more specific or shorter keywords, or check manually with the domain checker!"
    }
    
    return [TextContent(type="text", text=json.dumps(response_data, indent=2))]

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