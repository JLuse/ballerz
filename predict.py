#!/usr/bin/env python3
"""
Prediction script for the fantasy football analytics model.
Demonstrates how to use the trained model to make predictions.
"""

import sys
from pathlib import Path
import pandas as pd
import joblib

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.data.collect_data import FantasyDataCollector
from src.features.feature_engineering import FeatureEngineer


def load_model():
    """Load the trained model and feature columns."""
    model_path = Path("models/baseline_rf_model.joblib")
    feature_path = Path("models/feature_columns.txt")
    
    if not model_path.exists():
        raise FileNotFoundError("Model not found. Please run train_baseline.py first.")
    
    # Load model
    model = joblib.load(model_path)
    
    # Load feature columns
    with open(feature_path, 'r') as f:
        feature_columns = [line.strip() for line in f.readlines()]
    
    return model, feature_columns


def make_predictions(model, feature_columns, data):
    """
    Make predictions on new data.
    
    Args:
        model: Trained model
        feature_columns: List of feature column names
        data: DataFrame with features
        
    Returns:
        DataFrame with predictions
    """
    # Select features
    X = data[feature_columns].fillna(0)
    
    # Make predictions
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]
    
    # Add predictions to data
    result = data.copy()
    result['predicted_over_perform'] = predictions
    result['over_perform_probability'] = probabilities
    
    return result


def main():
    """Main prediction function."""
    print("=" * 60)
    print("FANTASY FOOTBALL ANALYTICS - PREDICTION DEMO")
    print("=" * 60)
    
    # Load model
    print("\n1. Loading trained model...")
    model, feature_columns = load_model()
    print(f"Model loaded with {len(feature_columns)} features")
    
    # Create sample data for prediction
    print("\n2. Creating sample data for prediction...")
    collector = FantasyDataCollector()
    raw_data = collector.create_sample_data("prediction_sample.csv")
    
    # Engineer features
    print("\n3. Engineering features...")
    engineer = FeatureEngineer()
    engineered_data = engineer.engineer_all_features(raw_data)
    
    # Make predictions
    print("\n4. Making predictions...")
    predictions = make_predictions(model, feature_columns, engineered_data)
    
    # Show results
    print("\n5. Prediction Results:")
    print("=" * 40)
    
    # Sample predictions
    sample_predictions = predictions[['player_name', 'team', 'week', 'fantasy_points', 
                                    'projection', 'predicted_over_perform', 
                                    'over_perform_probability']].head(10)
    
    print(sample_predictions.to_string(index=False))
    
    # Summary statistics
    print(f"\nPrediction Summary:")
    print(f"- Total predictions: {len(predictions)}")
    print(f"- Predicted to over-perform: {predictions['predicted_over_perform'].sum()}")
    print(f"- Predicted to under-perform: {(predictions['predicted_over_perform'] == 0).sum()}")
    print(f"- Average confidence: {predictions['over_perform_probability'].mean():.3f}")
    
    # High confidence predictions
    high_conf = predictions[predictions['over_perform_probability'] > 0.8]
    print(f"\nHigh confidence over-perform predictions (>80%):")
    if len(high_conf) > 0:
        print(high_conf[['player_name', 'team', 'week', 'over_perform_probability']].head(5).to_string(index=False))
    else:
        print("No high confidence predictions found.")
    
    print("\n" + "=" * 60)
    print("PREDICTION DEMO COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError during prediction: {e}")
        print("Please make sure you've run train_baseline.py first.")
        sys.exit(1)
