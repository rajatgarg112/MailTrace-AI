# MailTrace AI — AI/ML/NLP Module (Phase 1 Foundation)

## 1. Purpose of the Module

The `ml` package provides the machine learning and natural language processing (NLP) foundation for **MailTrace AI**, a pre-delivery email security gateway.

The primary responsibilities of this module are:
- Cleaning and tokenizing raw email content (headers, subject line, body text, HTML markup, embedded URLs/emails).
- Extracting statistical text metrics, domain-specific security keyword indicators, and structural features across 6 categories.
- Running multi-signal ML detection across key threat categories:
  1. **Phishing Classification**: Credential harvesting and spoofed login links.
  2. **Suspicious-Language Detection**: High urgency, pressure tactics, and unusual tone/capitalization.
  3. **Social-Engineering Detection**: Wire transfer requests, payroll fraud, secrecy demands, and authority pressure.
  4. **Malicious-Content Classification**: Malicious download cues, suspicious attachment references, and executable payload indicators.
  5. **Impersonation Signals**: Executive (CEO/CFO), IT helpdesk, and brand/admin role spoofing cues.
- Providing a thread-safe, fail-safe **Inference Service** (`MLInferenceService`) interface for backend orchestrators during pre-delivery email inspection.
- Establishing modular interfaces for offline model training, dataset ingestion, and metrics evaluation.

