#!/usr/bin/env python3
"""
Simple Python script to test vLLM server with OpenAI-compatible client
"""

import os
import sys
import json
from pathlib import Path
from openai import OpenAI


def find_env_file():
    """Find .env file starting from current directory and going up the directory tree"""
    current_dir = Path.cwd()
    for directory in [current_dir] + list(current_dir.parents):
        env_file = directory / ".env"
        if env_file.exists():
            return env_file
    return None


def load_env_file():
    """Load environment variables from .env file"""
    env_file = find_env_file()
    if env_file:
        print(f"Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")
    else:
        print("Warning: No .env file found in current directory or parent directories")


def make_request(prompt=None, max_tokens=100, temperature=0.7, stream=False):
    """Make a request to the vLLM server using OpenAI client"""
    
    # Load environment variables
    load_env_file()
    
    # Server configuration (matching server code)
    server_name = os.getenv("QWEN_MODEL_PATH", "qwen_server")
    port = os.getenv("vLLM_PORT", "7050")
    host = os.getenv("vLLM_HOST", "0.0.0.0")
    openai_api_key = os.getenv("OPENAI_API_KEY", "EMPTY")
    
    # If HOST is 0.0.0.0, use localhost for the request
    request_host = "localhost" if host == "0.0.0.0" else host
    base_url = f"http://{request_host}:{port}/v1"
    
    # Default prompt if none provided
    if prompt is None:
        prompt = "Hello! How are you today?"
    
    print(f"Testing vLLM server at: {base_url}")
    print(f"Model name: {server_name}")
    print(f"Sending prompt: {prompt}")
    print("Response:")
    print("-" * 50)
    
    # Create OpenAI client
    client = OpenAI(
        api_key=openai_api_key,
        base_url=base_url,
    )
    
    try:
        if stream:
            # Streaming response
            response = client.chat.completions.create(
                model=server_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_body={"chat_template_kwargs": {"enable_thinking": False}}
            )
            
            print("Streaming response:")
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print("\n" + "-" * 50)
            print("Full response:")
            print(full_response)
            
        else:
            # Non-streaming response
            response = client.chat.completions.create(
                model=server_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_body={"chat_template_kwargs": {"enable_thinking": False}}
            )
            
            # Pretty print the response
            print(json.dumps(response.model_dump(), indent=2))
            
            # Extract and print just the content for easier reading
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                print("\n" + "-" * 50)
                print("Generated text:")
                print(content)
        
    except Exception as e:
        print(f"Error making request: {e}")
        return None
    
    print("\n" + "-" * 50)
    print("Request completed.")
    return response


if __name__ == "__main__":
    # Get prompt from command line argument or use default
    prompt = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Optional: get max_tokens and temperature from command line
    max_tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    temperature = float(sys.argv[3]) if len(sys.argv) > 3 else 0.7
    
    # Optional: enable streaming with --stream flag
    stream = "--stream" in sys.argv
    
    make_request(prompt, max_tokens, temperature, stream) 