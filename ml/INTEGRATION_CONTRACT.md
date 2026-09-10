# MailTrace AI — ML/NLP Integration Contract (Phase 1 Specification)

This document defines the formal integration contract for the **AI/ML/NLP Module (`ml`)** of **MailTrace AI**.
It specifies the inputs, processing flow, output contracts, label semantics, and integration patterns for downstream modules (such as Member 6 — Delivery Gateway Orchestration, Risk Engine, Evidence & Reporting, and Web UI).

---

## 1. Input Expected by the ML Inference Service

The entry point for email analysis is `MLInferenceService.analyze_email(email_input)` (or `run_inference_pipeline(email_input)`).

`email_input` is a flexible payload that accepts a Python `dict`, string, or object with attributes:

```json
{
  "from": "alice@example.com",
  "to": ["bob@example.com"],
  "cc": ["carol@example.com"],
  "subject": "URGENT: Verify Your Account Password",
  "body_text": "Please click http://192.168.1.50/verify to update your password immediately.",
  "body_html": "<div>Please click <a href='http://192.168.1.50/verify'>here</a> to update password.</div>",
  "urls": ["http://192.168.1.50/verify"],
  "metadata": {
    "headers_present": true
  }
}
```

### Flexible Field Mappings:
- **Sender**: Looked up via `from`, `sender`, or `sender_email`.
- **Recipients**: Looked up via `to`, `cc`, `bcc`, or `recipients` (list of strings or comma-separated string).
- **Subject**: Looked up via `subject` or `raw_subject` (handles `None` / omitted).
- **Body Content**: Looked up via `body_text`, `body_html`, `body`, `content`, or `text` (handles `None` / omitted).
- **URLs**: Looked up via `urls` or `extracted_urls` (handles `None` / `[]` / explicit list).

### Edge Case Handling:
- **Missing Subject**: Safely processed (`cleaned_subject=""`, `is_missing_subject=True`).
- **Empty Body**: Safely processed (`cleaned_body=""`, `is_empty_body=True`, `tokens=[]`).
- **Missing Sender**: Safely processed (`sender_email=None`, `sender_domain=None`, `is_missing_sender=True`).
- **Empty URL List**: Safely processed (`extracted_urls=[]`, `has_urls=False`).

---

## 2. Preprocessing Flow

Execution is handled by `EmailPreprocessor` (`ml/preprocessing/email_preprocessor.py`), which orchestrates two sub-components:

1. **Text Normalization (`TextNormalizer`)**:
   - Strips HTML tags (`<[^>]+>`)
   - Decodes HTML entities (e.g. `&amp;` $\rightarrow$ `&`, `&lt;` $\rightarrow$ `<`)
   - Normalizes whitespace and newlines
   - Extracts lowercase tokens
2. **Indicator Extraction (`IndicatorExtractor`)**:
   - Extracts sender email & domain (`sender_domain`)
   - Extracts recipient emails & recipient domains (`recipient_domains`)
   - Deduplicates embedded URLs and email addresses
   - Computes structural status flags (`is_missing_subject`, `is_empty_body`, `is_missing_sender`, `has_urls`)
   - Computes basic text statistics (character counts, uppercase letter ratio, digit ratio, exclamation frequencies)

Output: `ProcessedEmail` dataclass.

---

## 3. Feature Extraction Flow

Execution is handled by `EmailFeatureExtractor` (`ml/features/composite_extractor.py`), which aggregates 6 specialized feature sub-extractors:

1. **Subject Text Characteristics** (`ml/features/subject_features.py`): Subject length, word count, uppercase ratio, digit ratio, exclamations, missing subject flag.
2. **Body Text Characteristics** (`ml/features/body_features.py`): Body length, line count, token count, uppercase ratio, digit ratio, special character ratio, empty body flag.
3. **URL-related Indicators** (`ml/features/url_features.py`): URL count, `has_urls`, IP-host URL count, suspicious TLD count (`.xyz`, `.top`, `.tk`, `.zip`), average URL length, url-to-word ratio.
4. **Sender-related Indicators** (`ml/features/sender_features.py`): Sender presence, domain length, freemail provider flag (`gmail.com`, `yahoo.com`), sender vs recipient domain mismatch.
5. **Suspicious-Language Indicators** (`ml/features/keyword_features.py`): Urgency keyword count, credential harvesting keyword count, social engineering keyword count, malicious payload cues, impersonation keyword count, combined pressure score.
6. **Message Structure Indicators** (`ml/features/structure_features.py`): Recipient count, recipient domain count, HTML presence, embedded email count, header presence.

Output: `FeatureVector` dataclass (serializable via `to_dict()`, `to_json()`, `to_flat_vector()`).

---

## 4. Classifier Interface

Abstract base class `BaseClassifier` (`ml/classifiers/base.py`) enforces standard prediction methods:

