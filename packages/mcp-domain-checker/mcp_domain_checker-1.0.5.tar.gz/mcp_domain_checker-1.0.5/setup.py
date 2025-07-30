from setuptools import setup, find_packages

setup(
    name="mcp-domain-checker",
    version="1.0.5",
    description="MCP server for checking domain availability and suggesting alternatives",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "aiohttp>=3.8.0",
    ],
    entry_points={
        "console_scripts": [
        "mcp-domain-checker=mcp_domain_checker.__main__:cli",
        ],
    },
)