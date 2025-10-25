"""
Vercel API Integration
Handles automated deployments to Vercel
"""

import os
import httpx
import asyncio
from typing import Dict, Optional


class VercelAPIClient:
    """Vercel API client for deployments"""
    
    def __init__(self):
        self.token = os.getenv("VERCEL_TOKEN", "")
        self.base_url = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def create_project(
        self,
        name: str,
        github_repo: str,  # format: "username/repo"
        framework: str = "nextjs"
    ) -> Dict:
        """Create a new Vercel project linked to a GitHub repo"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v9/projects",
                headers=self.headers,
                json={
                    "name": name,
                    "framework": framework,
                    "gitRepository": {
                        "type": "github",
                        "repo": github_repo
                    },
                    "buildCommand": "npm run build",
                    "devCommand": "npm run dev",
                    "installCommand": "npm install"
                },
                timeout=30.0
            )
            
            if response.status_code in [200, 201]:
                project_data = response.json()
                return {
                    "success": True,
                    "project_id": project_data.get("id"),
                    "project_name": project_data.get("name")
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create Vercel project: {response.text}"
                }
    
    async def trigger_deployment(
        self,
        project_name: str,
        github_repo: str
    ) -> Dict:
        """Trigger a new deployment"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v13/deployments",
                headers=self.headers,
                json={
                    "name": project_name,
                    "gitSource": {
                        "type": "github",
                        "repo": github_repo,
                        "ref": "main"
                    },
                    "target": "production"
                },
                timeout=30.0
            )
            
            if response.status_code in [200, 201]:
                deployment_data = response.json()
                deployment_id = deployment_data.get("id")
                
                # Wait for deployment to complete
                deployment_url = await self.wait_for_deployment(deployment_id)
                
                return {
                    "success": True,
                    "deployment_id": deployment_id,
                    "url": deployment_url or f"https://{project_name}.vercel.app"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to trigger deployment: {response.text}"
                }
    
    async def wait_for_deployment(
        self,
        deployment_id: str,
        max_attempts: int = 30,
        delay: int = 2
    ) -> Optional[str]:
        """Wait for a deployment to complete and return its URL"""
        
        async with httpx.AsyncClient() as client:
            for _ in range(max_attempts):
                response = await client.get(
                    f"{self.base_url}/v13/deployments/{deployment_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    deployment = response.json()
                    state = deployment.get("readyState")
                    
                    if state == "READY":
                        return deployment.get("url")
                    elif state in ["ERROR", "CANCELED"]:
                        return None
                
                await asyncio.sleep(delay)
        
        return None
    
    async def get_project(self, project_id: str) -> Dict:
        """Get project details"""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v9/projects/{project_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get project: {response.text}"
                }


# Singleton instance
vercel_client = VercelAPIClient()
