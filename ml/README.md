# MailTrace AI — AI/ML/NLP Module (Phase 1 Foundation)

## 1. Purpose of the Module

The `ml` package provides the machine learning and natural language processing (NLP) foundation for **MailTrace AI**, a pre-delivery email security gateway.

The primary responsibilities of this module are:
- Cleaning and tokenizing raw email content (headers, subject line, body text, HTML markup, embedded URLs/emails).
- Extracting statistical text metrics, domain-specific security keyword indicators, and semantic features.
- Running multi-signal ML detection across key threat categories:
  1. **Phishing Classification**: Credential harvesting and spoofed login links.
  2. **Suspicious-Language Detection**: High urgency, pressure tactics, and unusual tone/capitalization.
  3. **Social-Engineering Detection**: Wire transfer requests, payroll fraud, secrecy demands, and authority pressure.
  4. **Malicious-Content Classification**: Malicious download cues, suspicious attachment references, and executable payload indicators.
  5. **Impersonation Signals**: Executive (CEO/CFO), IT helpdesk, and brand/admin role spoofing cues.
- Providing a thread-safe, fail-safe **Inference Service** interface for backend orchestrators to query during pre-delivery email inspection.
- Establishing modular interfaces for offline model training, dataset ingestion, and metrics evaluation.

---

## 2. Folder Structure

```text
ml/
├── README.md                   # Complete module architecture documentation
├── __init__.py                 # Root package initialization
├── config/                     # Configuration management
│   ├── __init__.py
│   └── ml_config.py            # Dataclasses for model, feature, and runtime settings
├── preprocessing/              # Email text normalization & indicator extraction
│   ├── __init__.py
│   ├── base.py                 # BasePreprocessor interface & ProcessedEmail schema
│   └── email_preprocessor.py   # Concrete HTML cleaner, token/URL/email extractor
├── features/                   # NLP & statistical feature extractors
│   ├── __init__.py
│   ├── base.py                 # BaseFeatureExtractor & FeatureVector schema
│   ├── text_features.py        # Statistical metrics (char/word count, uppercase ratio, etc.)
│   └── keyword_features.py     # Threat signal keyword scanner across 5 categories
├── models/                     # Model interface & implementations
│   ├── __init__.py
│   ├── base.py                 # BaseModel abstract contract (predict, predict_proba, save, load)
│   └── placeholder_model.py   # Deterministic rule-assisted Phase 1 placeholder model
├── classifiers/                # Multi-signal risk aggregator
│   ├── __init__.py
│   ├── schemas.py              # MLPredictionResult, SignalVerdict, ClassificationCategory
│   ├── base.py                 # BaseClassifier abstract contract
│   └── email_classifier.py     # Concrete EmailClassifier uniting preprocessing, features & model
├── service/                    # High-level service wrapper for backend integration
│   ├── __init__.py
│   └── inference_service.py    # Thread-safe MLInferenceService with timing & fail-safe fallback
├── training/                   # Offline model training pipeline stubs
│   ├── __init__.py
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
    └── test_evaluation.py
```

---

## 3. Responsibilities of Each Component

| Component | Responsible For |
|---|---|
| **`config/ml_config.py`** | Centralized configuration for threshold values, model version tags, max sequence lengths, and execution timeouts. |
| **`preprocessing/email_preprocessor.py`** | Converts raw email payloads into a clean `ProcessedEmail` structure, removing HTML tags, normalizing whitespace, and extracting embedded URLs and email addresses. |
| **`features/text_features.py`** | Calculates statistical metrics (character counts, word counts, uppercase letter ratios, punctuation frequencies, URL density). |
| **`features/keyword_features.py`** | Scans text for domain threat keywords (urgency, credential harvesting, social engineering, malicious payload cues, impersonation). |
| **`models/base.py`** | Strict abstract interface (`BaseModel`) enforcing `predict()`, `predict_proba()`, `save()`, `load()`, and `get_metadata()`. |
| **`models/placeholder_model.py`** | Deterministic Phase 1 placeholder model calculating risk scores without requiring external neural model binaries. |
| **`classifiers/email_classifier.py`** | High-level orchestrator producing individual `SignalVerdict`s for all 5 security signals and computing the overall classification (`SAFE`, `SUSPICIOUS`, `MALICIOUS`). |
| **`service/inference_service.py`** | Public service entry point (`MLInferenceService`) that wraps `EmailClassifier`, tracks execution latency (`execution_time_ms`), and provides fail-safe error handling. |
| **`training/`** | Defines `BaseTrainer`, `BaseDatasetLoader`, and `TrainingPipeline` interfaces for future model training and artifact export. |
| **`evaluation/`** | Functional metrics (`compute_accuracy`, `compute_precision_recall_f1`, `compute_confusion_matrix`) and `ModelEvaluator` benchmark runner. |

---

## 4. How a Future Trained Model Will Plug Into the System

The architecture is explicitly designed so that a real trained model (e.g., TF-IDF + XGBoost, DeBERTa, RoBERTa, or fine-tuned Transformer) can seamlessly replace the Phase 1 placeholder without altering any backend API or service contracts.

### Step-by-Step Plug-in Procedure:
1. **Train Model**: Use `ml/training/train_pipeline.py` or an external training script to train your model (e.g. Scikit-learn / PyTorch / HuggingFace).
2. **Implement `BaseModel`**: Create `ml/models/trained_model.py` inheriting from `BaseModel`:
   ```python
   from ml.models.base import BaseModel
   from ml.features.base import FeatureVector

   class TrainedDeBERTaModel(BaseModel):
       def predict(self, feature_vector: FeatureVector) -> int:
           ...
       def predict_proba(self, feature_vector: FeatureVector) -> Dict[str, float]:
           ...
       def load(self, filepath: str) -> bool:
           ...
   ```
3. **Update Model Instantiation**: Pass the new model instance to `EmailClassifier`:
   ```python
   trained_model = TrainedDeBERTaModel()
   trained_model.load("models/weights/v2.0.pt")
   classifier = EmailClassifier(model=trained_model)
   service = MLInferenceService(classifier=classifier)
   ```
4. **Zero Backend Changes**: Upstream callers calling `service.analyze_email(payload)` receive the identical `MLPredictionResult` contract.

---

## 5. What is Intentionally NOT Implemented in Phase 1

To keep Phase 1 lightweight, clean, and fast to execute, the following items are intentionally deferred to Phase 2:
- Heavy deep learning dependencies (e.g. `torch`, `transformers`, `tensorflow`) and large pre-trained binary weights (`.bin`, `.pt`, `.safetensors`).
- Fine-tuned BERT/RoBERTa weights or live embedding models.
- Production dataset pipeline connectors to live databases or external Cloud Storage buckets.
- Real-time online model retraining or active learning loops.
