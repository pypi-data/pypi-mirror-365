from gliner2 import GLiNER2
from torch.ao.nn.quantized.functional import threshold
import json

# Load model
extractor = GLiNER2.from_pretrained("/home/urchadezaratiana/fastino-gh/GLiNER2-inter/train_gln2/checkpoints_large_v3/checkpoint-2000")

test_fail = ("Google announced new AI features today in Seattle.", ["company"])

# Test entity extraction on a real model
results = extractor.extract_entities(*test_fail)

text = """Blog Mistral 7B: https://mistral.ai/news/announcing-mistral-7b/ Blog Mixtral 8x7B: https://mistral.ai/news/mixtral-of-experts/ Blog LLaMA 2: https://ai.meta.com/blog/llama-2/ Blog LLaMA 3: https://ai.meta.com/blog/meta-llama-3/ Blog Gemma 2B/7B: https://blog.google/technology/ai/google-gemma-open-models/ Blog Command R+: https://docs.cohere.com/docs/command-r Blog Claude 3 Family: https://www.anthropic.com/news/claude-3-family Blog Phi-2: https://www.microsoft.com/en-us/research/blog/phi-2-the-surprising-power-of-small-language-models/ Blog Qwen: https://github.com/QwenLM/Qwen Blog Yi 34B: https://01.ai/blog/yi Blog Falcon 7B: https://falconllm.tii.ae/ Blog OpenChat: https://github.com/imoneoi/openchat Blog Deepseek LLMs: https://github.com/deepseek-ai/DeepSeek-LLM Blog Nous Hermes 2: https://nousresearch.com/blog"""

result = extractor.extract_json(
    text,
    {
        "blog post": [
            "model::str::name of the model",
            "url::str::link to the blog",
        ]
    }
)

schema = (extractor.create_schema()
    .structure("blog post")
        .field("model name", dtype="str", threshold=0.5)
        .field("url", dtype="str", threshold=0.5)
)

result = extractor.extract(text, schema)

print(json.dumps(result, indent=2))

contract_text = """
Service Agreement between TechCorp LLC and DataSystems Inc., effective January 1, 2024.
Termination clause: 30-day written notice required.
"""

# Multi-task extraction for comprehensive analysis
schema = (extractor.create_schema()
    .entities(["company", "date", "duration", "fee"])
    .classification("contract_type", ["service", "employment", "nda", "partnership"])
    .structure("contract_terms")
        .field("parties", dtype="list")
        .field("effective_date", dtype="str")
        .field("monthly_fee", dtype="str")
        .field("term_length", dtype="str")
        .field("renewal", dtype="str", choices=["automatic", "manual", "none"])
        .field("termination_notice", dtype="str")
)

results = extractor.extract(contract_text, schema)



# Sentiment analysis
result = extractor.classify_text(
    "This laptop has amazing performance but terrible battery life!",
    {"sentiment": ["positive", "negative", "neutral"]}
)
# Output: {'sentiment': 'negative'}

# Multi-aspect classification
result = extractor.classify_text(
    "Great camera quality, decent performance, but poor battery life.",
    {
        "aspects": {
            "labels": ["camera", "performance", "battery", "display", "price"],
            "multi_label": True,
            "cls_threshold": 0.4
        }
    }
)
# Output: {'aspects': ['camera', 'performance', 'battery']}
print("Sentiment Analysis Result:", result)

# Test texts - entities at different positions
test_cases = [
    ("Microsoft announced new AI features today in Seattle.", ["company", "technology", "location"]),
    ("Today in Seattle, Microsoft announced new AI features.", ["company", "technology", "location"]),
    ("The announcement today in Seattle was made by Microsoft.", ["company", "technology", "location"]),
]

print("\nTesting entity extraction on real model:")
print("-" * 50)

for text, entities in test_cases:
    results = extractor.extract_entities(text, entities)
    print(f"\nText: {text}")
    print(f"Extracted: {results}")
    # Check if Microsoft was found
    if 'company' in results.get('entities', {}):
        if 'Microsoft' in results['entities']['company']:
            print("✓ Found Microsoft")
        else:
            print("✗ Microsoft not found!")