"""Debug OpenRouter models API response structure."""
import urllib.request
import json

api_key = "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"

print("="*60)
print("OpenRouter Models API Structure Debug")
print("="*60)

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)

with urllib.request.urlopen(req, timeout=30) as response:
    models_data = json.loads(response.read().decode())

all_models = models_data.get("data", [])
print(f"\nTotal models: {len(all_models)}")

# Print first 3 models in full to see structure
print("\n" + "="*60)
print("First 3 models (full structure):")
print("="*60)

for i, model in enumerate(all_models[:3], 1):
    print(f"\n--- Model {i} ---")
    print(json.dumps(model, indent=2))

# Search for models with "embed" in ID
print("\n" + "="*60)
print("Models with 'embed' in ID:")
print("="*60)

embed_models = [m for m in all_models if "embed" in m.get("id", "").lower()]
print(f"Found {len(embed_models)} models")
for model in embed_models[:10]:
    print(f"  - {model['id']}")

# Check architecture fields
print("\n" + "="*60)
print("Checking architecture.output_modalities:")
print("="*60)

for i, model in enumerate(all_models[:20], 1):
    arch = model.get("architecture", {})
    output_mod = arch.get("output_modalities", [])
    if output_mod:
        print(f"{model['id']}: {output_mod}")
