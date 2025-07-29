"""
SPDX-License-Identifier: Apache-2.0

Netlify deployment tool for SWE Agent.
Deploy HTML/CSS/JS applications to Netlify ONLY when explicitly requested.
Uses direct HTTP API calls instead of netlify-python SDK.
"""

import os
import zipfile
from pathlib import Path
from langchain.tools import BaseTool
from pydantic import Field
from typing import Optional
from rich.console import Console
from .netlify_api import deploy_to_netlify_direct

console = Console()


class NetlifyDeployTool(BaseTool):
    """
    Deploy HTML/CSS/JS applications to Netlify.
    
    CRITICAL: This tool should ONLY be used when the user explicitly asks to deploy to Netlify.
    Do NOT automatically detect HTML projects - only deploy when specifically requested.
    """
    
    name: str = "netlify_deploy"
    description: str = """Deploy HTML/CSS/JS applications to Netlify hosting platform.

USAGE: Use this tool ONLY when user explicitly asks to deploy to Netlify.
Do NOT automatically detect HTML projects or suggest deployment.

Parameters:
- project_path: Path to directory containing HTML/CSS/JS files
- site_name: Optional custom name for the Netlify site

The tool will:
1. Create a deployment package from the project directory
2. Create a new Netlify site (or use existing site if creation fails)
3. Deploy the application and provide live URLs

Requires NETLIFY_ACCESS_TOKEN environment variable."""

    project_path: str = Field(description="Path to the project directory to deploy")
    site_name: Optional[str] = Field(default=None, description="Optional name for the Netlify site")

    def _run(self, project_path: str, site_name: Optional[str] = None) -> str:
        """Deploy project to Netlify using direct API calls."""
        return deploy_to_netlify_direct(project_path, site_name)


# Create tool instance
netlify_deploy_tool = NetlifyDeployTool(project_path="", site_name=None)