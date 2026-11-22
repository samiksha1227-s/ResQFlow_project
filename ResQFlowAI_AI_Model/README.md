# ResQFlowAI – AI Severity Model

> **⚠️ SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE ⚠️**
>
> This project uses entirely fabricated synthetic data generated algorithmically for hackathon demonstration purposes. It is **NOT** a medical diagnosis system, clinical triage tool, or professional emergency decision-making tool. Do not use this system in real emergency situations.

---

## Overview

`ResQFlowAI_AI_Model` is the machine-learning module of the **ResQFlowAI** hackathon project. It classifies emergency incident severity into four levels:

| Level | Icon | Meaning |
|-------|------|---------|
| CRITICAL | 🔴 | Immediate life threat – maximum response |
| HIGH | 🟠 | Serious condition – priority response |
| MEDIUM | 🟡 | Non-life-threatening but needs attention |
| LOW | 🟢 | Minor incident – standard response |

The model is trained entirely on **synthetic data** and runs **100% locally** — no cloud APIs, no external services.

---

## Project Structure

```
ResQFlowAI_AI_Model/
├── README.md
├── requirements.txt
├── setup.bat                         # One-click setup (Windows)
├── data/
│   ├── generate_synthetic_data.py    # Generates 1200 synthetic samples
│   └── synthetic_emergency_data.csv  # Generated CSV (after running above)
├── models/
│   ├── severity_model.pkl            # Trained sklearn model (after training)
│   └── severity_model.onnx          # ONNX export (if skl2onnx available)
├── src/
│   ├── __init__.py
│   ├── preprocessing.py             # Feature engineering utilities
│   ├── train.py                     # Model training script
│   ├── evaluate.py                  # Model evaluation & metrics
│   ├── predict.py                   # CLI prediction tool
│   ├── inference.py                 # Python inference wrapper class
│   └── rule_engine.py              # Pure rule-based fallback engine
└── tests/
    └── test_inference.py            # Integration test suite
```

---

## Input Features

| Feature | Type | Description |
|---------|------|-------------|
| `victim_count` | int | Number of victims (1–10) |
| `has_unconscious` | bool (0/1) | Any victim unconscious |
| `has_bleeding` | bool (0/1) | Active bleeding present |
| `has_breathing_difficulty` | bool (0/1) | Breathing difficulty observed |
| `has_visible_injury` | bool (0/1) | Visible injuries present |
| `has_critical_condition` | bool (0/1) | Critical medical condition |
| `age_group_critical` | bool (0/1) | Elderly or child involved |
| `vehicle_count` | int | Vehicles involved (1–5) |

---

## Quick Start

### Option A – One-Click Setup (Windows)

```bat
cd ResQFlowAI_AI_Model
setup.bat
```

This will create a venv, install packages, generate data, train the model, and run tests.

### Option B – Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate synthetic training data
python data/generate_synthetic_data.py

# 4. Train the model
python src/train.py

# 5. Evaluate
python src/evaluate.py

# 6. Run tests
python tests/test_inference.py
```

---

## Making Predictions

### Command-Line Tool

```bash
# Activate venv first
venv\Scripts\activate

# Basic prediction
python src/predict.py --victims 3 --unconscious 1 --bleeding 1 --breathing 1

# All options
python src/predict.py \
  --victims 4 \
  --unconscious 1 \
  --bleeding 1 \
  --breathing 0 \
  --visible-injury 1 \
  --critical 1 \
  --age-critical 1 \
  --vehicles 2

# JSON output (for backend integration)
python src/predict.py --victims 3 --unconscious 1 --json

# Force rule engine (no ML model)
python src/predict.py --victims 3 --unconscious 1 --force-rules
```

### Python API

```python
import sys
sys.path.insert(0, 'src')
from inference import SeverityInference

engine = SeverityInference()

result = engine.predict({
    "victim_count": 3,
    "has_unconscious": 1,
    "has_bleeding": 1,
    "has_breathing_difficulty": 0,
    "has_visible_injury": 1,
    "has_critical_condition": 0,
    "age_group_critical": 0,
    "vehicle_count": 2,
})

print(result)
# {
#   "severity": "CRITICAL",
#   "confidence": 0.94,
#   "method": "ONNX_MODEL",         # or "ML_MODEL" or "RULE_ENGINE"
#   "disclaimer": "SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE",
#   "details": {...}
# }
```

---

## Rule-Based Fallback Engine

The `RuleEngine` provides deterministic severity assessment with no ML dependency. It automatically activates if no trained model is found.

```python
from src.rule_engine import RuleEngine

engine = RuleEngine()
result = engine.assess({
    "victim_count": 2,
    "has_unconscious": 1,
    "has_critical_condition": 1,
    "has_breathing_difficulty": 1,
    # ... other fields default to 0
})
# result["method"] == "RULE_ENGINE"
# result["rules_triggered"] == ["CRIT_UNCONSCIOUS_BREATH_CRITICAL", ...]
```

### Rule Priority Table

| Rule | Severity | Confidence |
|------|----------|------------|
| Unconscious + breathing difficulty + critical condition | CRITICAL | 0.95 |
| ≥3 victims + unconscious + bleeding | CRITICAL | 0.90 |
| Unconscious + critical condition | CRITICAL | 0.88 |
| Any unconscious victim | HIGH | 0.85 |
| Bleeding + breathing difficulty | HIGH | 0.85 |
| Critical condition present | HIGH | 0.82 |
| ≥3 victims + visible injury | HIGH | 0.80 |
| Visible injury, conscious, ≤2 victims | MEDIUM | 0.75 |
| Bleeding, conscious, no breathing issues | MEDIUM | 0.72 |
| Multiple victims, no critical indicators | MEDIUM | 0.70 |
| Default (no indicators) | LOW | 0.60 |

---

## ONNX Export

The training script automatically attempts ONNX export via `skl2onnx`.

```bash
# Verify ONNX model works
python -c "
import onnxruntime as rt
import numpy as np
sess = rt.InferenceSession('models/severity_model.onnx')
X = np.array([[3,1,1,0,1,0,0,2]], dtype=np.float32)
print(sess.run(None, {'float_input': X}))
"
```

The `SeverityInference` class uses **ONNX Runtime** by default (fastest), falling back to the sklearn pickle if ONNX is unavailable.

---

## Backend Integration

The `SeverityInference` class is designed to plug into a REST API:

```python
# Example FastAPI endpoint
from fastapi import FastAPI
from inference import SeverityInference

app = FastAPI()
model = SeverityInference()   # loads once at startup

@app.post("/predict-severity")
def predict_severity(incident: dict):
    return model.predict(incident)
```

The returned `method` field tells the frontend whether the result came from `ONNX_MODEL`, `ML_MODEL`, or `RULE_ENGINE`.

---

## Inference Priority Chain

```
Request
  │
  ├─ ONNX model available? ──Yes──▶ onnxruntime inference (fastest)
  │
  ├─ sklearn .pkl available? ─Yes──▶ scikit-learn inference
  │
  └─ Fallback ────────────────────▶ RuleEngine (no ML deps required)
```

---

## Disclaimer

> **⚠️ SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE ⚠️**
>
> All training data is synthetically generated. The model has **not** been validated on real emergency data. This is a hackathon prototype for demonstration only. In real emergency situations, always follow official emergency protocols and rely on trained medical professionals.
