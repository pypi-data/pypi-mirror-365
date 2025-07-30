from setuptools import setup, find_packages

setup(
    name="mcp-domain-checker",
    version="1.0.0",
    description="MCP server for checking domain availability",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "aiohttp>=3.8.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-domain-checker=server:main",
        ],
    },
)