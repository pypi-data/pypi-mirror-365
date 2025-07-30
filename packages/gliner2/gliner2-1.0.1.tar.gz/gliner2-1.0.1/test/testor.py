"""
GLiNER2 Comprehensive Test Suite
================================

This test suite evaluates GLiNER2 performance across various scenarios:
1. Named Entity Recognition (NER)
2. Text Classification
3. Structured Data Extraction
4. Multi-task Extraction
5. Edge Cases and Robustness
6. Performance Benchmarks
7. Real-world Applications

Usage:
    python test_gliner2.py --model_path "your-model-path"
"""

import time
import json
import statistics
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import argparse

# Assuming GLiNER2 is installed
try:
    from gliner2 import GLiNER2
except ImportError:
    print("GLiNER2 not found. Please install with: pip install gliner2")
    exit(1)


@dataclass
class TestCase:
    """Test case definition"""
    name: str
    text: str
    expected: Dict[str, Any]
    description: str
    category: str


@dataclass
class TestResult:
    """Test result tracking"""
    test_name: str
    category: str
    passed: bool
    predicted: Dict[str, Any]
    expected: Dict[str, Any]
    execution_time: float
    details: str = ""


# extractor = GLiNER2.from_pretrained("")
class GLiNER2TestSuite:
    """Comprehensive test suite for GLiNER2"""

    def __init__(self, model_path: str="/home/urchadezaratiana/fastino-gh/GLiNER2-inter/train_gln2/checkpoints_large_v1/checkpoint-40000"):
        print(f"🚀 Loading GLiNER2 model from: {model_path}")
        start_time = time.time()
        self.extractor = GLiNER2.from_pretrained(model_path)
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds\n")

        self.results: List[TestResult] = []

    def run_all_tests(self):
        """Run all test categories"""
        print("=" * 80)
        print("🧪 STARTING COMPREHENSIVE GLiNER2 TEST SUITE")
        print("=" * 80)

        # Test categories
        test_categories = [
            ("Named Entity Recognition", self._test_ner),
            ("Text Classification", self._test_classification),
            ("Structured Data Extraction", self._test_structured_extraction),
            ("Multi-task Extraction", self._test_multitask),
            ("Edge Cases & Robustness", self._test_edge_cases),
            ("Performance Benchmarks", self._test_performance),
            ("Real-world Applications", self._test_real_world),
            ("Schema Flexibility", self._test_schema_flexibility),
            ("Threshold Sensitivity", self._test_threshold_sensitivity),
            ("Multi-language Support", self._test_multilingual)
        ]

        for category_name, test_func in test_categories:
            print(f"\n📋 {category_name.upper()}")
            print("-" * 60)
            test_func()

        self._generate_report()

    def _test_ner(self):
        """Test Named Entity Recognition capabilities"""
        test_cases = [
            TestCase(
                name="Basic NER",
                text="Apple CEO Tim Cook announced the iPhone 15 in Cupertino, California.",
                expected={"entities": {"company": ["Apple"], "person": ["Tim Cook"], "product": ["iPhone 15"],
                                       "location": ["Cupertino", "California"]}},
                description="Basic entity extraction with common types",
                category="NER"
            ),
            TestCase(
                name="Medical NER",
                text="Patient John Doe, 45, was prescribed 400mg ibuprofen for chronic back pain by Dr. Smith.",
                expected={
                    "entities": {"person": ["John Doe", "Dr. Smith"], "medication": ["ibuprofen"], "dosage": ["400mg"],
                                 "condition": ["chronic back pain"]}},
                description="Medical domain entity extraction",
                category="NER"
            ),
            TestCase(
                name="Financial NER",
                text="Tesla stock (TSLA) rose 5.2% to $245.67 after Q3 earnings beat expectations.",
                expected={"entities": {"company": ["Tesla"], "stock_symbol": ["TSLA"], "percentage": ["5.2%"],
                                       "price": ["$245.67"], "period": ["Q3"]}},
                description="Financial domain with numbers and symbols",
                category="NER"
            ),
            TestCase(
                name="Scientific NER",
                text="Researchers at MIT published findings on CRISPR-Cas9 gene editing in Nature journal.",
                expected={
                    "entities": {"organization": ["MIT"], "technology": ["CRISPR-Cas9"], "field": ["gene editing"],
                                 "publication": ["Nature"]}},
                description="Scientific and technical entity extraction",
                category="NER"
            ),
            TestCase(
                name="Event NER",
                text="The 2024 Olympics will be held in Paris from July 26 to August 11, 2024.",
                expected={"entities": {"event": ["2024 Olympics"], "location": ["Paris"],
                                       "date": ["July 26", "August 11, 2024"]}},
                description="Event and temporal entity extraction",
                category="NER"
            )
        ]

        for test_case in test_cases:
            self._run_ner_test(test_case)

    def _run_ner_test(self, test_case: TestCase):
        """Run individual NER test"""
        start_time = time.time()

        try:
            # Extract entity types from expected results
            entity_types = list(test_case.expected["entities"].keys())

            # Run extraction
            results = self.extractor.extract_entities(test_case.text, entity_types)
            execution_time = time.time() - start_time

            # Evaluate results
            passed = self._evaluate_ner_results(results, test_case.expected)

            result = TestResult(
                test_name=test_case.name,
                category=test_case.category,
                passed=passed,
                predicted=results,
                expected=test_case.expected,
                execution_time=execution_time,
                details=test_case.description
            )

            self.results.append(result)
            self._print_test_result(result)

        except Exception as e:
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=test_case.name,
                category=test_case.category,
                passed=False,
                predicted={},
                expected=test_case.expected,
                execution_time=execution_time,
                details=f"Error: {str(e)}"
            )
            self.results.append(result)
            self._print_test_result(result)

    def _test_classification(self):
        """Test text classification capabilities"""
        test_cases = [
            {
                "name": "Sentiment Analysis",
                "text": "This product is absolutely amazing! Best purchase I've ever made.",
                "task": {"sentiment": ["positive", "negative", "neutral"]},
                "expected": "positive",
                "description": "Basic sentiment classification"
            },
            {
                "name": "Multi-label Classification",
                "text": "Great camera quality but poor battery life and average display.",
                "task": {"aspects": {"labels": ["camera", "battery", "display", "performance"], "multi_label": True}},
                "expected": ["camera", "battery", "display"],
                "description": "Multi-label aspect detection"
            },
            {
                "name": "Intent Classification",
                "text": "I would like to cancel my subscription and get a refund.",
                "task": {"intent": ["cancel", "refund", "support", "purchase", "inquiry"]},
                "expected": "cancel",
                "description": "Customer intent classification"
            },
            {
                "name": "Topic Classification",
                "text": "The Federal Reserve announced a 0.25% interest rate hike to combat inflation.",
                "task": {"topic": ["politics", "finance", "technology", "sports", "health"]},
                "expected": "finance",
                "description": "News topic classification"
            },
            {
                "name": "Urgency Classification",
                "text": "URGENT: Server is down, customers cannot access the website!",
                "task": {"urgency": ["low", "medium", "high", "critical"]},
                "expected": "critical",
                "description": "Urgency level classification"
            }
        ]

        for test_case in test_cases:
            self._run_classification_test(test_case)

    def _run_classification_test(self, test_case: Dict):
        """Run individual classification test"""
        start_time = time.time()

        try:
            results = self.extractor.classify_text(test_case["text"], test_case["task"])
            execution_time = time.time() - start_time

            # Extract predicted result
            task_name = list(test_case["task"].keys())[0]
            predicted = results.get(task_name)

            # Evaluate
            if isinstance(test_case["expected"], list):
                # Multi-label case
                passed = isinstance(predicted, list) and set(predicted) == set(test_case["expected"])
            else:
                # Single-label case
                passed = predicted == test_case["expected"]

            result = TestResult(
                test_name=test_case["name"],
                category="Classification",
                passed=passed,
                predicted=results,
                expected={task_name: test_case["expected"]},
                execution_time=execution_time,
                details=test_case["description"]
            )

            self.results.append(result)
            self._print_test_result(result)

        except Exception as e:
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=test_case["name"],
                category="Classification",
                passed=False,
                predicted={},
                expected={list(test_case["task"].keys())[0]: test_case["expected"]},
                execution_time=execution_time,
                details=f"Error: {str(e)}"
            )
            self.results.append(result)
            self._print_test_result(result)

    def _test_structured_extraction(self):
        """Test structured data extraction"""
        test_cases = [
            {
                "name": "Product Information",
                "text": "iPhone 15 Pro Max with 256GB storage, priced at $1,199, features 5G and improved camera.",
                "schema": {
                    "product": [
                        "name::str",
                        "storage::str",
                        "price::str",
                        "features::list"
                    ]
                },
                "expected_fields": ["name", "storage", "price", "features"],
                "description": "Extract product specifications"
            },
            {
                "name": "Contact Information",
                "text": "Contact John Smith at john.smith@email.com or call (555) 123-4567 for more information.",
                "schema": {
                    "contact": [
                        "name::str",
                        "email::str",
                        "phone::str"
                    ]
                },
                "expected_fields": ["name", "email", "phone"],
                "description": "Extract contact details"
            },
            {
                "name": "Event Details",
                "text": "Tech Conference 2024 will be held at Convention Center on March 15, 2024 from 9 AM to 5 PM.",
                "schema": {
                    "event": [
                        "name::str",
                        "venue::str",
                        "date::str",
                        "start_time::str",
                        "end_time::str"
                    ]
                },
                "expected_fields": ["name", "venue", "date", "start_time", "end_time"],
                "description": "Extract event information"
            },
            {
                "name": "Restaurant Review",
                "text": "Pasta Palace serves excellent Italian food. Great ambiance, friendly staff, reasonable prices. Rating: 4.5/5",
                "schema": {
                    "review": [
                        "restaurant::str",
                        "cuisine::str",
                        "rating::str",
                        "aspects::[ambiance|staff|prices|food]::list"
                    ]
                },
                "expected_fields": ["restaurant", "cuisine", "rating", "aspects"],
                "description": "Extract restaurant review components"
            }
        ]

        for test_case in test_cases:
            self._run_structured_test(test_case)

    def _run_structured_test(self, test_case: Dict):
        """Run individual structured extraction test"""
        start_time = time.time()

        try:
            results = self.extractor.extract_json(test_case["text"], test_case["schema"])
            execution_time = time.time() - start_time

            # Evaluate structure
            schema_name = list(test_case["schema"].keys())[0]
            predicted_instances = results.get(schema_name, [])

            passed = False
            if predicted_instances:
                # Check if required fields are present
                first_instance = predicted_instances[0]
                extracted_fields = set(first_instance.keys())
                expected_fields = set(test_case["expected_fields"])

                # Consider test passed if most expected fields are extracted
                coverage = len(extracted_fields & expected_fields) / len(expected_fields)
                passed = coverage >= 0.6  # 60% field coverage threshold

            result = TestResult(
                test_name=test_case["name"],
                category="Structured",
                passed=passed,
                predicted=results,
                expected={"required_fields": test_case["expected_fields"]},
                execution_time=execution_time,
                details=test_case["description"]
            )

            self.results.append(result)
            self._print_test_result(result)

        except Exception as e:
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=test_case["name"],
                category="Structured",
                passed=False,
                predicted={},
                expected={"required_fields": test_case["expected_fields"]},
                execution_time=execution_time,
                details=f"Error: {str(e)}"
            )
            self.results.append(result)
            self._print_test_result(result)

    def _test_multitask(self):
        """Test multi-task extraction capabilities"""
        test_cases = [
            {
                "name": "News Article Analysis",
                "text": "Apple CEO Tim Cook announced iPhone 15 launch. The innovative features received positive market response.",
                "description": "Combined entity, classification, and structure extraction",
            },
            {
                "name": "Medical Report Processing",
                "text": "Patient John Doe showed improvement after 200mg medication. Condition appears stable with positive outlook.",
                "description": "Medical multi-task extraction",
            },
            {
                "name": "Customer Feedback Analysis",
                "text": "Amazon Prime delivery was fast but the package was damaged. Need immediate replacement.",
                "description": "Customer service multi-task analysis",
            }
        ]

        for test_case in test_cases:
            self._run_multitask_test(test_case)

    def _run_multitask_test(self, test_case: Dict):
        """Run multi-task extraction test"""
        start_time = time.time()

        try:
            # Create comprehensive schema
            schema = (self.extractor.create_schema()
                      .entities(["person", "company", "product", "location", "medication", "condition"])
                      .classification("sentiment", ["positive", "negative", "neutral"])
                      .classification("urgency", ["low", "medium", "high"])
                      .structure("key_info")
                      .field("subject", dtype="str")
                      .field("action", dtype="str")
                      .field("details", dtype="list")
                      )

            results = self.extractor.extract(test_case["text"], schema)
            execution_time = time.time() - start_time

            # Evaluate based on presence of different task types
            has_entities = bool(results.get("entities", {}).get("person") or
                                results.get("entities", {}).get("company") or
                                results.get("entities", {}).get("product"))
            has_classification = bool(results.get("sentiment") or results.get("urgency"))
            has_structure = bool(results.get("key_info"))

            # Pass if at least 2 out of 3 task types work
            passed = sum([has_entities, has_classification, has_structure]) >= 2

            result = TestResult(
                test_name=test_case["name"],
                category="Multi-task",
                passed=passed,
                predicted=results,
                expected={"entities": True, "classification": True, "structure": True},
                execution_time=execution_time,
                details=test_case["description"]
            )

            self.results.append(result)
            self._print_test_result(result)

        except Exception as e:
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=test_case["name"],
                category="Multi-task",
                passed=False,
                predicted={},
                expected={"entities": True, "classification": True, "structure": True},
                execution_time=execution_time,
                details=f"Error: {str(e)}"
            )
            self.results.append(result)
            self._print_test_result(result)

    def _test_edge_cases(self):
        """Test edge cases and robustness"""
        test_cases = [
            {
                "name": "Empty Text",
                "text": "",
                "description": "Handle empty input gracefully"
            },
            {
                "name": "Very Short Text",
                "text": "Hi.",
                "description": "Handle minimal input"
            },
            {
                "name": "Very Long Text",
                "text": "This is a very long text. " * 100,
                "description": "Handle long input sequences"
            },
            {
                "name": "Special Characters",
                "text": "Contact @user123 via email: user@domain.com or visit https://example.com #urgent",
                "description": "Handle special characters and URLs"
            },
            {
                "name": "Mixed Languages",
                "text": "Hello mundo! This is a mixed language text with français and español words.",
                "description": "Handle mixed language input"
            },
            {
                "name": "Numbers and Symbols",
                "text": "Price: $1,234.56 (±5%) Model: ABC-123 Serial: #789XYZ",
                "description": "Handle numbers, currency, and symbols"
            },
            {
                "name": "Repeated Entities",
                "text": "Apple Apple Apple released iPhone iPhone iPhone in California California.",
                "description": "Handle repeated entities"
            }
        ]

        for test_case in test_cases:
            self._run_edge_case_test(test_case)

    def _run_edge_case_test(self, test_case: Dict):
        """Run edge case test"""
        start_time = time.time()

        try:
            # Simple entity extraction test
            results = self.extractor.extract_entities(
                test_case["text"],
                ["person", "company", "product", "location"]
            )
            execution_time = time.time() - start_time

            # Pass if no errors occur
            passed = True

            result = TestResult(
                test_name=test_case["name"],
                category="Edge Cases",
                passed=passed,
                predicted=results,
                expected={"no_error": True},
                execution_time=execution_time,
                details=test_case["description"]
            )

            self.results.append(result)
            self._print_test_result(result)

        except Exception as e:
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=test_case["name"],
                category="Edge Cases",
                passed=False,
                predicted={},
                expected={"no_error": True},
                execution_time=execution_time,
                details=f"Error: {str(e)}"
            )
            self.results.append(result)
            self._print_test_result(result)

    def _test_performance(self):
        """Test performance benchmarks"""
        texts = [
            "Short text for speed test.",
            "Medium length text with more content and several entities like Apple, Tim Cook, and iPhone for performance evaluation.",
            "Very long text with extensive content. " + "This sentence contains multiple entities and should test the model's performance on longer sequences. " * 20
        ]

        for i, text in enumerate(texts):
            test_name = f"Performance Test {i + 1} ({'Short' if i == 0 else 'Medium' if i == 1 else 'Long'} Text)"
            self._run_performance_test(test_name, text)

    def _run_performance_test(self, test_name: str, text: str):
        """Run performance test"""
        execution_times = []

        # Run multiple times for average
        for _ in range(5):
            start_time = time.time()
            try:
                results = self.extractor.extract_entities(text, ["person", "company", "product", "location"])
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
            except Exception as e:
                execution_times.append(float('inf'))

        avg_time = statistics.mean(execution_times)
        passed = avg_time < 10.0  # 10 second threshold

        result = TestResult(
            test_name=test_name,
            category="Performance",
            passed=passed,
            predicted={"avg_time": avg_time, "times": execution_times},
            expected={"threshold": 10.0},
            execution_time=avg_time,
            details=f"Average execution time over 5 runs"
        )

        self.results.append(result)
        self._print_test_result(result)

    def _test_real_world(self):
        """Test real-world application scenarios"""
        scenarios = [
            {
                "name": "Email Processing",
                "text": "From: john.doe@company.com\nTo: team@startup.com\nSubject: Project Update\n\nHi team, the Q3 deadline is approaching on September 30th. Please prioritize tasks accordingly.",
                "description": "Email content extraction"
            },
            {
                "name": "Social Media Post",
                "text": "Just visited @AppleStore and bought the new #iPhone15Pro! Amazing camera quality 📸 #tech #apple",
                "description": "Social media content analysis"
            },
            {
                "name": "Legal Document",
                "text": "Party A (TechCorp Inc.) agrees to provide services to Party B (ClientCorp LLC) for $50,000 effective January 1, 2024.",
                "description": "Legal document processing"
            },
            {
                "name": "Scientific Abstract",
                "text": "CRISPR-Cas9 gene editing showed 95% efficiency in treating sickle cell disease patients at Stanford Medical Center.",
                "description": "Scientific literature processing"
            }
        ]

        for scenario in scenarios:
            self._run_real_world_test(scenario)

    def _run_real_world_test(self, scenario: Dict):
        """Run real-world scenario test"""
        start_time = time.time()

        try:
            # Create appropriate schema based on scenario
            if "Email" in scenario["name"]:
                schema = (self.extractor.create_schema()
                          .entities(["email", "person", "date", "company"])
                          .classification("urgency", ["low", "medium", "high"])
                          .structure("email_info")
                          .field("sender", dtype="str")
                          .field("recipient", dtype="str")
                          .field("subject", dtype="str")
                          .field("deadline", dtype="str")
                          )
            elif "Social" in scenario["name"]:
                schema = (self.extractor.create_schema()
                          .entities(["product", "company", "hashtag"])
                          .classification("sentiment", ["positive", "negative", "neutral"])
                          )
            elif "Legal" in scenario["name"]:
                schema = (self.extractor.create_schema()
                          .entities(["company", "person", "amount", "date"])
                          .structure("contract")
                          .field("party_a", dtype="str")
                          .field("party_b", dtype="str")
                          .field("amount", dtype="str")
                          .field("effective_date", dtype="str")
                          )
            else:  # Scientific
                schema = (self.extractor.create_schema()
                          .entities(["technology", "condition", "organization", "percentage"])
                          .classification("field", ["medicine", "technology", "biology", "chemistry"])
                          )

            results = self.extractor.extract(scenario["text"], schema)
            execution_time = time.time() - start_time

            # Pass if we get reasonable results
            has_results = bool(results.get("entities") or
                               any(k for k in results.keys() if k not in ["entities"]))

            result = TestResult(
                test_name=scenario["name"],
                category="Real-world",
                passed=has_results,
                predicted=results,
                expected={"has_results": True},
                execution_time=execution_time,
                details=scenario["description"]
            )

            self.results.append(result)
            self._print_test_result(result)

        except Exception as e:
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=scenario["name"],
                category="Real-world",
                passed=False,
                predicted={},
                expected={"has_results": True},
                execution_time=execution_time,
                details=f"Error: {str(e)}"
            )
            self.results.append(result)
            self._print_test_result(result)

    def _test_schema_flexibility(self):
        """Test schema building flexibility"""
        test_cases = [
            {
                "name": "Auto-finish Structure",
                "description": "Test automatic structure finishing"
            },
            {
                "name": "Field Order Preservation",
                "description": "Test field order preservation in results"
            },
            {
                "name": "Mixed Schema Types",
                "description": "Test mixing different schema components"
            }
        ]

        text = "Apple CEO Tim Cook announced iPhone 15. Very exciting news!"

        for test_case in test_cases:
            start_time = time.time()

            try:
                if test_case["name"] == "Auto-finish Structure":
                    # Test auto-finishing by calling entities after structure
                    schema = (self.extractor.create_schema()
                              .structure("product")
                              .field("name", dtype="str")
                              .field("company", dtype="str")
                              .entities(["person"])  # This should auto-finish structure
                              )

                elif test_case["name"] == "Field Order Preservation":
                    # Test field ordering
                    schema = (self.extractor.create_schema()
                              .structure("info")
                              .field("third", dtype="str")
                              .field("first", dtype="str")
                              .field("second", dtype="str")
                              )

                else:  # Mixed Schema Types
                    schema = (self.extractor.create_schema()
                              .entities(["person", "company"])
                              .classification("sentiment", ["positive", "negative"])
                              .structure("announcement")
                              .field("product", dtype="str")
                              .field("company", dtype="str")
                              )

                results = self.extractor.extract(text, schema)
                execution_time = time.time() - start_time

                # Pass if no errors occur
                passed = True

                result = TestResult(
                    test_name=test_case["name"],
                    category="Schema Flexibility",
                    passed=passed,
                    predicted=results,
                    expected={"no_error": True},
                    execution_time=execution_time,
                    details=test_case["description"]
                )

                self.results.append(result)
                self._print_test_result(result)

            except Exception as e:
                execution_time = time.time() - start_time
                result = TestResult(
                    test_name=test_case["name"],
                    category="Schema Flexibility",
                    passed=False,
                    predicted={},
                    expected={"no_error": True},
                    execution_time=execution_time,
                    details=f"Error: {str(e)}"
                )
                self.results.append(result)
                self._print_test_result(result)

    def _test_threshold_sensitivity(self):
        """Test threshold sensitivity"""
        text = "Apple CEO Tim Cook announced iPhone 15 launch in California."
        thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]

        for threshold in thresholds:
            start_time = time.time()

            try:
                results = self.extractor.extract_entities(
                    text,
                    ["person", "company", "product", "location"],
                    threshold=threshold
                )
                execution_time = time.time() - start_time

                # Count extracted entities
                entity_count = sum(len(entities) for entities in results.get("entities", {}).values())

                result = TestResult(
                    test_name=f"Threshold {threshold}",
                    category="Threshold Sensitivity",
                    passed=True,  # Always pass, we're just observing
                    predicted={"entity_count": entity_count, "results": results},
                    expected={"threshold": threshold},
                    execution_time=execution_time,
                    details=f"Entity extraction with threshold {threshold}"
                )

                self.results.append(result)
                self._print_test_result(result)

            except Exception as e:
                execution_time = time.time() - start_time
                result = TestResult(
                    test_name=f"Threshold {threshold}",
                    category="Threshold Sensitivity",
                    passed=False,
                    predicted={},
                    expected={"threshold": threshold},
                    execution_time=execution_time,
                    details=f"Error: {str(e)}"
                )
                self.results.append(result)
                self._print_test_result(result)

    def _test_multilingual(self):
        """Test multilingual capabilities (if supported)"""
        test_cases = [
            {
                "name": "Spanish Text",
                "text": "El CEO de Apple, Tim Cook, anunció el iPhone 15 en California.",
                "language": "Spanish"
            },
            {
                "name": "French Text",
                "text": "Le PDG d'Apple, Tim Cook, a annoncé l'iPhone 15 en Californie.",
                "language": "French"
            },
            {
                "name": "German Text",
                "text": "Apple CEO Tim Cook kündigte das iPhone 15 in Kalifornien an.",
                "language": "German"
            }
        ]

        for test_case in test_cases:
            start_time = time.time()

            try:
                results = self.extractor.extract_entities(
                    test_case["text"],
                    ["person", "company", "product", "location"]
                )
                execution_time = time.time() - start_time

                # Pass if we extract some entities
                has_entities = any(results.get("entities", {}).values())

                result = TestResult(
                    test_name=test_case["name"],
                    category="Multilingual",
                    passed=has_entities,
                    predicted=results,
                    expected={"has_entities": True},
                    execution_time=execution_time,
                    details=f"{test_case['language']} language processing"
                )

                self.results.append(result)
                self._print_test_result(result)

            except Exception as e:
                execution_time = time.time() - start_time
                result = TestResult(
                    test_name=test_case["name"],
                    category="Multilingual",
                    passed=False,
                    predicted={},
                    expected={"has_entities": True},
                    execution_time=execution_time,
                    details=f"Error: {str(e)}"
                )
                self.results.append(result)
                self._print_test_result(result)

    def _evaluate_ner_results(self, predicted: Dict, expected: Dict) -> bool:
        """Evaluate NER results"""
        pred_entities = predicted.get("entities", {})
        exp_entities = expected.get("entities", {})

        total_score = 0
        total_entities = 0

        for entity_type, exp_values in exp_entities.items():
            pred_values = pred_entities.get(entity_type, [])

            if not exp_values:
                continue

            total_entities += len(exp_values)

            # Calculate overlap
            pred_set = {v.lower() for v in pred_values}
            exp_set = {v.lower() for v in exp_values}

            overlap = len(pred_set & exp_set)
            total_score += overlap

        # Pass if we get at least 50% accuracy
        accuracy = total_score / max(total_entities, 1)
        return accuracy >= 0.5

    def _print_test_result(self, result: TestResult):
        """Print individual test result"""
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"  {status} {result.test_name:<25} ({result.execution_time:.3f}s)")

        if not result.passed or result.category in ["Performance", "Threshold Sensitivity"]:
            print(f"    📝 {result.details}")

        # Print prediction details for some categories
        if result.category in ["Performance", "Threshold Sensitivity", "Multilingual"]:
            if "entity_count" in str(result.predicted):
                count = result.predicted.get("entity_count", 0)
                print(f"    📊 Extracted {count} entities")
            elif "avg_time" in str(result.predicted):
                avg_time = result.predicted.get("avg_time", 0)
                print(f"    ⏱️ Average time: {avg_time:.3f}s")

        if not result.passed and result.details.startswith("Error"):
            print(f"    🔍 Expected: {result.expected}")
            print(f"    🔍 Got: {result.predicted}")

    def _generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)

        # Overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        pass_rate = (passed_tests / total_tests) * 100

        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Pass Rate: {pass_rate:.1f}%")

        # Performance statistics
        execution_times = [r.execution_time for r in self.results if r.execution_time > 0]
        if execution_times:
            avg_time = statistics.mean(execution_times)
            median_time = statistics.median(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)

            print(f"\n⏱️ PERFORMANCE METRICS:")
            print(f"   Average execution time: {avg_time:.3f}s")
            print(f"   Median execution time: {median_time:.3f}s")
            print(f"   Max execution time: {max_time:.3f}s")
            print(f"   Min execution time: {min_time:.3f}s")

        # Category breakdown
        category_stats = defaultdict(lambda: {"total": 0, "passed": 0})
        for result in self.results:
            category_stats[result.category]["total"] += 1
            if result.passed:
                category_stats[result.category]["passed"] += 1

        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, stats in category_stats.items():
            pass_rate = (stats["passed"] / stats["total"]) * 100
            print(f"   {category:<20}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")

        # Failed tests details
        failed_tests = [r for r in self.results if not r.passed]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   {test.category} - {test.test_name}: {test.details}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if pass_rate >= 90:
            print("   🎉 Excellent performance! Model is working very well across all test categories.")
        elif pass_rate >= 75:
            print("   👍 Good performance! Some areas might need fine-tuning.")
        elif pass_rate >= 50:
            print("   ⚠️ Moderate performance. Consider additional training or parameter tuning.")
        else:
            print("   🚨 Low performance. Model may need significant improvements.")

        # Save detailed results
        self._save_detailed_results()

    def _save_detailed_results(self):
        """Save detailed results to JSON file"""
        detailed_results = {
            "summary": {
                "total_tests": len(self.results),
                "passed_tests": sum(1 for r in self.results if r.passed),
                "pass_rate": (sum(1 for r in self.results if r.passed) / len(self.results)) * 100,
                "avg_execution_time": statistics.mean([r.execution_time for r in self.results if r.execution_time > 0])
            },
            "tests": [
                {
                    "name": r.test_name,
                    "category": r.category,
                    "passed": r.passed,
                    "execution_time": r.execution_time,
                    "details": r.details,
                    "predicted": str(r.predicted)[:500],  # Truncate for readability
                    "expected": str(r.expected)[:500]
                }
                for r in self.results
            ]
        }

        with open("gliner2_test_results.json", "w") as f:
            json.dump(detailed_results, f, indent=2)

        print(f"\n💾 Detailed results saved to: gliner2_test_results.json")


def main():
    """Main function to run tests"""
    parser = argparse.ArgumentParser(description="GLiNER2 Comprehensive Test Suite")
    parser.add_argument("--model_path", type=str, default="/home/urchadezaratiana/fastino-gh/GLiNER2-inter/train_gln2/checkpoints_large_v1/checkpoint-40000",
                        help="Path to GLiNER2 model (local path or HuggingFace model name)")
    parser.add_argument("--categories", type=str, nargs="*",
                        help="Specific test categories to run (default: all)")

    args = parser.parse_args()

    # Create and run test suite
    test_suite = GLiNER2TestSuite(args.model_path)
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()