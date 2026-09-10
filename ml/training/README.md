# MailTrace AI — Offline ML Model Training Structure

## 1. Purpose of the Training Structure

This directory and configuration structure prepares **MailTrace AI** for future offline machine learning model development, dataset ingestion, model training, metric evaluation, and model weight artifact registration.

In Phase 1, the pipeline establishes modular data contracts, configuration objects, dataset directory locations, and training pipeline stubs without committing binary dataset files or trained model weights to source control.

---

## 2. Directory Layout & Artifact Storage

```text
ml/
├── data/                       # Dataset directories (ignored by git, tracked via .gitkeep)
│   ├── train/                  # Offline training dataset files (.csv, .jsonl, .parquet)
│   ├── val/                    # Validation dataset files (.csv, .jsonl)
│   └── test/                   # Test/evaluation benchmark dataset files (.csv, .jsonl)
├── artifacts/                  # Trained model weight artifacts (.pt, .safetensors, .pkl)
├── config/
│   └── training_config.py      # Dataclass holding safe default training hyperparameters
├── training/
│   ├── README.md               # Training pipeline documentation (this file)
│   ├── base_trainer.py         # Abstract interface for model trainers (BaseTrainer)
│   ├── dataset_loader.py       # Ingestion & splitting of raw email datasets (EmailDatasetLoader)
│   └── train_pipeline.py      # End-to-end training pipeline orchestrator (TrainingPipeline)
└── evaluation/
    ├── metrics.py              # Metric calculation functions (Accuracy, Precision, Recall, F1)
    └── evaluator.py            # Model benchmark evaluator (ModelEvaluator)
```

---

## 3. Component Responsibilities

| Component | Responsible For |
|---|---|
| **`ml/data/train/`** | Place offline email training dataset samples (`.csv`, `.jsonl`, `.parquet`). |
| **`ml/data/val/`** | Place validation split dataset samples used for hyperparameter tuning and early stopping. |
| **`ml/data/test/`** | Place held-out evaluation dataset samples used for benchmark testing. |
| **`ml/artifacts/`** | Target directory for exported trained model weights (`.pt`, `.bin`, `.pkl`). |
| **`config/training_config.py`** | Centralized configuration for batch size, epochs, learning rate, random seed, and dataset paths. |
| **`training/dataset_loader.py`** | Ingests raw data files from `ml/data/` directories and returns structured `DatasetSplit` instances. |
| **`training/base_trainer.py`** | Defines `BaseTrainer` interface (`train()`, `evaluate()`, `export_artifacts()`). |
| **`training/train_pipeline.py`** | Orchestrates dataset loading, feature preprocessing, model fitting, metric evaluation, and weight export. |

---

## 4. How a Future Real Training Pipeline Will Fit In (Phase 2 Plug-in Guide)

To train and plug a real production ML model into MailTrace AI in Phase 2:

### Step 1: Place Datasets
Copy your labeled email datasets into `ml/data/train/`, `ml/data/val/`, and `ml/data/test/`.
*(Files like `.csv` or `.jsonl` inside these directories are automatically ignored by `.gitignore` to keep the git repository lightweight).*

### Step 2: Configure Hyperparameters
Update `ml/config/training_config.py` or pass custom parameters to `TrainingConfig`:
```python
config = TrainingConfig(
    train_data_dir="ml/data/train/",
    model_architecture="deberta_v3_phishing",
    epochs=5,
    batch_size=32,
    learning_rate=2e-5
)
```

### Step 3: Implement `BaseTrainer`
Create a custom trainer class in `ml/training/custom_trainer.py` inheriting from `BaseTrainer`:
```python
from ml.training.base_trainer import BaseTrainer

class PyTorchDeBERTaTrainer(BaseTrainer):
    def train(self, train_data, validation_data=None):
        # Execute PyTorch / Scikit-Learn training loop
        ...
    def evaluate(self, test_data):
        ...
    def export_artifacts(self, export_dir):
        # Export weights to ml/artifacts/deberta_v3.pt
        ...
```

### Step 4: Export Model Weights
Run the training pipeline to export trained model weights to `ml/artifacts/`:
```python
pipeline = TrainingPipeline(config=config)
results = pipeline.run_pipeline()
# Exported weight file saved to ml/artifacts/deberta_v3.pt
```

### Step 5: Plug Model Into Application
Create a model class inheriting from `BaseModel` (`ml/models/base.py`):
```python
from ml.models.base import BaseModel

class TrainedDeBERTaModel(BaseModel):
    def load(self, filepath: str) -> bool:
        # Load weights from ml/artifacts/deberta_v3.pt
        ...
    def predict_proba(self, feature_vector: FeatureVector) -> Dict[str, float]:
        # Return real model probability distribution
        ...
```
Pass `TrainedDeBERTaModel` to `EmailClassifier` or `MLInferenceService`:
```python
model = TrainedDeBERTaModel()
model.load("ml/artifacts/deberta_v3.pt")
classifier = EmailClassifier(model=model)
service = MLInferenceService(classifier=classifier)
```

**Zero Downstream Modifications**: The API contracts, preprocessing layer, feature extraction layer, inference service, backend risk engine, and frontend UI remain completely unchanged!

---

## 5. Phase 1 Scope & Constraints Observed

- **No Dataset Downloads**: No external datasets are automatically fetched or downloaded during execution.
- **No Git Commits of Heavy Data/Weights**: `.gitignore` strictly ignores `.csv`, `.tsv`, `.jsonl`, `.pt`, `.bin`, `.safetensors`, `.onnx`, and `.pkl` files while maintaining directory structure via `.gitkeep`.
- **No Model Fabrication**: Models are explicitly marked with `is_placeholder = True`.
- **No External Training APIs**: Training code operates locally without remote API calls.