> [!NOTE]
> For complete technical integration contracts, see [INTEGRATION_CONTRACT.md](file:///c:/Users/rajat/OneDrive/Documents/MailTrace-AI/ml/INTEGRATION_CONTRACT.md) and offline training instructions in [training/README.md](file:///c:/Users/rajat/OneDrive/Documents/MailTrace-AI/ml/training/README.md).

---

## 2. Folder Structure

```text
ml/
├── README.md                   # Module architecture documentation
├── INTEGRATION_CONTRACT.md     # Full integration contract for Member 6 & risk engine
├── __init__.py                 # Root package initialization
├── config/                     # Configuration management
│   ├── __init__.py
│   ├── ml_config.py            # Dataclasses for model, feature, and runtime settings
│   └── training_config.py      # Dataclasses for offline model training
├── preprocessing/              # Email text normalization & indicator extraction
│   ├── __init__.py
│   ├── base.py                 # BasePreprocessor interface & ProcessedEmail schema
│   ├── normalizer.py           # HTML cleaner, entity decoder, whitespace normalizer
│   ├── indicator_extractor.py  # Missing field flags & text metrics calculator
│   └── email_preprocessor.py   # Concrete EmailPreprocessor orchestrator
├── features/                   # NLP & statistical feature extractors
│   ├── __init__.py
│   ├── base.py                 # BaseFeatureExtractor & FeatureVector schema
│   ├── subject_features.py     # Subject text characteristics
│   ├── body_features.py        # Body text characteristics
│   ├── url_features.py         # URL security indicators & IP-host counts
│   ├── sender_features.py      # Sender domain length & freemail provider flags
│   ├── keyword_features.py     # Threat signal keyword scanner across 5 categories
│   ├── structure_features.py   # Recipient counts & HTML formatting indicators
│   └── composite_extractor.py  # Master EmailFeatureExtractor uniting all extractors
├── models/                     # Model interface & implementations
│   ├── __init__.py
│   ├── base.py                 # BaseModel abstract contract (predict, predict_proba, save, load)
│   ├── placeholder_model.py   # Deterministic rule-assisted Phase 1 placeholder model
│   └── mock_model.py           # Explicit MockClassifierModel tagged as is_placeholder=True
├── classifiers/                # Multi-signal risk aggregator
│   ├── __init__.py
│   ├── schemas.py              # ClassifierOutput, ClassifierLabel, MLPredictionResult
│   ├── base.py                 # BaseClassifier abstract contract
│   ├── email_classifier.py     # Concrete EmailClassifier uniting preprocessing, features & model
│   └── mock_classifier.py      # Deterministic MockClassifier for development/testing
├── service/                    # High-level service wrapper for backend integration
│   ├── __init__.py
│   └── inference_service.py    # Thread-safe MLInferenceService returning MLInferenceResult
├── data/                       # Directory structure for future training datasets (git-ignored)
│   ├── train/                  # Training data (.gitkeep)
│   ├── val/                    # Validation data (.gitkeep)
│   └── test/                   # Test data (.gitkeep)
├── artifacts/                  # Export directory for trained model weights (.gitkeep)
├── training/                   # Offline model training pipeline stubs
│   ├── README.md               # Training pipeline documentation
│   ├── base_trainer.py         # BaseTrainer interface for Phase 2 model training
│   ├── dataset_loader.py       # Email dataset loading & splitting abstraction
│   └── train_pipeline.py      # End-to-end training pipeline orchestrator
├── evaluation/                 # Metrics & benchmark evaluation utilities
│   ├── __init__.py
│   ├── metrics.py              # Accuracy, Precision, Recall, F1, Confusion Matrix
│   └── evaluator.py            # ModelEvaluator benchmark harness
└── tests/                      # Unit & integration test suite
    ├── __init__.py
    ├── test_config.py
    ├── test_preprocessing.py
    ├── test_features.py
    ├── test_models.py
    ├── test_classifiers.py
    ├── test_inference.py
    ├── test_training.py
    └── test_evaluation.py
```

---

## 3. Responsibilities of Each Component

| Component | Responsible For |
|---|---|
| **`config/ml_config.py`** | Centralized configuration for threshold values, model version tags, max sequence lengths, and execution timeouts. |
| **`preprocessing/email_preprocessor.py`** | Converts raw email payloads into a clean `ProcessedEmail` structure, removing HTML tags, normalizing whitespace, and extracting embedded URLs, emails, and structural indicator flags. |
| **`features/composite_extractor.py`** | Runs 6 specialized feature extractors (subject, body, URL, sender, keyword, structure) to produce a unified, serializable `FeatureVector`. |
| **`models/base.py`** | Strict abstract interface (`BaseModel`) enforcing `predict()`, `predict_proba()`, `is_placeholder()`, `save()`, `load()`, and `get_metadata()`. |
| **`models/mock_model.py`** | Deterministic `MockClassifierModel` explicitly tagged with `is_placeholder = True`. |
| **`classifiers/mock_classifier.py`** | High-level `MockClassifier` producing standardized `ClassifierOutput` (`"phishing"`, `"suspicious"`, `"benign"`, `"unknown"`). |
| **`service/inference_service.py`** | Public entry point (`MLInferenceService`) that orchestrates the 4-stage pipeline (preprocessing $\rightarrow$ features $\rightarrow$ classifier $\rightarrow$ result), tracks execution latency (`execution_time_ms`), and provides fail-safe error handling. |
| **`training/`** | Defines `BaseTrainer`, `EmailDatasetLoader`, and `TrainingPipeline` interfaces for future model training and artifact export. |
| **`evaluation/`** | Metric calculators (`compute_accuracy`, `compute_precision_recall_f1`, `compute_confusion_matrix`) and `ModelEvaluator` benchmark runner. |

---

## 4. ML Result Format & Integration

`MLInferenceService.analyze_email()` produces a structured result (`MLInferenceResult`) matching:

```json
{
  "source": "ml",
  "label": "phishing",
  "confidence": 0.85,
  "signals": [
    "Credential harvesting language or login verification cues detected.",
    "High urgency or immediate action pressure detected in text."
  ],
  "execution_time_ms": 0.79,
  "model_version": "mock-v1.0.0-phase1",
  "is_placeholder": true
}
```

- **`source`**: Always `"ml"`.
- **`label`**: `"phishing"`, `"suspicious"`, `"benign"`, or `"unknown"`.
- **`confidence`**: Validated score bounded between $[0.0, 1.0]$.
- **`signals`**: Human-readable threat explanation strings passed to Member 6 / Risk Engine.

---

## 5. How a Future Trained Model Will Plug Into the System

The architecture is explicitly designed so that a real trained model (e.g., fine-tuned DeBERTa, TF-IDF + XGBoost) can replace the mock classifier without altering any backend API or service contracts.

### Step-by-Step Plug-in Procedure:
1. **Train Model**: Use `ml/training/train_pipeline.py` or an external training script to train your model offline.
2. **Implement `BaseModel`**: Create `ml/models/trained_model.py` inheriting from `BaseModel`:
   ```python
   from ml.models.base import BaseModel
   from ml.features.base import FeatureVector

   class TrainedDeBERTaModel(BaseModel):
       def predict(self, feature_vector: FeatureVector) -> int:
           ...
       def predict_proba(self, feature_vector: FeatureVector) -> Dict[str, float]:
           ...
   ```
3. **Update Model Instantiation**: Pass the new model instance to `MockClassifier` or `EmailClassifier`:
   ```python
   trained_model = TrainedDeBERTaModel()
   trained_model.load("ml/artifacts/deberta_v3.pt")
   classifier = MockClassifier(model=trained_model)
   service = MLInferenceService(classifier=classifier)
   ```
4. **Zero Upstream Modifications**: Upstream callers calling `service.analyze_email(payload)` receive the identical `MLInferenceResult` contract.

---

## 6. What is Intentionally NOT Implemented in Phase 1

To maintain strict system boundaries and lightweight architecture, the following items are intentionally deferred to Phase 2:
- Heavy deep learning binary weights (`.bin`, `.pt`, `.safetensors`) committed to Git.
- Real-time online model retraining or live cloud model registry APIs.
- MailTrace system risk score calculation or delivery policy decisions (`DELIVER`/`QUARANTINE`).
- Direct database calls or external threat intelligence API queries.
