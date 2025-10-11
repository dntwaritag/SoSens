# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import create_model, Field
import joblib
import numpy as np
import os
from typing import List, Optional

# --- Resolve paths robustly ---
THIS_DIR = os.path.dirname(os.path.abspath(__file__))         # .../SoSens/app
PROJECT_ROOT = os.path.dirname(THIS_DIR)                      # .../SoSens
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")             # .../SoSens/models

MODEL_PATH = os.path.join(MODELS_DIR, "baseline_model.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
LE_PATH = os.path.join(MODELS_DIR, "label_encoder.pkl")
FEATURE_NAMES_PATH = os.path.join(MODELS_DIR, "feature_names.pkl")

# Fallback feature names (used if real feature_names not present)
FALLBACK_FEATURES = [
    "Ph","K","P","N","Zn","S","QV2M-W","QV2M-Sp","QV2M-Su",
    "QV2M-Au","T2M_MIN-W","T2M_MIN-Sp","WD10M","PRECTOTCORR-W"
]

app = FastAPI(title="Crop Recommendation API", docs_url="/docs")

# Model artifacts (loaded if available)
_model = None
_scaler = None
_label_encoder = None
_feature_names = None

def load_artifacts_if_available():
    global _model, _scaler, _label_encoder, _feature_names
    # Load model
    if os.path.exists(MODEL_PATH):
        try:
            _model = joblib.load(MODEL_PATH)
            print(f"Loaded model from {MODEL_PATH}")
        except Exception as e:
            print("Error loading model:", e)
            _model = None
    else:
        print(f"Model not found at {MODEL_PATH}")

    # Load scaler
    if os.path.exists(SCALER_PATH):
        try:
            _scaler = joblib.load(SCALER_PATH)
            print(f"Loaded scaler from {SCALER_PATH}")
        except Exception as e:
            print("Error loading scaler:", e)
            _scaler = None
    else:
        print(f"Scaler not found at {SCALER_PATH}")

    # Load label encoder
    if os.path.exists(LE_PATH):
        try:
            _label_encoder = joblib.load(LE_PATH)
            print(f"Loaded label encoder from {LE_PATH}")
        except Exception as e:
            print("Error loading label encoder:", e)
            _label_encoder = None
    else:
        print(f"Label encoder not found at {LE_PATH}")

    # Load feature names
    if os.path.exists(FEATURE_NAMES_PATH):
        try:
            _feature_names = joblib.load(FEATURE_NAMES_PATH)
            print(f"Loaded feature_names from {FEATURE_NAMES_PATH}")
        except Exception as e:
            print("Error loading feature_names:", e)
            _feature_names = None
    else:
        print(f"Feature names not found at {FEATURE_NAMES_PATH}")

# Attempt to load at import time (safe)
load_artifacts_if_available()

@app.get("/status")
def status():
    return {
        "project_root": PROJECT_ROOT,
        "models_dir": MODELS_DIR,
        "model_loaded": bool(_model),
        "scaler_loaded": bool(_scaler),
        "label_encoder_loaded": bool(_label_encoder),
        "feature_names_available": bool(_feature_names),
        "feature_count": len(_feature_names) if _feature_names else None
    }

@app.get("/feature-names")
def feature_names():
    """Return real feature names if available, otherwise return fallback list."""
    if _feature_names:
        return {"feature_names": _feature_names}
    return {"feature_names": FALLBACK_FEATURES, "note": "fallback list used — run training to save real feature_names."}

def get_active_feature_names() -> List[str]:
    return _feature_names if _feature_names else FALLBACK_FEATURES

def build_input_model():
    names = get_active_feature_names()
    fields = {name: (float, Field(..., description=name)) for name in names}
    return create_model("SoilInput", **fields)  # type: ignore

@app.post("/predict")
def predict(payload: dict):
    """
    Expect a JSON payload with numeric features matching the active feature list.
    Returns 503 if the model or scaler or label encoder are not loaded.
    """
    if not (_model and _scaler and _label_encoder):
        raise HTTPException(status_code=503, detail="Model artifacts not fully loaded. Run training to create 'models/' artifacts.")

    names = get_active_feature_names()
    try:
        x = np.array([[float(payload[k]) for k in names]], dtype=float)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing feature in payload: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload values: {e}")

    x_scaled = _scaler.transform(x)
    probs = _model.predict_proba(x_scaled)[0] if hasattr(_model, "predict_proba") else None
    pred_idx = int(_model.predict(x_scaled)[0])
    label = _label_encoder.inverse_transform([pred_idx])[0]

    resp = {"predicted_label": label, "predicted_label_index": pred_idx}
    if probs is not None:
        resp["confidence"] = float(np.max(probs))
        topk_idx = np.argsort(probs)[::-1][:3]
        resp["top3"] = [{"label": str(_label_encoder.inverse_transform([int(i)])[0]), "prob": float(probs[i])} for i in topk_idx]
    return resp
