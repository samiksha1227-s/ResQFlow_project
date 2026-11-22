This directory will contain the trained model files after running:

    python data/generate_synthetic_data.py
    python src/train.py

Expected files:
    severity_model.pkl   – Scikit-learn RandomForestClassifier (joblib format)
    severity_model.onnx  – ONNX export (requires skl2onnx)

⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
