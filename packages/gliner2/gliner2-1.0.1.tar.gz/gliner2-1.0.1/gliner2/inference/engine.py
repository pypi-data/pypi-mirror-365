"""
GLiNER2 - Advanced Information Extraction Engine

This module provides an intuitive schema-based interface for extracting
structured information from text using the GLiNER2 model.

Quick Examples
--------------
Extract entities:
    >>> extractor = GLiNER2.from_pretrained("your-model")
    >>> results = extractor.extract_entities(
    ...     "Apple released iPhone 15 in September 2023.",
    ...     ["company", "product", "date"]
    ... )
    >>> # {'entities': {'company': ['Apple'], 'product': ['iPhone 15'], 'date': ['September 2023']}}

Extract structured data:
    >>> results = extractor.extract_json(
    ...     "Contact John Doe at john@email.com or call 555-1234.",
    ...     {"contact": ["name:str", "email:str", "phone"]}
    ... )
    >>> # {'contact': [{'name': 'John Doe', 'email': 'john@email.com', 'phone': ['555-1234']}]}

Complex multi-task extraction:
    >>> schema = (extractor.create_schema()
    ...     .entities(["person", "location"])
    ...     .classification("sentiment", ["positive", "negative", "neutral"])
    ...     .structure("product_review")
    ...         .field("product", dtype="str")
    ...         .field("rating", dtype="str", choices=["1", "2", "3", "4", "5"])
    ...         .field("pros", dtype="list")
    ...         .field("cons", dtype="list")
    ... )
    >>> results = extractor.extract(review_text, schema)
"""

from typing import Any, Dict, List, Optional, Literal, Union, Tuple
from collections import OrderedDict
import torch
from gliner2.model import Extractor


