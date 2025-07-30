# GLiNER2: Unified Schema-Based Information Extraction

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/gliner2.svg)](https://badge.fury.io/py/gliner2)
[![Downloads](https://pepy.tech/badge/gliner2)](https://pepy.tech/project/gliner2)

> *Extract entities, classify text, and parse structured data—all in one efficient model.*

GLiNER2 unifies **Named Entity Recognition**, **Text Classification**, and **Structured Data Extraction** into a single 205M parameter model. It provides efficient CPU-based inference without requiring complex pipelines or external API dependencies.

## ✨ Why GLiNER2?

- **🎯 One Model, Three Tasks**: Entities, classification, and structured data in a single forward pass
- **💻 CPU First**: Lightning-fast inference on standard hardware—no GPU required
- **🛡️ Privacy**: 100% local processing, zero external dependencies

## 🚀 Installation & Quick Start

```bash
pip install gliner2
```

```python
from gliner2 import GLiNER2

# Load model once, use everywhere
extractor = GLiNER2.from_pretrained("fastino/gliner2-base")

# Extract entities in one line
text = "Apple CEO Tim Cook announced iPhone 15 in Cupertino yesterday."
result = extractor.extract_entities(text, ["company", "person", "product", "location"])

print(result)
# {'entities': {'company': ['Apple'], 'person': ['Tim Cook'], 'product': ['iPhone 15'], 'location': ['Cupertino']}}
```

## 📦 Available Models

| Model | Parameters | Description | Use Case                                         |
|-------|------------|-------------|--------------------------------------------------|
| `fastino/gliner2-base-0207` | 205M | base size   | Extraction / classification |
| `fastino/gliner2-large-1006` | 340M | large size  | Extraction / classification                      |

All models are available on [Hugging Face Hub](https://huggingface.co/fastino) and support the same API.

## 🎯 Core Capabilities

### 1. Entity Extraction
Extract named entities with optional descriptions for precision:

```python
# Basic entity extraction
entities = extractor.extract_entities(
    "Patient received 400mg ibuprofen for severe headache at 2 PM.",
    ["medication", "dosage", "symptom", "time"]
)
# Output: {'entities': {'medication': ['ibuprofen'], 'dosage': ['400mg'], 'symptom': ['severe headache'], 'time': ['2 PM']}}

# Enhanced with descriptions for medical accuracy
entities = extractor.extract_entities(
    "Patient received 400mg ibuprofen for severe headache at 2 PM.",
    {
        "medication": "Names of drugs, medications, or pharmaceutical substances",
        "dosage": "Specific amounts like '400mg', '2 tablets', or '5ml'",
        "symptom": "Medical symptoms, conditions, or patient complaints",
        "time": "Time references like '2 PM', 'morning', or 'after lunch'"
    }
)
# Same output but with higher accuracy due to context descriptions
```

### 2. Text Classification
Single or multi-label classification with configurable confidence:

```python
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
```

### 3. Structured Data Extraction
Parse complex structured information with field-level control:

```python
# Product information extraction
text = "iPhone 15 Pro Max with 256GB storage, A17 Pro chip, priced at $1199. Available in titanium and black colors."

result = extractor.extract_json(
    text,
    {
        "product": [
            "name::str::Full product name and model",
            "storage::str::Storage capacity like 256GB or 1TB", 
            "processor::str::Chip or processor information",
            "price::str::Product price with currency",
            "colors::list::Available color options"
        ]
    }
)
# Output: {
#     'product': [{
#         'name': 'iPhone 15 Pro Max',
#         'storage': '256GB', 
#         'processor': 'A17 Pro chip',
#         'price': '$1199',
#         'colors': ['titanium', 'black']
#     }]
# }

# Multiple structured entities
text = "Apple Inc. headquarters in Cupertino launched iPhone 15 for $999 and MacBook Air for $1299."

result = extractor.extract_json(
    text,
    {
        "company": [
            "name::str::Company name",
            "location::str::Company headquarters or office location"
        ],
        "products": [
            "name::str::Product name and model",
            "price::str::Product retail price"
        ]
    }
)
# Output: {
#     'company': [{'name': 'Apple Inc.', 'location': 'Cupertino'}],
#     'products': [
#         {'name': 'iPhone 15', 'price': '$999'},
#         {'name': 'MacBook Air', 'price': '$1299'}
#     ]
# }
```

### 4. Multi-Task Schema Composition
Combine all extraction types when you need comprehensive analysis:

```python
# Use create_schema() for multi-task scenarios
schema = (extractor.create_schema()
    # Extract key entities
    .entities({
        "person": "Names of people, executives, or individuals",
        "company": "Organization, corporation, or business names", 
        "product": "Products, services, or offerings mentioned"
    })
    
    # Classify the content
    .classification("sentiment", ["positive", "negative", "neutral"])
    .classification("category", ["technology", "business", "finance", "healthcare"])
    
    # Extract structured product details
    .structure("product_info")
        .field("name", dtype="str")
        .field("price", dtype="str")
        .field("features", dtype="list")
        .field("availability", dtype="str", choices=["in_stock", "pre_order", "sold_out"])
)

# Comprehensive extraction in one pass
text = "Apple CEO Tim Cook unveiled the revolutionary iPhone 15 Pro for $999. The device features an A17 Pro chip and titanium design."

results = extractor.extract(text, schema)
# Output: {
#     'entities': {
#         'person': ['Tim Cook'], 
#         'company': ['Apple'], 
#         'product': ['iPhone 15 Pro']
#     },
#     'sentiment': 'positive',
#     'category': 'technology', 
#     'product_info': [{
#         'name': 'iPhone 15 Pro',
#         'price': '$999',
#         'features': ['A17 Pro chip', 'titanium design'],
#         'availability': 'in_stock'
#     }]
# }
```

## 🏭 Example Usage Scenarios

### Financial Document Processing

```python
financial_text = """
Transaction Report: Goldman Sachs processed a $2.5M equity trade for Tesla Inc. 
on March 15, 2024. Commission: $1,250. Status: Completed.
"""

# Extract structured financial data
result = extractor.extract_json(
    financial_text,
    {
        "transaction": [
            "broker::str::Financial institution or brokerage firm",
            "amount::str::Transaction amount with currency",
            "security::str::Stock, bond, or financial instrument",
            "date::str::Transaction date",
            "commission::str::Fees or commission charged", 
            "status::str::Transaction status",
            "type::[equity|bond|option|future|forex]::str::Type of financial instrument"
        ]
    }
)
# Output: {
#     'transaction': [{
#         'broker': 'Goldman Sachs',
#         'amount': '$2.5M', 
#         'security': 'Tesla Inc.',
#         'date': 'March 15, 2024',
#         'commission': '$1,250',
#         'status': 'Completed',
#         'type': 'equity'
#     }]
# }
```

### Healthcare Information Extraction

```python
medical_record = """
Patient: Sarah Johnson, 34, presented with acute chest pain and shortness of breath.
Prescribed: Lisinopril 10mg daily, Metoprolol 25mg twice daily.
Follow-up scheduled for next Tuesday.
"""

result = extractor.extract_json(
    medical_record,
    {
        "patient_info": [
            "name::str::Patient full name",
            "age::str::Patient age",
            "symptoms::list::Reported symptoms or complaints"
        ],
        "prescriptions": [
            "medication::str::Drug or medication name",
            "dosage::str::Dosage amount and frequency",
            "frequency::str::How often to take the medication"
        ]
    }
)
# Output: {
#     'patient_info': [{
#         'name': 'Sarah Johnson',
#         'age': '34',
#         'symptoms': ['acute chest pain', 'shortness of breath']
#     }],
#     'prescriptions': [
#         {'medication': 'Lisinopril', 'dosage': '10mg', 'frequency': 'daily'},
#         {'medication': 'Metoprolol', 'dosage': '25mg', 'frequency': 'twice daily'}
#     ]
# }
```

### Legal Contract Analysis

```python
contract_text = """
Service Agreement between TechCorp LLC and DataSystems Inc., effective January 1, 2024.
Monthly fee: $15,000. Contract term: 24 months with automatic renewal.
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
# Output: {
#     'entities': {
#         'company': ['TechCorp LLC', 'DataSystems Inc.'],
#         'date': ['January 1, 2024'],
#         'duration': ['24 months'],
#         'fee': ['$15,000']
#     },
#     'contract_type': 'service',
#     'contract_terms': [{
#         'parties': ['TechCorp LLC', 'DataSystems Inc.'],
#         'effective_date': 'January 1, 2024',
#         'monthly_fee': '$15,000',
#         'term_length': '24 months', 
#         'renewal': 'automatic',
#         'termination_notice': '30-day written notice'
#     }]
# }
```

## ⚙️ Advanced Configuration

### Custom Confidence Thresholds

```python
# High-precision extraction for critical fields
result = extractor.extract_json(
    text,
    {
        "financial_data": [
            "account_number::str::Bank account number",  # default threshold
            "amount::str::Transaction amount",           # default threshold  
            "routing_number::str::Bank routing number"   # default threshold
        ]
    },
    threshold=0.9  # High confidence for all fields
)

# Per-field thresholds using schema builder (for multi-task scenarios)
schema = (extractor.create_schema()
    .structure("sensitive_data")
        .field("ssn", dtype="str", threshold=0.95)         # Highest precision
        .field("email", dtype="str", threshold=0.8)        # Medium precision  
        .field("phone", dtype="str", threshold=0.7)        # Lower precision
)
```

### Field Types and Constraints

```python
# Structured extraction with choices and types
result = extractor.extract_json(
    "Premium subscription at $99/month with mobile and web access.",
    {
        "subscription": [
            "tier::[basic|premium|enterprise]::str::Subscription level",
            "price::str::Monthly or annual cost",
            "billing::[monthly|annual]::str::Billing frequency", 
            "features::[mobile|web|api|analytics]::list::Included features"
        ]
    }
)
# Output: {
#     'subscription': [{
#         'tier': 'premium',
#         'price': '$99/month', 
#         'billing': 'monthly',
#         'features': ['mobile', 'web']
#     }]
# }
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 📚 Citation

If you use GLiNER2 in your research, please cite:

```bibtex
@misc{zaratiana2025gliner2efficientmultitaskinformation,
      title={GLiNER2: An Efficient Multi-Task Information Extraction System with Schema-Driven Interface}, 
      author={Urchade Zaratiana and Gil Pasternak and Oliver Boyd and George Hurn-Maloney and Ash Lewis},
      year={2025},
      eprint={2507.18546},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2507.18546}, 
}
```

## 🙏 Acknowledgments

Built upon the original [GLiNER](https://github.com/urchade/GLiNER) architecture by the team at [Fastino AI](https://fastino.ai).

---

<div align="center">
    <strong>Ready to extract insights from your data?</strong><br>
    <code>pip install gliner2</code>
</div>