```python
class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, email_input: Any) -> Union[ClassifierOutput, MLPredictionResult]:
        pass

    @abstractmethod
    def predict_verdict(self, email_input: Any) -> ClassifierOutput:
        pass
```

### Implementations:
- `MockClassifier` (`ml/classifiers/mock_classifier.py`): Deterministic Phase 1 placeholder classifier returned by default. Explicitly tagged with `is_placeholder = True`.
- `EmailClassifier` (`ml/classifiers/email_classifier.py`): Multi-signal risk aggregator uniting preprocessing, features, and model.

---

## 5. ML Output Structure

`MLInferenceService.analyze_email()` returns an `MLInferenceResult` object.
Its `.to_dict()` method produces the exact dictionary schema required by MailTrace architecture:

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
  "is_placeholder": true,
  "metadata": {
    "model_name": "mock_classifier_placeholder",
    "is_placeholder": true,
    "url_count": 1,
    "word_count": 24,
    "has_sender": true
  }
}
```

---

## 6. Meaning of Label

The `label` field represents the pure ML text/semantic classification result:

| Label | Meaning |
|---|---|
| `"phishing"` | High probability of phishing, credential harvesting, or malicious link/download cues in text. |
| `"suspicious"` | Moderate risk; contains high urgency, authority pressure, freemail sender, or domain anomalies requiring caution. |
| `"benign"` | Clean text tone with no overt security threat signals or credential harvesting patterns. |
| `"unknown"` | Input text missing essential content, or fail-safe fallback mode activated due to processing error. |

---

## 7. Meaning of Confidence

- `confidence`: A floating-point number strictly validated in the range $[0.0, 1.0]$.
- Represents the model's mathematical certainty for the predicted `label`.
- A score of `0.0` indicates total uncertainty or fail-safe mode, while `0.95+` indicates extremely high certainty.

---

## 8. Meaning of Signals

- `signals`: A `List[str]` of clear, human-readable explanation strings.
- Details the specific threat indicators detected by the ML module (e.g. `"Credential harvesting language detected"`, `"Direct IP address URL detected in email content"`).
- Signals are preserved for forensic reporting, evidence cards, and UI security verdict badges.

---

## 9. How Member 6 / Integration / Risk Layer Consumes the ML Result

Member 6 (Delivery Gateway Orchestration & Risk Engine) imports and queries `MLInferenceService`:

```python
from ml.service import MLInferenceService, MLInferenceResult

# 1. Instantiate ML Inference Service
ml_service = MLInferenceService()

# 2. Analyze incoming email payload during pre-delivery scan
ml_result: MLInferenceResult = ml_service.analyze_email(raw_email_dict)
result_dict = ml_result.to_dict()

# 3. Extract pure ML outputs
source = result_dict["source"]            # Always "ml"
ml_label = result_dict["label"]          # "phishing" | "suspicious" | "benign" | "unknown"
confidence = result_dict["confidence"]    # 0.85
signals = result_dict["signals"]          # List of explanation strings
latency_ms = result_dict["execution_time_ms"] # Latency tracking

# 4. Integrate into MailTrace Risk & Policy Engine (Member 6 / Correlation)
# Note: ML layer ONLY provides pure ML signals.
# The Risk Engine combines ml_label + Header Forensics + URL/Attachment analysis
# to calculate the overall system risk score and make delivery decisions (DELIVER/QUARANTINE).
```

### Strict System Boundary Reminders:
- The ML module **does NOT** compute the final MailTrace system risk score.
- The ML module **does NOT** make delivery decisions (`DELIVER`, `WARN`, `QUARANTINE`, `REJECT`).
- The ML module **does NOT** perform database queries or quarantine store operations.
- The ML module **does NOT** make calls to external threat-intelligence APIs.

---

## 10. How a Future Trained Model Can Replace the Mock Classifier

The architecture is explicitly designed so a real trained model (e.g., fine-tuned DeBERTa, TF-IDF + XGBoost) can replace the mock classifier with **zero breaking changes**:

1. **Train & Export Weights**: Train your model offline and save weight artifacts (`.pt` or `.pkl`) to `ml/artifacts/`.
2. **Implement `BaseModel`**: Create `TrainedDeBERTaModel` inheriting from `BaseModel` (`ml/models/base.py`). Override `predict()` and `predict_proba()`.
3. **Instantiate Service with Trained Model**:
   ```python
   trained_model = TrainedDeBERTaModel()
   trained_model.load("ml/artifacts/deberta_v3.pt")
   
   classifier = MockClassifier(model=trained_model)
   # Or classifier = EmailClassifier(model=trained_model)
   
   service = MLInferenceService(classifier=classifier)
   ```
4. **Zero Upstream Modifications**: Downstream callers calling `service.analyze_email(email_input)` receive the identical `MLInferenceResult` schema.
