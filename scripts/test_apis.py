#!/usr/bin/env python3
"""
Quick API connection test script
Run this to verify all sponsor APIs are working
"""

import asyncio
import httpx
import json

# API Configurations
JANITOR_API_ENDPOINT = "https://janitorai.com/hackathon/completions"
JANITOR_API_KEY = "calhacks2047"
CREAO_INVITATION_CODE = "CALHAC"
FETCHAI_API_KEY = "sk_f1565b8c1c934a7ab641446e5b1f4159fb14f45afe964224b90e7f6cfedd55a5"


async def test_janitor_ai():
    """Test Janitor AI JLLM API"""
    print("🤖 Testing Janitor AI API...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                JANITOR_API_ENDPOINT,
                headers={
                    "Authorization": JANITOR_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [
                        {"role": "user", "content": "Hello, this is a test from OPS-X!"}
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(" Janitor AI connected successfully!")
                print(f"   Response: {data.get('choices', [{}])[0].get('message', {}).get('content', 'No content')[:100]}...")
                return True
            else:
                print(f" Janitor AI error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f" Janitor AI connection failed: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def test_creao():
    """Test Creao (no API needed, just verify invitation code)"""
    print("\n🎨 Testing Creao...")
    print(f" Creao invitation code ready: {CREAO_INVITATION_CODE}")
    print("   Note: Register at Creao platform and use this code")
    return True


async def test_fetchai():
    """Test Fetch.ai API key format"""
    print("\n🤖 Testing Fetch.ai...")
    if FETCHAI_API_KEY.startswith("sk_") and len(FETCHAI_API_KEY) > 20:
        print(" Fetch.ai API key format looks valid")
        print("   Note: Deploy agents to Agentverse to fully test")
        return True
    else:
        print(" Fetch.ai API key format seems invalid")
        return False


async def main():
    """Run all API tests"""
    print(" OPS-X API Connection Test\n")
    
    results = await asyncio.gather(
        test_janitor_ai(),
        test_creao(),
        test_fetchai()
    )
    
    print("\n📊 Summary:")
    print(f"   Janitor AI: {' Working' if results[0] else ' Failed'}")
    print(f"   Creao: {' Ready' if results[1] else ' Failed'}")
    print(f"   Fetch.ai: {' Valid' if results[2] else ' Failed'}")
    
    if all(results):
        print("\n🎉 All APIs ready! You can start building!")
    else:
        print("\n Some APIs need attention. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
