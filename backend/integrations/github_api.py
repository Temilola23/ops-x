"""
GitHub API Integration
Handles repo creation, branches, commits, and PRs
"""

import os
import base64
import httpx
from typing import Dict, List, Optional


class GitHubAPIClient:
    """GitHub REST API client"""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        if not self.token:
            print("WARNING: GITHUB_TOKEN not found in environment")
        else:
            print(f"GitHub client initialized with token: {self.token[:8]}...")
    
    async def create_repo(self, name: str, description: str, private: bool = False) -> Dict:
        """Create a new GitHub repository"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json={
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": True  # Initialize with README
                }
            )
            
            if response.status_code == 201:
                repo_data = response.json()
                print(f"GitHub repo created successfully: {repo_data['html_url']}")
                return {
                    "success": True,
                    "repo_name": repo_data["full_name"],
                    "repo_url": repo_data["html_url"],
                    "clone_url": repo_data["clone_url"],
                    "default_branch": repo_data["default_branch"]
                }
            else:
                error_msg = f"GitHub API error {response.status_code}: {response.text}"
                print(f"ERROR creating repo: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
    
    async def get_default_branch_sha(self, repo_full_name: str) -> Optional[str]:
        """Get the SHA of the default branch"""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{repo_full_name}/git/refs/heads/main",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()["object"]["sha"]
            
            # Try 'master' if 'main' doesn't exist
            response = await client.get(
                f"{self.base_url}/repos/{repo_full_name}/git/refs/heads/master",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()["object"]["sha"]
            
            return None
    
    async def create_or_update_file(
        self, 
        repo_full_name: str,
        file_path: str,
        content: str,
        message: str,
        branch: str = "main"
    ) -> Dict:
        """Create or update a file in the repository"""
        
        # Encode content to base64
        content_bytes = content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        
        async with httpx.AsyncClient() as client:
            # Check if file exists
            get_response = await client.get(
                f"{self.base_url}/repos/{repo_full_name}/contents/{file_path}",
                headers=self.headers,
                params={"ref": branch}
            )
            
            payload = {
                "message": message,
                "content": content_base64,
                "branch": branch
            }
            
            # If file exists, include its SHA for update
            if get_response.status_code == 200:
                existing_sha = get_response.json()["sha"]
                payload["sha"] = existing_sha
            
            # Create or update the file
            response = await client.put(
                f"{self.base_url}/repos/{repo_full_name}/contents/{file_path}",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "commit_sha": response.json()["commit"]["sha"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create/update file: {response.text}"
                }
    
    async def create_branch(
        self,
        repo_full_name: str,
        branch_name: str,
        base_sha: str
    ) -> Dict:
        """Create a new branch"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{repo_full_name}/git/refs",
                headers=self.headers,
                json={
                    "ref": f"refs/heads/{branch_name}",
                    "sha": base_sha
                }
            )
            
            if response.status_code == 201:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": f"Failed to create branch: {response.text}"
                }
    
    async def create_pull_request(
        self,
        repo_full_name: str,
        title: str,
        head: str,
        base: str,
        body: str = ""
    ) -> Dict:
        """Create a pull request"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{repo_full_name}/pulls",
                headers=self.headers,
                json={
                    "title": title,
                    "head": head,
                    "base": base,
                    "body": body
                }
            )
            
            if response.status_code == 201:
                pr_data = response.json()
                return {
                    "success": True,
                    "pr_url": pr_data["html_url"],
                    "pr_number": pr_data["number"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create PR: {response.text}"
                }
    
    async def push_multiple_files(
        self,
        repo_full_name: str,
        files: Dict[str, str],
        commit_message: str,
        branch: str = "main"
    ) -> Dict:
        """Push multiple files to a repository"""
        
        results = []
        
        for file_path, content in files.items():
            result = await self.create_or_update_file(
                repo_full_name,
                file_path,
                content,
                commit_message,
                branch
            )
            results.append({
                "file": file_path,
                "success": result["success"]
            })
        
        all_successful = all(r["success"] for r in results)
        
        return {
            "success": all_successful,
            "results": results
        }


# Singleton instance
github_client = GitHubAPIClient()
