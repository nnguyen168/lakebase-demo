"""Test script for the Agent Model Serving endpoint."""

import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def test_agent_endpoint():
    """Test the agent model serving endpoint directly."""
    
    # Get configuration
    host = os.getenv('DATABRICKS_HOST', '').rstrip('/')
    token = os.getenv('DATABRICKS_TOKEN')
    endpoint_url = os.getenv('MODEL_SERVING_ENDPOINT')
    
    print(f"Host: {host}")
    print(f"Token: {'Present' if token else 'Missing'}")
    print(f"Endpoint: {endpoint_url}")
    print()
    
    if not all([host, token, endpoint_url]):
        print("❌ Missing required environment variables!")
        print("Please set DATABRICKS_HOST, DATABRICKS_TOKEN, and MODEL_SERVING_ENDPOINT")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test message
    payload = {
        "input": [
            {
                "role": "user",
                "content": "What are my top 5 products by revenue?"
            }
        ]
    }
    
    print("Testing agent endpoint...")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        with httpx.Client(timeout=120.0, verify=False) as client:
            response = client.post(endpoint_url, headers=headers, json=payload)
            
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Response:")
                print(json.dumps(data, indent=2))
                
                # Extract the assistant's message
                output_list = data.get("output", [])
                if output_list:
                    first_message = output_list[0]
                    content_list = first_message.get("content", [])
                    for content_item in content_list:
                        if content_item.get("type") == "output_text":
                            print("\n" + "="*80)
                            print("ASSISTANT RESPONSE:")
                            print("="*80)
                            print(content_item.get("text", ""))
                            print("="*80)
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
    except httpx.TimeoutException:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_agent_api():
    """Test the agent API endpoint (through FastAPI backend)."""
    
    print("\n" + "="*80)
    print("Testing Agent API (FastAPI backend)")
    print("="*80 + "\n")
    
    # Assuming the backend is running on localhost:8000
    api_url = "http://localhost:8000/api/agent/send-message"
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "What are my top 5 products by revenue?"
            }
        ]
    }
    
    print(f"Request URL: {api_url}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(api_url, json=payload)
            
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Response:")
                print(json.dumps(data, indent=2))
                
                print("\n" + "="*80)
                print("ASSISTANT RESPONSE:")
                print("="*80)
                print(data.get("content", ""))
                print("="*80)
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
    except httpx.ConnectError:
        print("❌ Could not connect to backend. Is the server running on localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_health_check():
    """Test the agent health check endpoint."""
    
    print("\n" + "="*80)
    print("Testing Agent Health Check")
    print("="*80 + "\n")
    
    api_url = "http://localhost:8000/api/agent/health"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(api_url)
            
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Health Check Response:")
                print(json.dumps(data, indent=2))
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
    except httpx.ConnectError:
        print("❌ Could not connect to backend. Is the server running on localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("="*80)
    print("Agent Model Serving Endpoint Test")
    print("="*80 + "\n")
    
    # Test 1: Direct endpoint
    test_agent_endpoint()
    
    # Test 2: Health check
    test_health_check()
    
    # Test 3: FastAPI backend
    print("\nTo test the FastAPI backend, make sure the server is running:")
    print("  cd app/smart_stock && uv run uvicorn server.app:app --reload")
    print("\nThen run this test again or uncomment the line below:")
    # test_agent_api()

