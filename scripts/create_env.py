#!/usr/bin/env python3
"""Create or update .env file with all API keys"""

import os

# Default values
DEFAULT_ENV = {
    "CREAO_INVITATION_CODE": "CALHAC",
    "GITHUB_TOKEN": "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",
    "POSTMAN_API_KEY": "your_postman_api_key_here",
    "DEEPGRAM_API_KEY": "your_deepgram_api_key_here",
    "GEMINI_API_KEY": "AIzaSyCLJ9Yf_g6R8VLpIqjOPJefGv4sGw5TGA4",
    "V0_API_KEY": "V0_API_KEY=v1:RPFdMvkqfXKjtpuSXZsVMxU8:MvPE7ACUpMlqJ81LdAgj20VA",
    "VERCEL_TOKEN": "your_vercel_token_here",
    "JANITOR_API_ENDPOINT": "https://janitorai.com/hackathon/completions",
    "JANITOR_API_KEY": "calhacks2047",
    "FETCHAI_API_KEY": "sk_f1565b8c1c934a7ab641446e5b1f4159fb14f45afe964224b90e7f6cfedd55a5",
    "FETCHAI_ENDPOINT": "https://agentverse.ai",
    "CHROMA_HOST": "localhost",
    "CHROMA_PORT": "8000",
    "BACKEND_PORT": "8000",
    "FRONTEND_PORT": "3000",
    "MCP_SERVER_PORT": "8080",
    "NODE_ENV": "development",
    "DEBUG": "true"
}

def load_existing_env(filepath):
    """Load existing .env file into a dictionary"""
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def save_env(filepath, env_vars):
    """Save environment variables to .env file"""
    with open(filepath, 'w') as f:
        f.write("# OPS-X Environment Variables\n\n")
        
        # Write in sections
        f.write("# API Keys\n")
        for key in ["CREAO_INVITATION_CODE", "GITHUB_TOKEN", "POSTMAN_API_KEY", 
                    "DEEPGRAM_API_KEY", "GEMINI_API_KEY", "V0_API_KEY", "VERCEL_TOKEN"]:
            if key in env_vars:
                f.write(f"{key}={env_vars[key]}\n")
        
        f.write("\n# Janitor AI\n")
        for key in ["JANITOR_API_ENDPOINT", "JANITOR_API_KEY"]:
            if key in env_vars:
                f.write(f"{key}={env_vars[key]}\n")
        
        f.write("\n# Fetch.ai\n")
        for key in ["FETCHAI_API_KEY", "FETCHAI_ENDPOINT"]:
            if key in env_vars:
                f.write(f"{key}={env_vars[key]}\n")
        
        f.write("\n# Database\n")
        for key in ["CHROMA_HOST", "CHROMA_PORT"]:
            if key in env_vars:
                f.write(f"{key}={env_vars[key]}\n")
        
        f.write("\n# Server Config\n")
        for key in ["BACKEND_PORT", "FRONTEND_PORT", "MCP_SERVER_PORT"]:
            if key in env_vars:
                f.write(f"{key}={env_vars[key]}\n")
        
        f.write("\n# Environment\n")
        for key in ["NODE_ENV", "DEBUG"]:
            if key in env_vars:
                f.write(f"{key}={env_vars[key]}\n")

def main():
    env_path = '.env'
    
    # Load existing values
    existing = load_existing_env(env_path)
    
    # Merge with defaults (existing values take precedence)
    env_vars = {**DEFAULT_ENV, **existing}
    
    # Save
    save_env(env_path, env_vars)
    
    if existing:
        print(f"Updated {env_path} (preserved existing values)")
    else:
        print(f"Created {env_path} with default values")
    
    # Check for placeholder values
    needs_update = []
    for key, value in env_vars.items():
        if "your_" in value.lower() and key in ["GITHUB_TOKEN", "GEMINI_API_KEY"]:
            needs_update.append(key)
    
    if needs_update:
        print("\nPlease update these required keys:")
        for key in needs_update:
            print(f"  - {key}")

if __name__ == "__main__":
    main()
