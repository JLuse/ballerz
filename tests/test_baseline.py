"""
Simple tests for the fantasy football analytics baseline model.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.data.collect_data import FantasyDataCollector
from src.features.feature_engineering import FeatureEngineer
from src.models.baseline_model import BaselineModel


def test_data_collection():
    """Test that data collection works."""
    print("Testing data collection...")
    
    collector = FantasyDataCollector()
    data = collector.collect_all_data()
    
    assert 'rb_performance' in data
    assert len(data['rb_performance']) > 0
    assert 'fantasy_points' in data['rb_performance'].columns
    assert 'projection' in data['rb_performance'].columns
    
    print("✓ Data collection test passed")


def test_feature_engineering():
    """Test that feature engineering works."""
    print("Testing feature engineering...")
    
    # Create sample data
    collector = FantasyDataCollector()
    raw_data = collector.create_sample_data()
    
    # Engineer features
    engineer = FeatureEngineer()
    engineered_data = engineer.engineer_all_features(raw_data)
    
    assert len(engineered_data.columns) > len(raw_data.columns)
    assert 'target' in engineered_data.columns
    assert 'fantasy_points_rolling_3' in engineered_data.columns
    
    print("✓ Feature engineering test passed")


def test_model_training():
    """Test that model training works."""
    print("Testing model training...")
    
    # Create sample data and engineer features
    collector = FantasyDataCollector()
    raw_data = collector.create_sample_data()
    
    engineer = FeatureEngineer()
    engineered_data = engineer.engineer_all_features(raw_data)
    
    # Train model
    model = BaselineModel()
    X, y = model.prepare_features(engineered_data)
    
    # Quick training test
    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier(n_estimators=10, random_state=42)
    rf.fit(X, y)
    
    # Make predictions
    predictions = rf.predict(X[:10])
    assert len(predictions) == 10
    
    print("✓ Model training test passed")


def run_all_tests():
    """Run all tests."""
    print("Running fantasy football analytics tests...")
    print("=" * 50)
    
    try:
        test_data_collection()
        test_feature_engineering()
        test_model_training()
        
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