class StructureBuilder:
    """
    Builder for structured data schemas - auto-finishes when parent method is called.

    This builder allows fluent construction of structured data with multiple fields.
    It automatically completes when any Schema method is called, ensuring
    proper schema construction without explicit finish() calls.
    """

    def __init__(self, schema: 'Schema', parent: str):
        self.schema = schema
        self.parent = parent
        self.fields = OrderedDict()  # Preserve field order
        self.descriptions = OrderedDict()  # Preserve description order
        self.field_order = []  # Track field addition order
        self._finished = False

    def field(
            self,
            name: str,
            dtype: Literal["str", "list"] = "list",
            choices: Optional[List[str]] = None,
            description: Optional[str] = None,
            threshold: Optional[float] = None
    ) -> 'StructureBuilder':
        """
        Add a field to the structured data.

        Parameters
        ----------
        name : str
            The name of the field to extract.
        dtype : {"str", "list"}, default="list"
            The data type of the field:
            - "str": Extract a single value (best match)
            - "list": Extract multiple values
        choices : List[str], optional
            If provided, the field becomes a classification field where values
            must be selected from these choices. For dtype="str", selects the
            best matching choice. For dtype="list", can select multiple choices.
        description : str, optional
            Human-readable description of what this field represents. Used to
            improve extraction accuracy through better context understanding.
        threshold : float, optional
            Custom confidence threshold for this field (overrides default).
            Values must be between 0 and 1.

        Returns
        -------
        StructureBuilder
            Returns self for method chaining.

        Examples
        --------
        >>> # Simple field extraction
        >>> builder.field("address")

        >>> # Single-choice classification
        >>> builder.field("priority", dtype="str", choices=["high", "medium", "low"])

        >>> # Multi-choice classification
        >>> builder.field("amenities", dtype="list",
        ...               choices=["wifi", "parking", "pool", "gym"],
        ...               description="Available amenities at the location")

        >>> # Field with custom threshold
        >>> builder.field("phone", threshold=0.8)

        >>> # High-precision field
        >>> builder.field("email", dtype="str", threshold=0.9,
        ...               description="Contact email address")
        """
        # Store field in schema format
        self.fields[name] = {"value": "", "choices": choices} if choices else ""
        self.field_order.append(name)  # Track order

        if description:
            self.descriptions[name] = description

        # Store metadata including threshold
        self.schema._store_field_metadata(self.parent, name, dtype, threshold, choices)
        return self

    def _auto_finish(self):
        """Automatically finish this structure when needed."""
        if not self._finished:
            # Store field order for this structure
            self.schema._store_field_order(self.parent, self.field_order)

            self.schema.schema["json_structures"].append({self.parent: self.fields})

            if self.descriptions:
                if "json_descriptions" not in self.schema.schema:
                    self.schema.schema["json_descriptions"] = {}
                self.schema.schema["json_descriptions"][self.parent] = self.descriptions

            self._finished = True

    def __getattr__(self, name):
        """Auto-finish when any schema method is called."""
        if hasattr(self.schema, name):
            self._auto_finish()
            return getattr(self.schema, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


class Schema:
    """Main schema builder for extraction tasks."""

    def __init__(self):
        self.schema = {
            "json_structures": [],
            "classifications": [],
            "entities": OrderedDict(),  # Preserve entity order
            "json_descriptions": {},
            "entity_descriptions": OrderedDict()  # Preserve description order
        }
        # Store metadata for thresholds and types
        self._field_metadata = {}  # "parent.field" -> {dtype, threshold, choices}
        self._entity_metadata = {}  # "entity_name" -> {dtype, threshold}
        self._field_orders = {}  # "parent" -> [field1, field2, ...]
        self._entity_order = []  # [entity1, entity2, ...]
        self._active_structure_builder = None  # Track active structure builder

    def _store_field_metadata(self, parent: str, field: str, dtype: str, threshold: Optional[float],
                              choices: Optional[List[str]]):
        """Store field configuration."""
        # Validate threshold if provided
        if threshold is not None:
            if not 0 <= threshold <= 1:
                raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")

        key = f"{parent}.{field}"
        self._field_metadata[key] = {"dtype": dtype, "threshold": threshold, "choices": choices}

    def _store_entity_metadata(self, entity: str, dtype: str, threshold: Optional[float]):
        """Store entity configuration."""
        # Validate threshold if provided
        if threshold is not None:
            if not 0 <= threshold <= 1:
                raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")

        self._entity_metadata[entity] = {"dtype": dtype, "threshold": threshold}

    def _store_field_order(self, parent: str, field_order: List[str]):
        """Store field order for a structure."""
        self._field_orders[parent] = field_order

    def structure(self, name: str) -> StructureBuilder:
        """
        Start building a structured data schema for hierarchical extraction.

        This method creates a builder for defining structured data with multiple
        fields. The structure will extract repeated instances of the defined
        pattern from the text.

        Parameters
        ----------
        name : str
            The name of the structure (e.g., "product", "address", "event").
            This will be the key in the results dictionary.

        Returns
        -------
        StructureBuilder
            A builder object for adding fields to this structure.

        Examples
        --------
        >>> # Extract product information
        >>> schema = (extractor.create_schema()
        ...     .structure("product")
        ...         .field("name", dtype="str")
        ...         .field("price")
        ...         .field("category", dtype="str",
        ...                choices=["electronics", "clothing", "food"])
        ... )

        >>> # Extract multiple addresses
        >>> schema = (extractor.create_schema()
        ...     .structure("address")
        ...         .field("street")
        ...         .field("city", dtype="str")
        ...         .field("country", dtype="str")
        ... )

        Notes
        -----
        - Any previously active structure is automatically finished
        - No need to explicitly call finish() - it's handled automatically
        - The extractor will find ALL instances of this structure in the text
        """
        # Auto-finish any active structure builder
        if self._active_structure_builder:
            self._active_structure_builder._auto_finish()

        self._active_structure_builder = StructureBuilder(self, name)
        return self._active_structure_builder

    def classification(
            self,
            task: str,
            labels: Union[List[str], Dict[str, str]],
            multi_label: bool = False,
            cls_threshold: float = 0.5,
            **kwargs
    ) -> 'Schema':
        """
        Add a text classification task.

        This method adds a classification task that assigns one or more labels
        to the entire input text (document-level classification).

        Parameters
        ----------
        task : str
            The name of the classification task (e.g., "sentiment", "category").
            This will be the key in the results dictionary.
        labels : List[str] or Dict[str, str]
            Either:
            - List[str]: Simple list of label names
            - Dict[str, str]: Mapping of label names to descriptions
              (descriptions help improve classification accuracy)
        multi_label : bool, default=False
            If True, multiple labels can be assigned to the text.
            If False, only the single best label is selected.
        cls_threshold : float, default=0.5
            Confidence threshold for label assignment (0-1).
            For multi_label, labels above this threshold are selected.
        **kwargs : dict
            Additional configuration options:
            - class_act : str, optional
                Activation function: "sigmoid", "softmax", or "auto"

        Returns
        -------
        Schema
            Returns self for method chaining.

        Examples
        --------
        >>> # Simple sentiment classification
        >>> schema = (extractor.create_schema()
        ...     .classification("sentiment", ["positive", "negative", "neutral"])
        ... )

        >>> # Multi-label classification with descriptions
        >>> schema = (extractor.create_schema()
        ...     .classification("topics",
        ...         {
        ...             "technology": "Related to computers, AI, or gadgets",
        ...             "business": "Related to companies, finance, or economy",
        ...             "health": "Related to medicine, wellness, or healthcare"
        ...         },
        ...         multi_label=True,
        ...         cls_threshold=0.3
        ...     )
        ... )

        >>> # High-precision classification
        >>> schema = (extractor.create_schema()
        ...     .classification("priority",
        ...         ["urgent", "high", "medium", "low"],
        ...         cls_threshold=0.8
        ...     )
        ... )

        Notes
        -----
        - For multi_label=False, returns (label, confidence) tuple
        - For multi_label=True, returns list of (label, confidence) tuples
        - Label descriptions significantly improve accuracy
        - Lower thresholds = more labels selected (for multi_label)
        """
        # Auto-finish any active structure builder
        if self._active_structure_builder:
            self._active_structure_builder._auto_finish()
            self._active_structure_builder = None

        # Parse labels
        if isinstance(labels, dict):
            label_names = list(labels.keys())
            label_descriptions = labels
        else:
            label_names = labels
            label_descriptions = None

        # Create classification config
        config = {
            "task": task,
            "labels": label_names,
            "multi_label": multi_label,
            "cls_threshold": cls_threshold,
            "true_label": ["N/A"],
            **kwargs
        }

        if label_descriptions:
            config["label_descriptions"] = label_descriptions

        self.schema["classifications"].append(config)
        return self

    def entities(
            self,
            entity_types: Union[str, List[str], Dict[str, Union[str, Dict]]],
            dtype: Literal["str", "list"] = "list",
            threshold: Optional[float] = None
    ) -> 'Schema':
        """
        Add entity extraction task for named entity recognition.

        This method configures extraction of specific entity types from the text,
        such as people, organizations, locations, or any custom entity types.

        Parameters
        ----------
        entity_types : str, List[str], or Dict[str, Union[str, Dict]]
            Entity types to extract. Can be:
            - str: Single entity type
            - List[str]: Multiple entity types
            - Dict[str, str]: Entity types with descriptions
            - Dict[str, Dict]: Entity types with full configuration
              (including dtype, threshold, description)
        dtype : {"str", "list"}, default="list"
            Default data type for entities:
            - "str": Extract only one entity per type (the best match)
            - "list": Extract all matching entities per type
        threshold : float, optional
            Default confidence threshold for entity extraction (0-1).
            Individual entities can override this.

        Returns
        -------
        Schema
            Returns self for method chaining.

        Examples
        --------
        >>> # Simple entity extraction
        >>> schema = extractor.create_schema().entities(["person", "location", "date"])

        >>> # Single entity per type
        >>> schema = extractor.create_schema().entities(
        ...     ["company", "ceo"],
        ...     dtype="str"
        ... )

        >>> # Entities with descriptions
        >>> schema = extractor.create_schema().entities({
        ...     "drug": "Pharmaceutical drug or medication names",
        ...     "disease": "Medical conditions or diseases",
        ...     "symptom": "Medical symptoms or side effects"
        ... })

        >>> # Advanced configuration per entity
        >>> schema = extractor.create_schema().entities({
        ...     "email": {
        ...         "description": "Email addresses",
        ...         "dtype": "list",
        ...         "threshold": 0.9
        ...     },
        ...     "phone": {
        ...         "description": "Phone numbers",
        ...         "dtype": "str",
        ...         "threshold": 0.8
        ...     }
        ... })

        Notes
        -----
        - Entities are extracted as exact text spans from the input
        - Multiple calls to entities() are cumulative
        - Entity descriptions improve extraction accuracy
        - Results are returned as {"entities": [{"type1": [...], "type2": [...]}]}
        """
        # Auto-finish any active structure builder
        if self._active_structure_builder:
            self._active_structure_builder._auto_finish()
            self._active_structure_builder = None

        entities = self._parse_entity_input(entity_types)

        for entity_name, config in entities.items():
            self.schema["entities"][entity_name] = ""

            # Only add to order if not already present
            if entity_name not in self._entity_order:
                self._entity_order.append(entity_name)

            # Get configuration
            entity_dtype = config.get("dtype", dtype)
            entity_threshold = config.get("threshold", threshold)
            description = config.get("description")

            # Store metadata
            self._store_entity_metadata(entity_name, entity_dtype, entity_threshold)

            # Store description
            if description:
                self.schema["entity_descriptions"][entity_name] = description

        return self

    def _parse_entity_input(self, entity_types) -> Dict[str, Dict]:
        """Parse different entity input formats."""
        if isinstance(entity_types, str):
            return {entity_types: {}}
        elif isinstance(entity_types, list):
            return {name: {} for name in entity_types}
        elif isinstance(entity_types, dict):
            result = {}
            for name, config in entity_types.items():
                if isinstance(config, str):
                    result[name] = {"description": config}
                elif isinstance(config, dict):
                    result[name] = config
                else:
                    result[name] = {}
            return result
        else:
            raise ValueError("Invalid entity_types format")

    def build(self) -> Dict[str, Any]:
        """
        Build the final schema dictionary.

        This method finalizes the schema construction and returns the internal
        schema representation. Any pending structures are automatically
        completed.

        Returns
        -------
        Dict[str, Any]
            The complete schema dictionary ready for extraction.

        Examples
        --------
        >>> # Explicit build
        >>> schema_builder = extractor.create_schema()
        >>> schema_builder.entities(["person", "location"])
        >>> schema_builder.classification("sentiment", ["positive", "negative"])
        >>> schema_dict = schema_builder.build()

        >>> # Implicit build (recommended)
        >>> # No need to call build() when using extract()
        >>> results = extractor.extract(
        ...     text,
        ...     schema_builder  # build() is called automatically
        ... )

        Notes
        -----
        - Automatically finishes any incomplete structures
        - Not necessary to call when using extract()
        - Can be used to inspect the schema structure
        - Safe to call multiple times
        """
        # Auto-finish any active structure builder
        if self._active_structure_builder:
            self._active_structure_builder._auto_finish()
            self._active_structure_builder = None

        return self.schema


class GLiNER2(Extractor):
    """
    Advanced information extraction model with intuitive schema-based API.

    GLiNER2 provides a clean, powerful interface for extracting structured
    information from text including entities, classifications, and complex
    nested data structures. It uses a schema-based approach that allows
    combining multiple extraction tasks together.

    Key Features
    ------------
    - **Entity Extraction**: Extract named entities like persons, locations, etc.
    - **Text Classification**: Single/multi-label document classification
    - **Structured Extraction**: Extract complex nested data structures
    - **Field-level Control**: Set custom thresholds and types per field
    - **Auto-completion**: No need to explicitly finish/build schemas
    - **Order Preservation**: Maintains field and entity ordering

    Quick Start
    -----------
    >>> from gliner2 import GLiNER2
    >>>
    >>> # Load pre-trained model
    >>> extractor = GLiNER2.from_pretrained("your-model")
    >>>
    >>> # Simple entity extraction
    >>> results = extractor.extract_entities(
    ...     "Apple Inc. announced new products in California.",
    ...     ["company", "product", "location"]
    ... )
    >>>
    >>> # Complex multi-task extraction
    >>> schema = (extractor.create_schema()
    ...     .entities(["person", "date"])
    ...     .classification("sentiment", ["positive", "negative"])
    ...     .structure("event")
    ...         .field("name", dtype="str")
    ...         .field("location")
    ...         .field("type", choices=["conference", "launch", "meeting"])
    ... )
    >>> results = extractor.extract(text, schema)

    Schema Building
    ---------------
    The schema provides a fluent interface for defining what to extract:

    1. **Entities**: Simple named entity recognition
       ```python
       schema.entities(["person", "organization", "location"])
       ```

    2. **Classification**: Document-level labels
       ```python
       schema.classification("category", ["tech", "finance", "health"])
       ```

    3. **Structures**: Complex field extraction
       ```python
       schema.structure("product")
              .field("name", dtype="str")
              .field("features", dtype="list")
              .field("category", choices=["electronics", "software"])
       ```

    Output Format
    -------------
    Results are organized by extraction type:
    ```python
    {
        "entities": {
            "person": ["John Doe", "Jane Smith"],
            "location": ["New York"]
        },
        "sentiment": "positive",
        "product": [
            {
                "name": "iPhone",
                "features": ["5G", "Camera"],
                "category": "electronics"
            }
        ]
    }
    ```

    Advanced Usage
    --------------
    - **Custom Thresholds**: `field("price", threshold=0.9)`
    - **Descriptions**: `entities({"drug": "Medication names"})`
    - **Raw Results**: `extract(text, schema, format_results=False)`
    - **Confidence Scores**: `include_confidence=True`

    See Also
    --------
    create_schema : Start building a new extraction schema
    extract : Main extraction method
    extract_entities : Quick entity extraction
    classify_text : Quick text classification
    extract_json : Quick structured extraction
    """

    def create_schema(self) -> Schema:
        """
        Create a new schema for defining extraction tasks.

        This is the starting point for building extraction schemas using the
        fluent API. The schema defines what information to extract from the text.

        Returns
        -------
        Schema
            A new schema instance for chaining extraction tasks.

        Examples
        --------
        >>> # Simple entity extraction
        >>> schema = extractor.create_schema().entities(["person", "location"])

        >>> # Complex multi-task extraction
        >>> schema = (extractor.create_schema()
        ...     .entities({
        ...         "person": "Names of people mentioned",
        ...         "organization": "Company or organization names"
        ...     })
        ...     .classification("sentiment", ["positive", "negative", "neutral"])
        ...     .structure("contact_info")
        ...         .field("email", dtype="str")
        ...         .field("phone", dtype="list")
        ...     .structure("product")
        ...         .field("name", dtype="str")
        ...         .field("price")
        ...         .field("category", dtype="str",
        ...                choices=["electronics", "clothing", "food"])
        ... )

        See Also
        --------
        Schema : The schema class with available methods
        extract : Method to run extraction with the schema
        """
        return Schema()

    @torch.no_grad()
    def extract(
            self,
            text: str,
            schema: Union[Schema, Dict[str, Any]],
            threshold: float = 0.5,
            format_results: bool = True,
            include_confidence: bool = False
    ) -> Dict[str, Any]:
        """
        Extract information from text using a schema.

        This is the main extraction method that processes text according to the
        defined schema and returns structured results.

        Parameters
        ----------
        text : str
            The input text to extract information from. Can be a sentence,
            paragraph, or full document. A period is automatically added if
            the text doesn't end with punctuation.
        schema : Schema or Dict[str, Any]
            Either:
            - A Schema instance (recommended)
            - A raw schema dictionary (for advanced use)
        threshold : float, default=0.5
            Minimum confidence score (0-1) for accepting extracted spans.
            Higher values = more precise but may miss some extractions.
            Lower values = more recall but may include false positives.
        format_results : bool, default=True
            If True, returns clean, formatted results.
            If False, returns raw results with full details.
        include_confidence : bool, default=False
            If True, includes confidence scores in formatted output.
            Only applies when format_results=True.

        Returns
        -------
        Dict[str, Any]
            Extraction results organized by task name:
            - Entity results: {"entities": [{"person": ["John"], "location": ["NYC"]}]}
            - Classification: {"sentiment": "positive"} or with confidence
            - Structures: {"product": [{"name": "iPhone", "price": "999"}]}

        Examples
        --------
        >>> # Basic extraction
        >>> schema = extractor.create_schema().entities(["person", "location"])
        >>> results = extractor.extract(
        ...     "John Smith visited New York yesterday.",
        ...     schema
        ... )
        >>> # {'entities': {'person': ['John Smith'], 'location': ['New York']}}

        >>> # With confidence scores
        >>> results = extractor.extract(
        ...     text, schema,
        ...     include_confidence=True
        ... )
        >>> # {'sentiment': {'label': 'positive', 'confidence': 0.95}}

        >>> # High precision mode
        >>> results = extractor.extract(
        ...     text, schema,
        ...     threshold=0.8  # Only very confident extractions
        ... )

        >>> # Raw results for debugging
        >>> results = extractor.extract(
        ...     text, schema,
        ...     format_results=False  # Get all internal details
        ... )

        Notes
        -----
        - Schema is automatically built if not already done
        - Empty results are returned as empty lists/dicts, not None
        - Overlapping spans are resolved using greedy selection
        - Classification thresholds can be set per-task in the schema

        Raises
        ------
        ValueError
            If the schema is invalid or empty
        """
        # Clean up text
        if not text.endswith(('.', '!', '?')):
            text += "."

        # Handle StructureBuilder case (when only structure was used)
        if hasattr(schema, 'schema') and hasattr(schema, '_auto_finish'):
            # This is a StructureBuilder - get the parent Schema
            schema._auto_finish()  # Finish the structure
            schema = schema.schema

        # Extract schema information - auto-build if Schema
        if isinstance(schema, Schema):
            schema_dict = schema.build()  # This will auto-finish any pending structures
            field_metadata = schema._field_metadata
            entity_metadata = schema._entity_metadata
            field_orders = schema._field_orders
            entity_order = schema._entity_order
        elif isinstance(schema, dict):
            schema_dict = schema
            field_metadata = {}
            entity_metadata = {}
            field_orders = {}
            entity_order = []
        else:
            raise ValueError(
                "Invalid schema type. Expected Schema or dict, "
                f"got {type(schema).__name__}. "
                "Did you forget to call create_schema() first?"
            )

        # Create record and extract
        record = {"text": text, "schema": schema_dict}
        raw_results = self._perform_extraction(
            record, threshold, field_metadata, entity_metadata, field_orders, entity_order
        )

        # Format results if requested
        if format_results:
            return self.format_results(raw_results, include_confidence)
        else:
            return raw_results

    def _perform_extraction(
            self,
            record: Dict[str, Any],
            default_threshold: float,
            field_metadata: Dict[str, Dict],
            entity_metadata: Dict[str, Dict],
            field_orders: Dict[str, List[str]],
            entity_order: List[str]
    ) -> Dict[str, Any]:
        """Core extraction pipeline."""
        # Setup model
        self.eval()
        self.processor.change_mode(is_training=False)

        # Prepare schema - record["schema"] is always a dict here
        self._prepare_schema(record["schema"])

        # Build classification field mapping (without modifying schema)
        classification_fields = self._build_classification_map(record["schema"])

        # Process through model pipeline
        outputs = self.processor.process_record(self.encoder, record)
        span_info = self.compute_span_rep(outputs["token_embeddings"])

        # Extract results
        results = {}
        for i, schema_tokens in enumerate(outputs["schema_tokens_list"]):
            if len(schema_tokens) < 4:
                continue

            schema_name = self._get_schema_name(schema_tokens)
            task_type = outputs["task_types"][i]

            if task_type == "classifications":
                self._extract_classification(
                    results, schema_name, record["schema"],
                    outputs["embs_per_schema"][i], schema_tokens
                )
            else:
                self._extract_spans(
                    results, schema_name, i, outputs, span_info, record,
                    default_threshold, field_metadata, entity_metadata,
                    field_orders, entity_order, classification_fields
                )

        return results

    def _prepare_schema(self, schema: Dict[str, Any]):
        """
        Prepare schema for processing.

        Parameters
        ----------
        schema : Dict[str, Any]
            The schema dictionary (not a Schema instance)
        """
        # Ensure classifications have true_label
        for cls_config in schema.get("classifications", []):
            cls_config.setdefault("true_label", ["N/A"])

    def _build_classification_map(self, schema: Dict[str, Any]) -> Dict[str, List[str]]:
        """Build mapping of classification fields to their choices without modifying schema."""
        mapping = {}
        for struct in schema.get("json_structures", []):
            for parent, fields in struct.items():
                for fname, fval in fields.items():
                    if isinstance(fval, dict) and "choices" in fval:
                        mapping[f"{parent}.{fname}"] = fval["choices"]
        return mapping

    def _get_schema_name(self, schema_tokens: List[str]) -> str:
        """Extract schema name from tokens."""
        return schema_tokens[2].split(" [DESCRIPTION] ")[0]

    def _extract_classification(
            self,
            results: Dict,
            schema_name: str,
            schema: Dict,
            embeddings: List,
            schema_tokens: List[str]
    ):
        """Extract classification results."""
        # Find classification config
        cls_config = next(
            c for c in schema["classifications"]
            if schema_tokens[2].startswith(c["task"])
        )

        # Get model predictions
        schema_emb = torch.stack(embeddings)
        cls_embeds = schema_emb[1:]  # Skip [P] token
        logits = self.classifier(cls_embeds).squeeze(-1)

        # Apply activation function
        activation = cls_config.get("class_act", "auto")
        if activation == "sigmoid":
            probs = torch.sigmoid(logits)
        elif activation == "softmax":
            probs = torch.softmax(logits, dim=-1)
        else:
            # Auto-select based on multi_label
            is_multi = cls_config.get("multi_label", False)
            probs = torch.sigmoid(logits) if is_multi else torch.softmax(logits, dim=-1)

        # Format results
        labels = cls_config["labels"]
        threshold = cls_config.get("cls_threshold", 0.5)

        if cls_config.get("multi_label", False):
            # Multi-label classification
            chosen = [
                (labels[j], probs[j].item())
                for j in range(len(labels))
                if probs[j].item() >= threshold
            ]
            # Fallback to best prediction if none above threshold
            if not chosen:
                best_idx = int(torch.argmax(probs).item())
                chosen = [(labels[best_idx], probs[best_idx].item())]
            results[schema_name] = chosen
        else:
            # Single-label classification
            best_idx = int(torch.argmax(probs).item())
            results[schema_name] = (labels[best_idx], probs[best_idx].item())

    def _extract_spans(
            self,
            results: Dict,
            schema_name: str,
            schema_idx: int,
            outputs: Dict,
            span_info: Dict,
            record: Dict,
            default_threshold: float,
            field_metadata: Dict,
            entity_metadata: Dict,
            field_orders: Dict[str, List[str]],
            entity_order: List[str],
            classification_fields: Dict[str, List[str]]
    ):
        """Extract span-based results (entities, structures)."""
        # Get basic information
        schema_tokens = outputs["schema_tokens_list"][schema_idx]
        field_names = self._get_field_names(schema_tokens)
        embeddings = outputs["embs_per_schema"][schema_idx]

        if not field_names:
            results[schema_name] = [] if schema_name == "entities" else {}
            return

        # Get span predictions
        count, span_scores = self._predict_spans(embeddings, field_names, span_info)

        if count <= 0:
            results[schema_name] = [] if schema_name == "entities" else {}
            return

        # Extract based on schema type
        if schema_name == "entities":
            results[schema_name] = self._extract_entity_results(
                field_names, span_scores, record, outputs,
                default_threshold, entity_metadata, entity_order
            )
        else:
            results[schema_name] = self._extract_structure_results(
                schema_name, field_names, span_scores, count, record, outputs,
                default_threshold, field_metadata, field_orders, classification_fields
            )

    def _get_field_names(self, schema_tokens: List[str]) -> List[str]:
        """Extract field names from schema tokens."""
        field_names = []
        for i in range(len(schema_tokens) - 1):
            if schema_tokens[i] in ("[E]", "[C]", "[R]"):
                field_names.append(schema_tokens[i + 1])
        return field_names

    def _predict_spans(self, embeddings: List, field_names: List[str], span_info: Dict) -> Tuple[
        int, Optional[torch.Tensor]]:
        """Predict count and span scores."""
        schema_emb = torch.stack(embeddings)

        # Predict how many instances to extract
        count_logits = self.count_pred(schema_emb[0].unsqueeze(0))
        pred_count = int(count_logits.argmax(dim=1).item())

        if pred_count <= 0:
            return 0, None

        # Get span representations
        struct_proj = self.count_embed(schema_emb[1:], pred_count)
        span_scores = torch.sigmoid(
            torch.einsum("lkd,bpd->bplk", span_info["span_rep"], struct_proj)
        )

        return pred_count, span_scores

    def _extract_entity_results(
            self,
            entity_names: List[str],
            span_scores: torch.Tensor,
            record: Dict,
            outputs: Dict,
            default_threshold: float,
            entity_metadata: Dict,
            entity_order: List[str]
    ) -> List[Dict[str, Any]]:
        """Extract entity results with per-entity thresholds and preserved order."""
        if span_scores is None:
            return []

        text_len = len(self.processor.tokenize_text(record["text"]))
        # Use first instance for entities
        scores = span_scores[0, :, -text_len:]

        # Use OrderedDict to preserve entity order
        entity_results = OrderedDict()

        # Process entities in the order they were defined
        for entity_name in entity_order if entity_order else entity_names:
            if entity_name not in entity_names:
                continue

            entity_idx = entity_names.index(entity_name)

            # Get entity configuration
            metadata = entity_metadata.get(entity_name, {})
            threshold = metadata.get("threshold")
            if threshold is None:
                threshold = default_threshold
            dtype = metadata.get("dtype", "list")

            # Find spans above threshold
            spans = self._find_valid_spans(
                scores[entity_idx], threshold, record, outputs, text_len
            )

            # Format results
            if dtype == "list":
                entity_results[entity_name] = self._format_span_list(spans)
            else:  # "str"
                entity_results[entity_name] = spans[0][0] if spans else ""

        return [entity_results] if entity_results else []

    def _extract_structure_results(
            self,
            schema_name: str,
            field_names: List[str],
            span_scores: torch.Tensor,
            count: int,
            record: Dict,
            outputs: Dict,
            default_threshold: float,
            field_metadata: Dict,
            field_orders: Dict[str, List[str]],
            classification_fields: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Extract structured data results with per-field thresholds and preserved order."""
        if span_scores is None:
            return []

        text_len = len(self.processor.tokenize_text(record["text"]))
        tokens = outputs["text_tokens"]
        instances = []

        # Get the field order for this schema
        ordered_fields = field_orders.get(schema_name, field_names)

        for instance_idx in range(count):
            scores = span_scores[instance_idx, :, -text_len:]

            # Use OrderedDict to preserve field order
            instance_data = OrderedDict()

            # Process fields in the order they were defined
            for field_name in ordered_fields:
                if field_name not in field_names:
                    continue

                field_idx = field_names.index(field_name)

                # Get field configuration
                field_key = f"{schema_name}.{field_name}"
                metadata = field_metadata.get(field_key, {})
                threshold = metadata.get("threshold")
                if threshold is None:
                    threshold = default_threshold
                dtype = metadata.get("dtype", "list")

                # Check if this is a classification field
                if field_key in classification_fields:
                    # Handle classification field
                    choices = classification_fields[field_key]
                    field_scores = span_scores[instance_idx, field_idx, :-text_len]

                    # Debug: Check if we have any scores at all
                    if field_scores.numel() == 0:
                        continue

                    if dtype == "list":
                        # Multi-choice selection with duplicate prevention
                        selected = []
                        selected_set = set()
                        for choice in choices:
                            if choice in selected_set:
                                continue
                            choice_indices = self._find_choice_indices(choice, tokens[:-text_len])
                            if not choice_indices:
                                # Try with [selection] prefix
                                choice_indices = self._find_choice_indices(f"[selection]{choice}", tokens[:-text_len])
                            for start_idx in choice_indices:
                                if start_idx >= 0 and start_idx < field_scores.shape[0] and field_scores[
                                    start_idx, 0].item() >= threshold:
                                    selected.append(choice)
                                    selected_set.add(choice)
                                    break
                        instance_data[field_name] = selected
                    else:  # str
                        # Single choice selection
                        best_choice = None
                        best_score = -1.0

                        # Try each choice
                        for choice in choices:
                            choice_indices = self._find_choice_indices(choice, tokens[:-text_len])
                            if not choice_indices:
                                # Try with [selection] prefix
                                choice_indices = self._find_choice_indices(f"[selection]{choice}", tokens[:-text_len])

                            for start_idx in choice_indices:
                                if start_idx >= 0 and start_idx < field_scores.shape[0]:
                                    score = field_scores[start_idx, 0].item()
                                    if score > best_score:
                                        best_score = score
                                        best_choice = choice

                        # Apply threshold check
                        if best_choice and best_score >= threshold:
                            instance_data[field_name] = best_choice
                        elif threshold == 0.0 and best_choice:
                            # Special case: threshold is 0, so include best match regardless
                            instance_data[field_name] = best_choice
                        else:
                            # Set None for str fields with no valid choice
                            instance_data[field_name] = None
                else:
                    # Regular span extraction
                    spans = self._find_valid_spans(
                        scores[field_idx], threshold, record, outputs, text_len
                    )

                    # Format and store results
                    if spans:
                        if dtype == "list":
                            instance_data[field_name] = self._format_span_list(spans)
                        else:  # "str"
                            instance_data[field_name] = spans[0][0]
                    else:
                        # Set None for str fields, empty list for list fields
                        if dtype == "list":
                            instance_data[field_name] = []
                        else:  # "str"
                            instance_data[field_name] = None

            # Only add instance if it has at least one non-empty field
            has_content = False
            for value in instance_data.values():
                if value is not None and value != []:
                    has_content = True
                    break

            if has_content:
                instances.append(instance_data)

        return instances

    def _find_choice_indices(self, choice: str, tokens: List[str]) -> List[int]:
        """Find all starting indices where a choice appears in tokens."""
        indices = []

        # For classification choices, they often appear as single tokens in the prefix
        # First check for exact match
        choice_lower = choice.lower()
        for i, token in enumerate(tokens):
            if token.lower() == choice_lower:
                indices.append(i)

        # If no exact match found, try substring matching for the prefix area
        # This helps when choices are part of constructed tokens like "[selection]Italian"
        if not indices:
            for i, token in enumerate(tokens):
                if choice_lower in token.lower():
                    indices.append(i)

        return indices

    def _find_valid_spans(
            self,
            field_scores: torch.Tensor,
            threshold: float,
            record: Dict,
            outputs: Dict,
            text_len: int
    ) -> List[Tuple[str, float, int, int]]:
        """Find all valid spans above threshold with position information."""
        # Ensure threshold has a value
        if threshold is None:
            threshold = 0.5

        valid_positions = torch.where(field_scores >= threshold)
        starts, widths = valid_positions

        spans = []
        # Check if position mappings exist
        has_char_mapping = (
                "start_token_idx_to_text_idx" in outputs and
                "end_token_idx_to_text_idx" in outputs
        )

        for start, width in zip(starts.tolist(), widths.tolist()):
            end = start + width + 1

            # Check bounds
            if 0 <= start < text_len and end <= text_len:
                if has_char_mapping:
                    try:
                        char_start = outputs["start_token_idx_to_text_idx"][start]
                        char_end = outputs["end_token_idx_to_text_idx"][end - 1]
                        text_span = record["text"][char_start:char_end].strip()
                    except (KeyError, IndexError):
                        # Fallback to token-based
                        text_tokens = outputs["text_tokens"][-text_len:]
                        span_tokens = text_tokens[start:end]
                        text_span = " ".join(span_tokens).strip()
                else:
                    # Use token-based extraction
                    text_tokens = outputs["text_tokens"][-text_len:]
                    span_tokens = text_tokens[start:end]
                    text_span = " ".join(span_tokens).strip()

                confidence = field_scores[start, width].item()

                if text_span:  # Only add non-empty spans
                    spans.append((text_span, confidence, start, end))

        return spans

    def _format_span_list(self, spans: List[Tuple[str, float, int, int]]) -> List[str]:
        """Format spans into a clean list with proper overlap detection and greedy selection."""
        if not spans:
            return []

        # Apply greedy selection for non-overlapping spans
        # Sort by confidence descending
        sorted_spans = sorted(spans, key=lambda x: x[1], reverse=True)

        selected = []

        for text, confidence, start, end in sorted_spans:
            # Check for overlap with already selected spans
            overlap = False
            for sel_text, sel_conf, sel_start, sel_end in selected:
                # Check position-based overlap
                if not (end <= sel_start or start >= sel_end):
                    overlap = True
                    break

            if not overlap:
                selected.append((text, confidence, start, end))

        # Return only the text, maintaining confidence order
        return [text for text, _, _, _ in selected]

    def format_results(self, results: Dict[str, Any], include_confidence: bool = False) -> Dict[str, Any]:
        """
        Format raw extraction results into clean, user-friendly output.

        This method processes raw extraction results to:
        - Remove duplicates and empty values
        - Simplify confidence score presentation
        - Ensure consistent structure
        - Preserve field ordering

        Parameters
        ----------
        results : Dict[str, Any]
            Raw extraction results from extract or similar.
        include_confidence : bool, default=False
            If True, includes confidence scores in the output.
            If False, returns only the extracted values.

        Returns
        -------
        Dict[str, Any]
            Formatted results with clean structure.

        Examples
        --------
        >>> # Format without confidence
        >>> raw_results = extractor.extract(text, schema, format_results=False)
        >>> clean = extractor.format_results(raw_results)
        >>> # {'entities': {'person': ['John Doe'], 'location': ['New York']}}

        >>> # Format with confidence
        >>> clean = extractor.format_results(raw_results, include_confidence=True)
        >>> # {'sentiment': {'label': 'positive', 'confidence': 0.95}}

        Notes
        -----
        - Removes duplicate values (case-insensitive)
        - Filters out empty strings and None values
        - Maintains original field order when possible
        - Single-value lists are kept as lists (not unwrapped)
        """
        formatted = {}

        for key, value in results.items():
            if isinstance(value, list) and len(value) > 0:
                # Handle entity results (list of dicts)
                if isinstance(value[0], dict):
                    if key == "entities":
                        # Format entities specially
                        formatted[key] = self._format_entities(value[0], include_confidence)
                    else:
                        # Structures - format each instance
                        formatted[key] = [
                            self._format_structure_instance(instance, include_confidence)
                            for instance in value
                        ]
                elif isinstance(value[0], tuple):
                    # Multi-label classification results
                    if include_confidence:
                        formatted[key] = [{"label": label, "confidence": conf} for label, conf in value]
                    else:
                        formatted[key] = [label for label, _ in value]
                else:
                    # Simple list results
                    formatted[key] = value
            elif isinstance(value, tuple):
                # Single-label classification result
                label, conf = value
                if include_confidence:
                    formatted[key] = {"label": label, "confidence": conf}
                else:
                    formatted[key] = label
            elif isinstance(value, dict):
                # Single structure instance
                formatted[key] = self._format_structure_instance(value, include_confidence)
            else:
                # Direct value
                formatted[key] = value

        return formatted

    def _format_entities(self, entities: Dict[str, Any], include_confidence: bool) -> Dict[str, Any]:
        """Format entity extraction results."""
        formatted = {}
        for entity_type, spans in entities.items():
            if isinstance(spans, list):
                # Remove empty strings and duplicates while preserving order
                unique_spans = []
                seen = set()
                for span in spans:
                    if span and span.lower() not in seen:
                        seen.add(span.lower())
                        unique_spans.append(span)
                formatted[entity_type] = unique_spans
            else:
                # Single span (str type)
                formatted[entity_type] = spans if spans else None
        return formatted

    def _format_structure_instance(self, instance: Dict[str, Any], include_confidence: bool) -> Dict[str, Any]:
        """Format a single structure instance."""
        formatted = {}
        for field, value in instance.items():
            if isinstance(value, list):
                # Remove empty strings and duplicates
                unique_values = []
                seen = set()
                for v in value:
                    if v and v.lower() not in seen:
                        seen.add(v.lower())
                        unique_values.append(v)
                formatted[field] = unique_values
            elif value:  # Non-empty string
                formatted[field] = value
            else:
                formatted[field] = None
        return formatted

    def pretty_print_results(self, results: Dict[str, Any], include_confidence: bool = False) -> str:
        """
        Convert extraction results to a nicely formatted JSON string.

        This method formats results as indented JSON for easy reading and debugging.
        Useful for displaying results in logs, console output, or documentation.

        Parameters
        ----------
        results : Dict[str, Any]
            Extraction results (raw or already formatted).
        include_confidence : bool, default=False
            Whether to include confidence scores in the output.

        Returns
        -------
        str
            Pretty-printed JSON string with 2-space indentation.

        Examples
        --------
        >>> results = extractor.extract_entities(
        ...     "John works at OpenAI in San Francisco.",
        ...     ["person", "company", "location"]
        ... )
        >>> print(extractor.pretty_print_results(results))
        {
          "entities": {
            "person": [
              "John"
            ],
            "company": [
              "OpenAI"
            ],
            "location": [
              "San Francisco"
            ]
          }
        }

        >>> # With confidence scores
        >>> print(extractor.pretty_print_results(results, include_confidence=True))
        {
          "sentiment": {
            "label": "positive",
            "confidence": 0.92
          }
        }

        Notes
        -----
        - Uses 2-space indentation for readability
        - Handles Unicode characters properly (ensure_ascii=False)
        - Automatically formats results if not already formatted
        """
        import json
        formatted = self.format_results(results, include_confidence)
        return json.dumps(formatted, indent=2, ensure_ascii=False)

    # Convenience methods for common use cases
    def extract_entities(
            self,
            text: str,
            entity_types: Union[List[str], Dict[str, Union[str, Dict]]],
            threshold: float = 0.5,
            format_results: bool = True,
            include_confidence: bool = False
    ) -> Dict[str, Any]:
        """
        Quick entity extraction without explicit schema building.

        This is a convenience method for simple entity extraction tasks.
        Internally creates a schema with only entity extraction.

        Parameters
        ----------
        text : str
            The input text to extract entities from.
        entity_types : List[str] or Dict
            Entity types to extract (see entities for format details).
        threshold : float, default=0.5
            Minimum confidence threshold for entity extraction.
        format_results : bool, default=True
            Whether to format the results nicely.
        include_confidence : bool, default=False
            Whether to include confidence scores.

        Returns
        -------
        Dict[str, Any]
            Dictionary with "entities" key containing extracted entities.

        Examples
        --------
        >>> # Simple entity extraction
        >>> results = extractor.extract_entities(
        ...     "Apple Inc. CEO Tim Cook announced new products.",
        ...     ["company", "person", "product"]
        ... )
        >>> # {'entities': {'company': ['Apple Inc.'], 'person': ['Tim Cook']}}

        >>> # With descriptions for better accuracy
        >>> results = extractor.extract_entities(
        ...     text,
        ...     {
        ...         "medication": "Names of drugs or medications",
        ...         "dosage": "Dosage amounts like '50mg' or '2 tablets'"
        ...     }
        ... )

        See Also
        --------
        create_schema : For more complex extraction tasks
        entities : For detailed entity configuration
        """
        schema = self.create_schema().entities(entity_types)
        return self.extract(text, schema, threshold, format_results, include_confidence)

    def classify_text(
            self,
            text: str,
            tasks: Dict[str, Union[List[str], Dict[str, Any]]],
            threshold: float = 0.5,
            format_results: bool = True,
            include_confidence: bool = False
    ) -> Dict[str, Any]:
        """
        Quick text classification without explicit schema building.

        This is a convenience method for classification tasks. Supports both
        single-label and multi-label classification with optional configurations.

        Parameters
        ----------
        text : str
            The text to classify.
        tasks : Dict[str, Union[List[str], Dict[str, Any]]]
            Classification tasks where keys are task names and values are either:
            - List[str]: Simple list of labels
            - Dict with "labels" key and optional config (multi_label, cls_threshold)
        threshold : float, default=0.5
            Confidence threshold (mainly used for other extraction types).
        format_results : bool, default=True
            Whether to format the results nicely.
        include_confidence : bool, default=False
            Whether to include confidence scores.

        Returns
        -------
        Dict[str, Any]
            Classification results keyed by task name.

        Examples
        --------
        >>> # Simple classification
        >>> results = extractor.classify_text(
        ...     "This product is amazing! Best purchase ever.",
        ...     {"sentiment": ["positive", "negative", "neutral"]}
        ... )
        >>> # {'sentiment': 'positive'}

        >>> # Multi-label classification
        >>> results = extractor.classify_text(
        ...     "The new smartphone has great camera but poor battery life.",
        ...     {
        ...         "aspects": {
        ...             "labels": ["camera", "battery", "screen", "performance"],
        ...             "multi_label": True,
        ...             "cls_threshold": 0.5
        ...         }
        ...     }
        ... )
        >>> # {'aspects': ['camera', 'battery']}

        >>> # With confidence scores
        >>> results = extractor.classify_text(
        ...     text,
        ...     {"category": ["tech", "sports", "politics"]},
        ...     include_confidence=True
        ... )
        >>> # {'category': {'label': 'tech', 'confidence': 0.92}}

        See Also
        --------
        classification : For more detailed classification configuration
        create_schema : For combining with other extraction tasks
        """
        schema = self.create_schema()

        for task_name, task_config in tasks.items():
            if isinstance(task_config, (list, dict)) and "labels" not in task_config:
                # Simple format: labels only
                schema.classification(task_name, task_config)
            elif isinstance(task_config, dict) and "labels" in task_config:
                # Full config format
                labels = task_config.pop("labels")
                schema.classification(task_name, labels, **task_config)
            else:
                raise ValueError(f"Invalid task config for {task_name}")

        return self.extract(text, schema, threshold, format_results, include_confidence)

    def extract_json(
            self,
            text: str,
            structures: Dict[str, List[str]],
            threshold: float = 0.5,
            format_results: bool = True,
            include_confidence: bool = False
    ) -> Dict[str, Any]:
        """
        Quick structured data extraction without explicit schema building.

        This is a convenience method for extracting structured data that follows
        a pattern with multiple fields. Extracts all instances found.

        Parameters
        ----------
        text : str
            The text to extract structured data from.
        structures : Dict[str, List[str]]
            Dictionary where keys are structure names and values are lists of
            field specifications. Field specs support flexible formats:
            - Simple: "field_name" (extracts as list)
            - With description: "field_name::description text here"
            - Typed: "field_name::str" or "field_name::list"
            - Choices: "field_name::[option1|option2|option3]" (defaults to str)
            - Choices with type: "field_name::[opt1|opt2]::list"
            - Full spec: "field_name::[opt1|opt2]::str::description here"
        threshold : float, default=0.5
            Minimum confidence threshold for extraction.
        format_results : bool, default=True
            Whether to format the results nicely.
        include_confidence : bool, default=False
            Whether to include confidence scores.

        Returns
        -------
        Dict[str, List[Dict]]
            Extracted structures keyed by structure name. Each structure
            contains a list of instances found.

        Examples
        --------
        >>> # Basic extraction
        >>> results = extractor.extract_json(
        ...     "iPhone 15 costs $999. Galaxy S24 is priced at $899.",
        ...     {
        ...         "product": [
        ...             "name::str",
        ...             "price::Product price"
        ...         ]
        ...     }
        ... )

        >>> # With choices and descriptions
        >>> results = extractor.extract_json(
        ...     text,
        ...     {
        ...         "reservation": [
        ...             "guest_name::str::Full name of the guest",
        ...             "room_type::[single|double|suite]::str::Type of room",
        ...             "amenities::[wifi|parking|pool|gym]::list::Selected amenities"
        ...         ]
        ...     }
        ... )

        >>> # Mixed specifications
        >>> results = extractor.extract_json(
        ...     text,
        ...     {
        ...         "task": [
        ...             "title::str",
        ...             "description::Detailed task description",
        ...             "priority::[low|medium|high|urgent]",
        ...             "tags::[bug|feature|docs|test]::list::Task labels",
        ...             "assignees::list::People assigned to this task"
        ...         ]
        ...     }
        ... )

        Notes
        -----
        - Default type is "list" for regular fields, "str" for choice fields
        - Choices with ":list" allow multiple selections
        - Descriptions improve extraction accuracy
        - Order of specification parts is flexible

        See Also
        --------
        structure : For more complex structure definitions
        create_schema : For combining with other extraction tasks
        """
        schema = self.create_schema()

        for parent, fields in structures.items():
            builder = schema.structure(parent)

            for field_spec in fields:
                name, dtype, choices, description = self._parse_field_spec(field_spec)
                builder.field(name, dtype=dtype, choices=choices, description=description)

        return self.extract(text, schema, threshold, format_results, include_confidence)

    def _parse_field_spec(self, field_spec: str) -> Tuple[str, str, Optional[List[str]], Optional[str]]:
        """
        Parse field specification string into components.

        This internal method parses the field specification format used in
        the extract_json convenience method. It supports flexible ordering and
        all combinations of type, choices, and descriptions.

        Parameters
        ----------
        field_spec : str
            Field specification in various formats:
            - "field_name" -> (field_name, "list", None, None)
            - "field_name::description here" -> (field_name, "list", None, "description here")
            - "field_name::str" -> (field_name, "str", None, None)
            - "field_name::list" -> (field_name, "list", None, None)
            - "field_name::[opt1|opt2|opt3]" -> (field_name, "str", [opt1, opt2, opt3], None)
            - "field_name::[opt1|opt2|opt3]::list" -> (field_name, "list", [opt1, opt2, opt3], None)
            - "field_name::str::Description text" -> (field_name, "str", None, "Description text")
            - "field_name::[opt1|opt2]::str::Description" -> (field_name, "str", [opt1, opt2], "Description")
            - "field_name::[opt1|opt2]::list::Description" -> (field_name, "list", [opt1, opt2], "Description")

        Returns
        -------
        Tuple[str, str, Optional[List[str]], Optional[str]]
            A tuple of (field_name, dtype, choices, description):
            - field_name: The name of the field
            - dtype: "str" or "list" (defaults to "list" unless choices without type)
            - choices: List of valid options, or None
            - description: Field description, or None

        Examples
        --------
        >>> # Simple field
        >>> _parse_field_spec("address")
        ('address', 'list', None, None)

        >>> # Field with description only
        >>> _parse_field_spec("address::Street address: including city and zip")
        ('address', 'list', None, 'Street address: including city and zip')

        >>> # Typed field
        >>> _parse_field_spec("email::str")
        ('email', 'str', None, None)

        >>> # Choice field (defaults to str)
        >>> _parse_field_spec("status::[active|pending|closed]")
        ('status', 'str', ['active', 'pending', 'closed'], None)

        >>> # Choice field with explicit list type
        >>> _parse_field_spec("tags::[python|javascript|java]::list")
        ('tags', 'list', ['python', 'javascript', 'java'], None)

        >>> # Field with type and description
        >>> _parse_field_spec("email::str::Contact email: user@example.com")
        ('email', 'str', None, 'Contact email: user@example.com')

        >>> # Choice field with type and description
        >>> _parse_field_spec("priority::[low|medium|high]::str::Task priority: importance level")
        ('priority', 'str', ['low', 'medium', 'high'], 'Task priority: importance level')

        >>> # Multi-select choices with description
        >>> _parse_field_spec("features::[wifi|parking|pool|gym]::list::Available amenities: select all that apply")
        ('features', 'list', ['wifi', 'parking', 'pool', 'gym'], 'Available amenities: select all that apply')

        Notes
        -----
        - Uses :: as separator to allow descriptions with colons
        - Default type is "list" for regular fields
        - Default type is "str" for choice fields (unless explicitly set)
        - Choices are trimmed of whitespace
        - Everything after type (or choices if no type) is treated as description
        """
        # Split by :: but keep at most 3 parts (name, middle, description)
        parts = field_spec.split('::', 2)

        # Field name is always first
        field_name = parts[0]

        # Defaults
        dtype = "list"
        choices = None
        description = None

        # No additional parts - just field name
        if len(parts) == 1:
            return field_name, dtype, choices, description

        # Process remaining parts
        remaining_parts = parts[1:]

        # Helper to check if a part is a type
        is_type = lambda s: s in ['str', 'list']

        # Helper to extract choices
        def parse_choices(s):
            if s.startswith('[') and s.endswith(']'):
                return [c.strip() for c in s[1:-1].split('|')]
            return None

        # Process based on number of remaining parts
        if len(remaining_parts) == 1:
            # One part after name: type, choices, or description
            part = remaining_parts[0]

            if is_type(part):
                dtype = part
            elif choices_parsed := parse_choices(part):
                choices = choices_parsed
                dtype = "str"  # Default for choices
            else:
                description = part

        elif len(remaining_parts) == 2:
            # Two parts after name
            first, second = remaining_parts

            # Check all combinations
            if choices_parsed := parse_choices(first):
                # First is choices
                choices = choices_parsed
                dtype = "str"  # Default for choices

                if is_type(second):
                    dtype = second
                else:
                    description = second

            elif is_type(first):
                # First is type, second is description
                dtype = first
                description = second

            else:
                # First part is neither choices nor type, treat as description
                # Join both parts back as description
                description = '::'.join(remaining_parts)

        return field_name, dtype, choices, description


# Legacy aliases for backwards compatibility
BuilderExtractor = GLiNER2
SchemaBuilder = Schema
JsonStructBuilder = StructureBuilder