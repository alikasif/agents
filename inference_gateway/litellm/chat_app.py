"""
Chat Application - LLM Client Call Example.
Demonstrates how to make LLM calls using the LiteLLM proxy.
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

# LiteLLM proxy URL
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")

# Master key for LiteLLM proxy admin operations
MASTER_KEY = os.getenv("LITELLM_MASTER_KEY")


def create_user(
    user_id: str,
    user_email: str,
    master_key: str = None,
) -> dict:
    """
    Create a new user in LiteLLM proxy.
    
    Args:
        user_email: Email address for the new user
        user_id: Optional user ID (auto-generated if not provided)
        master_key: Admin master key (defaults to LITELLM_MASTER_KEY env var)
        
    Returns:
        dict with created user info
        
    Example:
        user = create_user("john@example.com")
        print(user)
    """
    master_key = master_key or MASTER_KEY
    
    payload = {"user_email": user_email, "user_id": user_id}
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{LITELLM_PROXY_URL}/user/new",
            json=payload,
            headers={
                "Authorization": f"Bearer {master_key}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()


def generate_key(
    user_id: str,
    models: list[str] = None,
    key: str = None,
    duration: str = "30min",
    master_key: str = None,
) -> dict:
    """
    Generate an API key for LiteLLM proxy.
    
    Args:
        models: List of model names the key can access (e.g., ["gemini"])
        aliases: Model aliases mapping (e.g., {"gpt-3.5-turbo": "gemini"})
        duration: Key validity duration (e.g., "30min", "1h", "7d")
        master_key: Admin master key (defaults to LITELLM_MASTER_KEY env var)
        
    Returns:
        dict with generated key info including 'key' field
        
    Example:
        key_info = generate_key(
            models=["gemini"],
            key_alias="007key",
            duration="1h"
        )
        print(key_info["key"])
    """
    master_key = master_key or MASTER_KEY
    
    payload = {
        "duration": duration,
    }

    payload["user_id"] = user_id
    
    if models:
        payload["models"] = models
    if key:
        payload["key"] = key
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{LITELLM_PROXY_URL}/key/generate",
            json=payload,
            headers={
                "Authorization": f"Bearer {master_key}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()["key"]


def chat(prompt: str, model: str = "gpt5", temperature: float = 0.7, api_key: str = None) -> str:
    """
    Make a synchronous LLM call to LiteLLM proxy.
    
    Args:
        prompt: User message/prompt
        model: Model name from config.yaml (default: gpt5)
        temperature: Sampling temperature (0-2)
        
    Returns:
        LLM response content as string
    """
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{LITELLM_PROXY_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def get_key_info(key: str, master_key: str = None) -> dict:
    """
    Get key info and spend tracking for a given API key.
    
    Args:
        user_key: The API key to get info for
        master_key: Admin master key (defaults to LITELLM_MASTER_KEY env var)
        
    Returns:
        dict with key info including spend, usage, models, etc.
        
    Example:
        info = get_key_info("sk-abc123...")
        print(f"Total spend: ${info.get('spend', 0)}")
    """
    master_key = master_key or MASTER_KEY
    
    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            f"{LITELLM_PROXY_URL}/key/info",
            params={"key": key},
            headers={"Authorization": f"Bearer {master_key}"},
        )

        if response.status_code == 404:
            return None
        
        return response.json()["key"]


def get_user_info(user_id: str, master_key: str = None) -> dict:
    """
    Get user info from LiteLLM proxy.
    
    Args:
        user_email: The user email to get info for
        master_key: Admin master key (defaults to LITELLM_MASTER_KEY env var)
        
    Returns:
        dict with user info including spend, keys, etc.
        
    Example:
        info = get_user_info("my-unique-id")
        print(info)
    """
    master_key = master_key or MASTER_KEY
    
    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            f"{LITELLM_PROXY_URL}/user/info",
            params={"user_id": user_id},
            headers={"Authorization": f"Bearer {master_key}"},
        )
        if response.status_code == 404:
            return None
        
        return response.json()


if __name__ == "__main__":
    # Example usage
    print("=" * 50)
    print("LLM Client Demo")
    print("=" * 50)
    
    prompt = "write a python function to check if number is perfect square"
    print(f"\nPrompt: {prompt}")
    
    try:
        user_id="007bond"
        user_email = "007@bond.com"
        model = "anthropic"
        key = "sk-007key"
        
        user_info = get_user_info(user_id)
        
        if not user_info:
            print(f"user {user_id} not found, creating user")
            user_info = create_user(user_id=user_id, user_email=user_email)    
        
        print(f"User Info: {user_info['user_id']}")

        virtual_key = get_key_info(key=key)        
        if not virtual_key:
            print(f"virtual key {key} not found, creating virtual key")
            virtual_key = generate_key(key=key, user_id=user_id, models=["anthropic"], duration="1d")
        
        print(f"Virtual Key: {virtual_key}")
        
        user_info = get_user_info(user_id)
        print(f"User Info 1: {user_info['user_info']['spend']}")

        response = chat(prompt, model="gpt5", api_key=virtual_key)
        print(f"Response: {response}")

        user_info = get_user_info(user_id)
        print(f"User Info 2: {user_info['user_info']['spend']}")
    
    except httpx.ConnectError:
        print("Error: LiteLLM proxy not running. Start it with:")
        print("  litellm --config config.yaml --port 4000")
    except Exception as e:
        print(f"Error: {e}")
