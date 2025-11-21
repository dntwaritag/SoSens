"""
Improved ML Model Training with realistic Rwanda soil data
Place this file in: C:\Users\ntwar\OneDrive\Desktop\BSE-Project\Capstone\SoSens\
Run: python train_ml_models.py
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from pathlib import Path

# Set correct path
project_root = Path(__file__).parent
models_dir = project_root / 'app' / 'models'
models_dir.mkdir(parents=True, exist_ok=True)

print("="*80)
print(" SoSens ML Model Training - Improved Rwanda Soil Data")
print("="*80)
print(f"\nModels Directory: {models_dir}\n")

# ============================================================================
# STEP 1: CREATE REALISTIC RWANDA SOIL TRAINING DATA
# ============================================================================

print("[1/6] Creating realistic Rwanda soil dataset...")

np.random.seed(42)
training_data = []

# BEANS - Acidic soil, low-medium nutrients
# Common in southern Rwanda, volcanic soils
for _ in range(200):
    training_data.append({
        'Ph': np.random.normal(5.8, 0.5),      # Acidic
        'N': np.random.normal(25, 10),         # Low nitrogen
        'P': np.random.normal(12, 6),          # Low phosphorus
        'K': np.random.normal(100, 25),        # Low potassium
        'Zn': np.random.normal(1.5, 0.8),      # Low zinc
        'S': np.random.normal(10, 3),          # Low sulfur
        'Crop': 'Beans'
    })

# MAIZE - Neutral, HIGH nutrients (demanding crop)
# Best in central/western Rwanda, fertile zones
for _ in range(200):
    training_data.append({
        'Ph': np.random.normal(6.8, 0.5),      # Neutral
        'N': np.random.normal(90, 15),         # HIGH nitrogen
        'P': np.random.normal(50, 10),         # HIGH phosphorus
        'K': np.random.normal(250, 40),        # HIGH potassium
        'Zn': np.random.normal(4.0, 1.0),      # Good zinc
        'S': np.random.normal(25, 4),          # Good sulfur
        'Crop': 'Maize'
    })

# CASSAVA - Highly acidic, very LOW nutrients
# Tolerates poor soils, marginal zones
for _ in range(150):
    training_data.append({
        'Ph': np.random.normal(5.2, 0.6),      # Very acidic
        'N': np.random.normal(15, 8),          # Very low N
        'P': np.random.normal(8, 4),           # Very low P
        'K': np.random.normal(60, 20),         # Very low K
        'Zn': np.random.normal(1.0, 0.6),      # Very low Zn
        'S': np.random.normal(8, 2),           # Very low S
        'Crop': 'Cassava'
    })

# POTATO - Neutral-slightly acidic, MEDIUM-HIGH nutrients
# Highland zones (Musanze, Ruhengeri)
for _ in range(180):
    training_data.append({
        'Ph': np.random.normal(6.5, 0.4),      # Neutral
        'N': np.random.normal(65, 12),         # Medium-high N
        'P': np.random.normal(40, 8),          # Medium-high P
        'K': np.random.normal(200, 35),        # Medium-high K
        'Zn': np.random.normal(3.5, 0.8),      # Good Zn
        'S': np.random.normal(20, 3),          # Good S
        'Crop': 'Potato'
    })

# RICE - Neutral, MEDIUM nutrients (wetland zones)
# Bugesera, Gatsibo, Ngoma districts
for _ in range(150):
    training_data.append({
        'Ph': np.random.normal(6.2, 0.5),      # Neutral
        'N': np.random.normal(50, 12),         # Medium N
        'P': np.random.normal(30, 8),          # Medium P
        'K': np.random.normal(150, 30),        # Medium K
        'Zn': np.random.normal(2.5, 0.8),      # Medium Zn
        'S': np.random.normal(16, 3),          # Medium S
        'Crop': 'Rice'
    })

# WHEAT - Neutral-alkaline, MEDIUM-HIGH nutrients
# Cool highland zones (above 1800m)
for _ in range(120):
    training_data.append({
        'Ph': np.random.normal(7.0, 0.5),      # Neutral-alkaline
        'N': np.random.normal(70, 13),         # Medium-high N
        'P': np.random.normal(35, 8),          # Medium-high P
        'K': np.random.normal(220, 35),        # Medium-high K
        'Zn': np.random.normal(3.8, 0.9),      # Good Zn
        'S': np.random.normal(22, 3),          # Good S
        'Crop': 'Wheat'
    })

df = pd.DataFrame(training_data)

# Clip to realistic ranges
df['Ph'] = df['Ph'].clip(4.0, 8.5)
df['N'] = df['N'].clip(5, 150)
df['P'] = df['P'].clip(2, 80)
df['K'] = df['K'].clip(30, 350)
df['Zn'] = df['Zn'].clip(0.2, 7.0)
df['S'] = df['S'].clip(3, 35)

print(f"    Created {len(df)} training samples")
print(f"\n   Crop Distribution:")
for crop, count in df['Crop'].value_counts().items():
    print(f"      {crop:10s}: {count:3d} samples")

print(f"\n   Soil Parameter Ranges (across all crops):")
print(f"      pH:  {df['Ph'].min():.2f} - {df['Ph'].max():.2f}")
print(f"      N:   {df['N'].min():.1f} - {df['N'].max():.1f} kg/ha")
print(f"      P:   {df['P'].min():.1f} - {df['P'].max():.1f} kg/ha")
print(f"      K:   {df['K'].min():.1f} - {df['K'].max():.1f} kg/ha")
print(f"      Zn:  {df['Zn'].min():.2f} - {df['Zn'].max():.2f} mg/kg")
print(f"      S:   {df['S'].min():.1f} - {df['S'].max():.1f} mg/kg")

# ============================================================================
# STEP 2: PREPARE FEATURES AND TARGETS
# ============================================================================

print("\n[2/6] Preparing features and targets...")

X = df[['Ph', 'N', 'P', 'K', 'Zn', 'S']]
y = df['Crop']

print(f"    Features shape: {X.shape}")
print(f"    Target shape: {y.shape}")

# ============================================================================
# STEP 3: CREATE AND TRAIN SCALER
# ============================================================================

print("\n[3/6] Training feature scaler...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

scaler_path = models_dir / 'feature_scaler.pkl'
joblib.dump(scaler, scaler_path)
print(f"    Scaler saved: {scaler_path}")

# ============================================================================
# STEP 4: CREATE AND TRAIN LABEL ENCODER
# ============================================================================

print("\n[4/6] Training label encoder...")

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

encoder_path = models_dir / 'label_encoder.pkl'
joblib.dump(encoder, encoder_path)
print(f"    Encoder classes: {list(encoder.classes_)}")
print(f"    Encoder saved: {encoder_path}")

# ============================================================================
# STEP 5: TRAIN RANDOM FOREST MODEL (IMPROVED)
# ============================================================================

print("\n[5/6] Training Random Forest model...")

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Better hyperparameters for multi-class classification
model = RandomForestClassifier(
    n_estimators=300,          # More trees
    max_depth=20,              # Deeper trees
    min_samples_split=3,       # Lower split requirement
    min_samples_leaf=1,        # Lower leaf requirement
    max_features='sqrt',       # Better feature selection
    bootstrap=True,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced_subsample'
)

model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)
y_pred_train = model.predict(X_train)

# Accuracy
train_accuracy = accuracy_score(y_train, y_pred_train)
test_accuracy = accuracy_score(y_test, y_pred)

# Cross-validation
cv_scores = cross_val_score(model, X_scaled, y_encoded, cv=5)

print(f"\n  Training set accuracy: {train_accuracy:.2%}")
print(f"    Test set accuracy: {test_accuracy:.2%}")
print(f"    Cross-validation scores: {cv_scores}")
print(f"    Mean CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

print(f"\n   Classification Report:")
print(classification_report(y_test, y_pred, target_names=encoder.classes_, digits=3))

# Feature importance
feature_names = ['Ph', 'N', 'P', 'K', 'Zn', 'S']
importance_dict = dict(zip(feature_names, model.feature_importances_))
print(f"\n   Feature Importance:")
for feat, imp in sorted(importance_dict.items(), key=lambda x: x[1], reverse=True):
    bar = '█' * int(imp * 50)
    print(f"      {feat:3s}: {imp:.4f} {bar}")

# Save model
model_path = models_dir / 'rwanda_soil_model_random_forest.pkl'
joblib.dump(model, model_path)
print(f"\n  Model saved: {model_path}")
print(f"      Size: {os.path.getsize(model_path) / 1024:.1f} KB")

# ============================================================================
# STEP 6: SAVE METADATA
# ============================================================================

print("\n[6/6] Saving metadata...")

metadata = {
    'model_type': 'RandomForestClassifier',
    'n_estimators': 300,
    'max_depth': 20,
    'train_accuracy': float(train_accuracy),
    'test_accuracy': float(test_accuracy),
    'cv_mean_accuracy': float(cv_scores.mean()),
    'cv_std': float(cv_scores.std()),
    'classes': encoder.classes_.tolist(),
    'features': feature_names,
    'training_samples': len(df),
    'test_samples': len(X_test),
    'version': '2.0',
    'created_date': pd.Timestamp.now().isoformat(),
    'crop_info': {
        'Beans': {
            'description': 'Tolerates acidic soils',
            'optimal_ph': '5.5-6.2',
            'nutrient_level': 'Low-Medium',
            'zones': 'Southern Rwanda, volcanic areas'
        },
        'Maize': {
            'description': 'High nutrient demanding crop',
            'optimal_ph': '6.5-7.0',
            'nutrient_level': 'High',
            'zones': 'Central/Western Rwanda, fertile zones'
        },
        'Cassava': {
            'description': 'Tolerates poor soils and droughts',
            'optimal_ph': '5.0-6.0',
            'nutrient_level': 'Very Low',
            'zones': 'Marginal lands, dry zones'
        },
        'Potato': {
            'description': 'Medium-high nutrient requirement',
            'optimal_ph': '6.3-7.0',
            'nutrient_level': 'Medium-High',
            'zones': 'Highland zones (>1800m)'
        },
        'Rice': {
            'description': 'Wetland crop, medium nutrients',
            'optimal_ph': '6.0-6.5',
            'nutrient_level': 'Medium',
            'zones': 'Wetland areas, Bugesera, Gatsibo'
        },
        'Wheat': {
            'description': 'Cool highland crop',
            'optimal_ph': '6.8-7.5',
            'nutrient_level': 'Medium-High',
            'zones': 'Cool highlands (>1800m)'
        }
    },
    'soil_guidelines': {
        'Ph': {'min': 4.0, 'max': 8.5, 'optimal': '6.0-7.0'},
        'N': {'min': 5, 'max': 150, 'optimal': '40-80', 'unit': 'kg/ha'},
        'P': {'min': 2, 'max': 80, 'optimal': '20-40', 'unit': 'kg/ha'},
        'K': {'min': 30, 'max': 350, 'optimal': '150-250', 'unit': 'kg/ha'},
        'Zn': {'min': 0.2, 'max': 7.0, 'optimal': '2.0-4.0', 'unit': 'mg/kg'},
        'S': {'min': 3, 'max': 35, 'optimal': '15-25', 'unit': 'mg/kg'}
    }
}

metadata_path = models_dir / 'model_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"   ✓ Metadata saved: {metadata_path}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print(" MODEL TRAINING COMPLETE")
print("="*80)

print(f"\n All files created in: {models_dir}")
print(f"\n Model Performance:")
print(f"   • Training Accuracy: {train_accuracy:.2%}")
print(f"   • Test Accuracy: {test_accuracy:.2%}")
print(f"   • 5-Fold CV Mean: {cv_scores.mean():.2%}")
print(f"   • Supported Crops: {len(encoder.classes_)}")

print(f"\n Next steps:")
print(f"   1. Start server: python -m uvicorn app.app:app --reload")
print(f"   2. Check for: '✓ ML Model loaded successfully'")
print(f"   3. Test prediction with realistic soil data")
print(f"   4. Commit models: git add app/models/")

print("\n" + "="*80 + "\n")