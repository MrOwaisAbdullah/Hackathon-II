"""Test OpenRouter API key and free embedding model."""
import os
from openai import OpenAI

# Load API key
api_key = "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"

print("="*60)
print("OpenRouter API & Model Test")
print("="*60)

# Test 1: List available models
print("\n1. Testing models endpoint...")
try:
    import httpx

    response = httpx.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10.0
    )

    if response.status_code == 200:
        models = response.json()
        print(f"✅ Found {len(models.get('data', []))} models")

        # Find free embedding models
        print("\n🔍 Searching for free embedding models...")
        for model in models.get('data', []):
            model_id = model.get('id', '')
            if 'free' in model_id.lower() and 'embed' in model_id.lower():
                print(f"   📌 {model_id}")
    else:
        print(f"❌ Models request failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Models endpoint error: {e}")

# Test 2: Test the specific embedding model
print("\n2. Testing openai/text-embedding-3-small embedding...")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

try:
    print("   🔢 Sending test request...")
    response = client.embeddings.create(
        model="openai/text-embedding-3-small",
        input=["Test sentence for embedding."],
    )

    print(f"✅ Embedding successful!")
    print(f"   Model: {response.model}")
    print(f"   Embedding dimension: {len(response.data[0].embedding)}")
    print(f"   First 5 values: {response.data[0].embedding[:5]}")

except Exception as e:
    print(f"❌ Embedding API error: {e}")
    print(f"   Error type: {type(e).__name__}")

    # Check if it's an auth error
    if "401" in str(e) or "auth" in str(e).lower():
        print("\n💡 Tips:")
        print("   - Check your API key at https://openrouter.ai/keys")
        print("   - Make sure the key has credits or is active")
    elif "rate" in str(e).lower():
        print("\n💡 Tips:")
        print("   - Rate limit reached, wait a moment and try again")
    elif "model" in str(e).lower():
        print("\n💡 Tips:")
        print("   - The model might not support embeddings")
        print("   - Try a different model")

print("\n" + "="*60)
