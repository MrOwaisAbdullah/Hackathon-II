"""Find available embedding models on OpenRouter."""
import urllib.request
import json

api_key = "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"

print("="*60)
print("OpenRouter Embedding Models Search")
print("="*60)

# Get all models
print("\n📡 Fetching all models from OpenRouter...")
req = urllib.request.Request(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        models_data = json.loads(response.read().decode())
except Exception as e:
    print(f"❌ Failed to fetch models: {e}")
    exit(1)

all_models = models_data.get("data", [])
print(f"✅ Found {len(all_models)} total models")

# Filter for embedding models (output modality = embeddings)
print("\n🔍 Filtering for embedding models...")
embedding_models = []

for model in all_models:
    architecture = model.get("architecture", {})
    output_modalities = architecture.get("output_modalities", [])

    # Check if embeddings is an output modality
    if "embeddings" in output_modalities or "embedding" in model.get("id", "").lower():
        embedding_models.append({
            "id": model.get("id"),
            "name": model.get("name"),
            "pricing": model.get("pricing", {}),
            "context_length": model.get("context_length"),
        })

print(f"✅ Found {len(embedding_models)} embedding models")

# Sort by price (cheapest first)
def get_prompt_price(model):
    pricing = model.get("pricing", {})
    prompt_price = pricing.get("prompt", "999")
    try:
        return float(prompt_price)
    except:
        return 999.0

embedding_models.sort(key=get_prompt_price)

# Display top 10 cheapest embedding models
print("\n" + "="*60)
print("Top 10 Cheapest Embedding Models:")
print("="*60)

for i, model in enumerate(embedding_models[:10], 1):
    pricing = model.get("pricing", {})
    prompt_price = pricing.get("prompt", "N/A")
    request_price = pricing.get("request", "0")

    print(f"\n{i}. {model['name']}")
    print(f"   ID: {model['id']}")
    print(f"   Price: ${prompt_price}/1M tokens")
    if request_price and request_price != "0":
        print(f"   Request fee: ${request_price}/request")
    print(f"   Context: {model.get('context_length', 'N/A')} tokens")

# Check if any are truly free (0.0 price)
free_models = [m for m in embedding_models if get_prompt_price(m) == 0.0]
if free_models:
    print(f"\n" + "="*60)
    print(f"✅ Found {len(free_models)} FREE embedding models!")
    print("="*60)
    for model in free_models:
        print(f"  - {model['id']}")
else:
    print(f"\n" + "="*60)
    print("⚠️  No free embedding models found")
    print("="*60)
    print("\n💡 Recommendation:")
    print("   The cheapest embedding model is:")
    cheapest = embedding_models[0] if embedding_models else None
    if cheapest:
        print(f"   - {cheapest['id']}")
        print(f"   - Price: ${cheapest['pricing'].get('prompt', 'N/A')}/1M tokens")
        print("\n   For a hackathon with limited documents (~100 chunks),")
        print("   this should cost less than $0.01 total.")

print("\n" + "="*60)
